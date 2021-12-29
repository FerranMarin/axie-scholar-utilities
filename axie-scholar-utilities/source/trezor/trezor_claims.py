import sys
import asyncio
import json
import rlp
import logging
from datetime import datetime

from requests.exceptions import RetryError
from web3 import Web3, exceptions
import requests
from trezorlib.client import get_default_client
from trezorlib import ethereum

from axie.utils import (
    check_balance,
    get_nonce,
    load_json,
    ImportantLogsFilter,
    SLP_CONTRACT,
    RONIN_PROVIDER_FREE,
    USER_AGENT
)
from trezor.trezor_utils import TrezorAxieGraphQL, CustomUI


now = int(datetime.now().timestamp())
log_file = f'logs/results_{now}.log'
logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file, mode='w')
file_handler.setLevel(logging.INFO)
file_handler.addFilter(ImportantLogsFilter())
logger.addHandler(file_handler)


class TrezorClaim(TrezorAxieGraphQL):
    def __init__(self, acc_name, **kwargs):
        super().__init__(**kwargs)
        self.w3 = Web3(
            Web3.HTTPProvider(
                RONIN_PROVIDER_FREE,
                request_kwargs={"headers": {"content-type": "application/json", "user-agent": USER_AGENT}}))
        with open("axie/slp_abi.json", encoding='utf-8') as f:
            slp_abi = json.load(f)
        self.slp_contract = self.w3.eth.contract(
            address=Web3.toChecksumAddress(SLP_CONTRACT),
            abi=slp_abi
        )
        self.acc_name = acc_name
        self.request = requests.Session()
        self.gwei = self.w3.toWei('0', 'gwei')
        self.gas = 492874

    def has_unclaimed_slp(self):
        url = f"https://game-api.skymavis.com/game-api/clients/{self.account}/items/1"
        try:
            response = self.request.get(url, headers={"User-Agent": self.user_agent})
        except RetryError:
            logging.critical(f"Failed to check if there is unclaimed SLP for acc {self.acc_name} "
                             f"({self.account.replace('0x','ronin:')})")
            return None
        if 200 <= response.status_code <= 299:
            in_game_total = int(response.json()['total'])
            wallet_total = check_balance(self.account)
            if in_game_total > wallet_total:
                return in_game_total - wallet_total
        return None

    async def execute(self):
        unclaimed = self.has_unclaimed_slp()
        if not unclaimed:
            logging.info(f"Important: Account {self.acc_name} ({self.account.replace('0x', 'ronin:')}) "
                         "has no claimable SLP")
            return
        logging.info(f"Account {self.acc_name} ({self.account.replace('0x', 'ronin:')}) has "
                     f"{unclaimed} unclaimed SLP")
        jwt = self.get_jwt()
        if not jwt:
            logging.critical("Important: Skipping claiming, we could not get the JWT for account "
                             f"{self.account.replace('0x', 'ronin:')}")
            return
        headers = {
            "User-Agent": self.user_agent,
            "authorization": f"Bearer {jwt}"
        }
        url = f"https://game-api.skymavis.com/game-api/clients/{self.account}/items/1/claim"
        try:
            response = self.request.post(url, headers=headers, json="")
        except RetryError as e:
            logging.critical(f"Error! Executing SLP claim API call for account {self.acc_name}"
                             f"({self.account.replace('0x', 'ronin:')}). Error {e}")
            return
        if 200 <= response.status_code <= 299:
            signature = response.json()["blockchain_related"].get("signature")
            if not signature or not signature["signature"]:
                logging.critical(f"Account {self.acc_name} ({self.account.replace('0x', 'ronin:')}) had no signature "
                                 "in blockchain_related")
                return
        else:
            logging.info(f"Important: Claim for account {self.acc_name} ({self.account.replace('0x', 'ronin:')}) "
                         "had to be skipped")
            return
        nonce = get_nonce(self.account)
        # Build claim
        claim = self.slp_contract.functions.checkpoint(
            Web3.toChecksumAddress(self.account),
            signature['amount'],
            signature['timestamp'],
            signature['signature']
        ).buildTransaction({'gas': self.gas, 'gasPrice': 0, 'nonce': nonce})
        data = self.w3.toBytes(hexstr=claim['data'])
        to = self.w3.toBytes(hexstr=SLP_CONTRACT)
        sig = ethereum.sign_tx(
            self.client,
            n=self.bip_path,
            nonce=nonce,
            gas_price=self.gwei,
            gas_limit=self.gas,
            to=SLP_CONTRACT,
            value=0,
            data=data,
            chain_id=2020
        )
        logging.info(f'Important: Debugging information {sig}')
        if sig[1][:4] == b'0x00':
            sig[1] = b'0x' + sig[1][4:]
        if sig[2][:4] == b'0x00':
            sig[2] = b'0x' + sig[2][4:]
        transaction = rlp.encode((nonce, self.gwei, self.gas, to, 0, data) + sig)
        # Send raw transaction
        self.w3.eth.send_raw_transaction(transaction)
        hash = self.w3.toHex(self.w3.keccak(transaction))
        # Wait for transaction to finish
        while True:
            try:
                recepit = self.w3.eth.get_transaction_receipt(hash)
                if recepit["status"] == 1:
                    success = True
                else:
                    success = False
                break
            except exceptions.TransactionNotFound:
                logging.debug(f"Waiting for claim for {self.acc_name} ({self.account.replace('0x', 'ronin:')}) to "
                              f"finish (Nonce:{nonce}) (Hash: {hash})...")
                # Sleep 5 seconds not to constantly send requests!
                await asyncio.sleep(5)
        if success:
            logging.info(f"Important: SLP Claimed! New balance for account {self.acc_name} "
                         f"({self.account.replace('0x', 'ronin:')}) is: {check_balance(self.account)}")
            return
        else:
            logging.info(f"Important: Claim for account {self.acc_name} ({self.account.replace('0x', 'ronin:')}) "
                         "failed")
            return


class TrezorAxieClaimsManager:
    def __init__(self, payments_file, trezor_config):
        self.trezor_config, self.acc_names = self.load_trezor_config_and_acc_name(trezor_config, payments_file)

    def load_trezor_config_and_acc_name(self, trezor_config, payments_file):
        config = load_json(trezor_config)
        payments = load_json(payments_file)
        refined_config = {}
        acc_names = {}
        for scholar in payments['Scholars']:
            key = scholar['AccountAddress'].lower()
            refined_config[key] = config[key]
            acc_names[key] = scholar['Name']
        return refined_config, acc_names

    def verify_inputs(self):
        validation_success = True
        if not self.trezor_config:
            logging.warning("No configuration found for trezor")
            validation_success = False
        for acc in self.trezor_config:
            if not acc.startswith("ronin:"):
                logging.critical(f"Public address {acc} needs to start with ronin:")
                validation_success = False
        if not validation_success:
            sys.exit()
        logging.info("Files correctly validated")

    def prepare_claims(self):
        claims_list = [
            TrezorClaim(
                account=acc,
                client=get_default_client(ui=CustomUI(passphrase=self.trezor_config[acc]['passphrase'])),
                bip_path=self.trezor_config[acc]['bip_path'],
                acc_name=self.acc_names[acc]) for acc in self.trezor_config]
        logging.info("Claiming starting...")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*[claim.execute() for claim in claims_list]))
        logging.info("Claiming completed!")
