import sys
import logging
import json
import rlp
from datetime import datetime, timedelta
from time import sleep

from jsonschema import validate
from jsonschema.exceptions import ValidationError
from web3 import Web3, exceptions
from trezorlib.client import get_default_client
from trezorlib.tools import parse_path
from trezorlib import ethereum

from axie.schemas import transfers_schema
from axie.axies import Axies
from axie.utils import (
    get_nonce,
    load_json,
    ImportantLogsFilter,
    RONIN_PROVIDER_FREE,
    AXIE_CONTRACT,
    TIMEOUT_MINS,
    USER_AGENT
)
from trezor.trezor_utils import CustomUI


now = int(datetime.now().timestamp())
log_file = f'logs/results_{now}.log'
logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file, mode='w')
file_handler.setLevel(logging.INFO)
file_handler.addFilter(ImportantLogsFilter())
logger.addHandler(file_handler)


class TrezorTransfer:
    def __init__(self, from_acc, client, bip_path, to_acc, axie_id):
        self.w3 = Web3(
            Web3.HTTPProvider(
                RONIN_PROVIDER_FREE,
                request_kwargs={"headers": {"content-type": "application/json", "user-agent": USER_AGENT}}))
        self.from_acc = from_acc.replace("ronin:", "0x")
        self.to_acc = to_acc.replace("ronin:", "0x")
        self.axie_id = axie_id
        self.client = client
        self.bip_path = parse_path(bip_path)
        self.gwei = self.w3.toWei('0', 'gwei')
        self.gas = 250000

    def execute(self):
        # Load ABI
        with open('trezor/axie_abi.json', encoding='utf-8') as f:
            axie_abi = json.load(f)
        axie_contract = self.w3.eth.contract(
            address=Web3.toChecksumAddress(AXIE_CONTRACT),
            abi=axie_abi
        )
        # Get Nonce
        nonce = get_nonce(self.from_acc)
        # Build transaction
        transfer_tx = axie_contract.functions.safeTransferFrom(
            Web3.toChecksumAddress(self.from_acc),
            Web3.toChecksumAddress(self.to_acc),
            self.axie_id
        ).buildTransaction({
            "chainId": 2020,
            "gas": self.gas,
            "gasPrice": self.w3.toWei("0", "gwei"),
            "value": 0,
            "nonce": nonce
        })
        data = self.w3.toBytes(hexstr=transfer_tx['data'])
        to = self.w3.toBytes(hexstr=AXIE_CONTRACT)
        sig = ethereum.sign_tx(
            self.client,
            n=self.bip_path,
            nonce=nonce,
            gas_price=self.gwei,
            gas_limit=self.gas,
            to=AXIE_CONTRACT,
            value=0,
            data=data,
            chain_id=2020
        )
        logging.info(f'Important: Debugging information {sig}')
        l_sig = list(sig)
        l_sig[1] = l_sig[1].lstrip(b'\x00')
        l_sig[2] = l_sig[2].lstrip(b'\x00')
        sig = tuple(l_sig)
        transaction = rlp.encode((nonce, self.gwei, self.gas, to, 0, data) + sig)
        # Send raw transaction
        self.w3.eth.send_raw_transaction(transaction)
        # Get transaction hash
        hash = self.w3.toHex(self.w3.keccak(transaction))
        # Wait for transaction to finish or timeout
        start_time = datetime.now()
        while True:
            # We will wait for max 10min for this trasnfer to happen
            if datetime.now() - start_time > timedelta(minutes=TIMEOUT_MINS):
                success = False
                logging.info(f"Important: Transfer {self}, timed out!")
                break
            try:
                recepit = self.w3.eth.get_transaction_receipt(hash)
                if recepit["status"] == 1:
                    success = True
                else:
                    success = False
                break
            except exceptions.TransactionNotFound:
                logging.info(f"Waiting for transfer '{self}' to finish (Nonce:{nonce})...")
                # Sleep 10 seconds not to constantly send requests!
                sleep(10)
        if success:
            logging.info(f"Important: {self} completed! Hash: {hash} - "
                         f"Explorer: https://explorer.roninchain.com/tx/{str(hash)}")
        else:
            logging.info(f"Important: {self} failed")

    def __str__(self):
        return (f"Axie Transfer of axie ({self.axie_id}) from account ({self.from_acc.replace('0x', 'ronin:')}) "
                f"to account ({self.to_acc.replace('0x', 'ronin:')})")


class TrezorAxieTransferManager:
    def __init__(self, transfers_file, trezor_config, secure=None):
        self.transfers_file = load_json(transfers_file)
        self.trezor_config = load_json(trezor_config)
        self.secure = secure

    def verify_inputs(self):
        logging.info("Validating file inputs...")
        validation_success = True
        # Validate transfers file
        try:
            validate(self.transfers_file, transfers_schema)
        except ValidationError as ex:
            logging.critical("Transfers file failed validation. Please review it. "
                             f"Error given: {ex.message}. "
                             f"For attribute in: {list(ex.path)}")
            validation_success = False
        # Check we have private keys for all accounts
        for acc in self.transfers_file:
            if acc["AccountAddress"].lower() not in self.trezor_config:
                logging.critical(f"Account '{acc['AccountAddress']}' is not present in trezor config file, "
                                 "please re-run trezor setup command.")
                validation_success = False
        if not validation_success:
            logging.critical("Please make sure your transfers.json file looks like the one in the README.md\n"
                             "Find it here: https://ferranmarin.github.io/axie-scholar-utilities/")
            sys.exit()
        logging.info("Files correctly validated!")

    def prepare_transfers(self):
        transfers = []
        logging.info("Preparing transfers")
        for acc in self.transfers_file:
            axies_in_acc = Axies(acc['AccountAddress'].lower()).get_axies()
            for axie in acc['Transfers']:
                if not self.secure or (self.secure and axie['ReceiverAddress'].lower() in self.trezor_config):
                    # Check axie in account
                    if axie['AxieId'] in axies_in_acc:
                        t = TrezorTransfer(
                            to_acc=axie['ReceiverAddress'].lower(),
                            client=get_default_client(
                                ui=CustomUI(
                                    passphrase=self.trezor_config[acc['AccountAddress'].lower()]['passphrase'])),
                            bip_path=self.trezor_config[acc['AccountAddress'].lower()]['bip_path'],
                            from_acc=acc['AccountAddress'].lower(),
                            axie_id=axie['AxieId']
                        )
                        transfers.append(t)
                        logging.info(f"Added transaction to the list: {t}")
                    else:
                        logging.info(f"Axie ({axie['AxieId']}) not in account ({acc['AccountAddress']}), skipping.")
                else:
                    logging.info(f"Receiver address {axie['ReceiverAddress']} not in secrets.json, skipping transfer.")
        self.execute_transfers(transfers)

    def execute_transfers(self, transfers):
        logging.info("Starting to transfer axies")
        for t in transfers:
            t.execute()
        logging.info("Axie transfers finished")
