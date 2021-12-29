import sys
import json
import rlp
import logging
from time import sleep
from datetime import datetime, timedelta

from jsonschema import validate
from jsonschema.exceptions import ValidationError
from trezorlib.client import get_default_client
from trezorlib.tools import parse_path
from trezorlib import ethereum
from web3 import Web3, exceptions

from axie.payments import PaymentsSummary
from axie.schemas import payments_percent_schema
from axie.utils import (
    check_balance,
    get_nonce,
    load_json,
    ImportantLogsFilter,
    SLP_CONTRACT,
    RONIN_PROVIDER_FREE,
    TIMEOUT_MINS,
    USER_AGENT
)
from trezor.trezor_utils import CustomUI


CREATOR_FEE_ADDRESS = "ronin:9fa1bc784c665e683597d3f29375e45786617550"

now = int(datetime.now().timestamp())
log_file = f'logs/results_{now}.log'
logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.addFilter(ImportantLogsFilter())
logger.addHandler(file_handler)


class TrezorPayment:

    def __init__(self, name, payment_type, client, bip_path, from_acc, to_acc, amount, summary):
        self.w3 = Web3(
            Web3.HTTPProvider(
                RONIN_PROVIDER_FREE,
                request_kwargs={"headers": {"content-type": "application/json", "user-agent": USER_AGENT}}))
        self.name = name
        self.payment_type = payment_type
        self.from_acc = from_acc.replace("ronin:", "0x")
        self.to_acc = to_acc.replace("ronin:", "0x")
        self.amount = amount
        with open("trezor/slp_abi.json", encoding='utf-8') as f:
            slb_abi = json.load(f)
        self.contract = self.w3.eth.contract(
            address=Web3.toChecksumAddress(SLP_CONTRACT),
            abi=slb_abi
        )
        self.client = client
        self.bip_path = bip_path
        self.gwei = self.w3.toWei('0', 'gwei')
        self.gas = 250000
        self.summary = summary

    def send_replacement_tx(self, nonce):
        # check nonce is still available, do nothing if nonce is not available anymore
        if nonce != get_nonce(self.from_acc):
            return
        # build replacement tx
        replace_tx = self.contract.functions.transfer(
            Web3.toChecksumAddress(self.from_acc),
            0
        ).buildTransaction({
            "chainId": 2020,
            "gas": self.gas,
            "gasPrice": self.w3.toWei("0", "gwei"),
            "nonce": nonce
        })
        data = self.w3.toBytes(hexstr=replace_tx['data'])
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
        l_sig = list(sig)
        l_sig[1] = l_sig[1].lstrip(b'\x00')
        l_sig[2] = l_sig[2].lstrip(b'\x00')
        sig = tuple(l_sig)
        replacement_tx = rlp.encode((nonce, self.gwei, self.gas, to, 0, data) + sig)
        # Send raw transaction
        self.w3.eth.send_raw_transaction(replacement_tx)
        # get transaction hash
        new_hash = self.w3.toHex(self.w3.keccak(replacement_tx))
        # Wait for transaction to finish or timeout
        start_time = datetime.now()
        while True:
            # We will wait for max 5min for this replacement tx to happen
            if datetime.now() - start_time > timedelta(minutes=TIMEOUT_MINS):
                success = False
                logging.info("Replacement transaction, timed out!")
                break
            try:
                receipt = self.w3.eth.get_transaction_receipt(new_hash)
                if receipt['status'] == 1:
                    success = True
                else:
                    success = False
                break
            except exceptions.TransactionNotFound:
                sleep(10)
                logging.info(f"Waiting for replacement tx to finish (Nonce: {nonce})")

        if success:
            logging.info(f"Successfuly replaced transaction with nonce: {nonce}")
            logging.info(f"Trying again to execute transaction {self} in 10 seconds")
            sleep(10)
            self.execute()
        else:
            logging.info(f"Important: Replacement transaction failed. Means we could not complete tx {self}")

    def execute(self):
        # Get Nonce
        nonce = get_nonce(self.from_acc)
        # Build transaction
        send_tx = self.contract.functions.transfer(
            Web3.toChecksumAddress(self.to_acc),
            self.amount
        ).buildTransaction({
            "chainId": 2020,
            "gas": self.gas,
            "gasPrice": self.gwei,
            "nonce": nonce
        })
        data = self.w3.toBytes(hexstr=send_tx['data'])
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
        l_sig = list(sig)
        l_sig[1] = l_sig[1].lstrip(b'\x00')
        l_sig[2] = l_sig[2].lstrip(b'\x00')
        sig = tuple(l_sig)
        transaction = rlp.encode((nonce, self.gwei, self.gas, to, 0, data) + sig)
        # Send raw transaction
        self.w3.eth.send_raw_transaction(transaction)
        hash = self.w3.toHex(self.w3.keccak(transaction))
        # Wait for transaction to finish or timeout
        start_time = datetime.now()
        while True:
            # We will wait for max 10minutes for this tx to respond, if it does not, we will re-try
            if datetime.now() - start_time > timedelta(minutes=TIMEOUT_MINS):
                success = False
                logging.info(f"Transaction {self}, timed out!")
                break
            try:
                recepit = self.w3.eth.get_transaction_receipt(hash)
                if recepit["status"] == 1:
                    success = True
                else:
                    success = False
                break
            except exceptions.TransactionNotFound:
                # Sleep 10s while waiting
                sleep(10)
                logging.info(f"Waiting for transaction '{self}' to finish (Nonce:{nonce})...")

        if success:
            logging.info(f"Important: Transaction {self} completed! Hash: {hash} - "
                         f"Explorer: https://explorer.roninchain.com/tx/{str(hash)}")
            self.summary.increase_payout(
                amount=self.amount,
                address=self.to_acc.replace('0x', 'ronin:'),
                payout_type=self.payment_type)
        else:
            logging.info(f"Important: Transaction {self} failed. Trying to replace it with a 0 value tx and re-try.")
            self.send_replacement_tx(nonce)

    def __str__(self):
        return f"{self.name}({self.to_acc.replace('0x', 'ronin:')}) for the amount of {self.amount} SLP"


class TrezorAxiePaymentsManager:
    def __init__(self, payments_file, trezor_config, auto=False):
        self.payments_file = load_json(payments_file)
        self.trezor_config = load_json(trezor_config)
        self.manager_acc = None
        self.scholar_accounts = None
        self.donations = None
        self.auto = auto
        self.summary = PaymentsSummary()

    def verify_inputs(self):
        logging.info("Validating file inputs...")
        validation_success = True
        # Validate payments file
        try:
            validate(self.payments_file, payments_percent_schema)
        except ValidationError as ex:
            logging.critical("If you were tyring to pay using percents:\n"
                             f"Error given: {ex.message}\n"
                             f"For attribute in: {list(ex.path)}\n")
        if len(self.payments_file["Manager"].replace("ronin:", "0x")) != 42:
            logging.critical(f"Check your manager ronin {self.payments_file['Manager']}, it has an incorrect format")
            validation_success = False
        # check donations do not exceed 100%
        if self.payments_file.get("Donations"):
            total = sum([x["Percent"] for x in self.payments_file.get("Donations")])
            if total > 99:
                logging.critical("Payments file donations exeeds 100%, please review it")
                validation_success = False
            if any(len(dono['AccountAddress'].replace("ronin:", "0x")) != 42 for dono in self.payments_file["Donations"]): # noqa
                logging.critical("Please review the ronins in your donations. One or more are wrong!")
                validation_success = False
            self.donations = self.payments_file["Donations"]

        # Check we have trezor configs for all accounts
        for acc in self.payments_file["Scholars"]:
            if acc["AccountAddress"].lower() not in self.trezor_config:
                logging.critical(f"Account '{acc['Name']}' is not present in trezor config file, please re-run setup.")
                validation_success = False
        if not validation_success:
            logging.critical("Please make sure your payments.json file looks like the one in the README.md\n"
                             "Find it here: https://ferranmarin.github.io/axie-scholar-utilities/")
            logging.critical("If your problem is with trezor_config.json, delete it and re-run trezor setup command.")
            sys.exit()
        self.manager_acc = self.payments_file["Manager"]
        self.scholar_accounts = self.payments_file["Scholars"]
        logging.info("Files correctly validated!")

    def check_acc_has_enough_balance(self, account, balance):
        account_balance = check_balance(account)
        if account_balance < balance:
            logging.critical(f"Balance in account {account} is "
                             "inssuficient to cover all planned payments!")
            return False
        elif account_balance - balance > 0:
            logging.info(f'These payments will leave {account_balance - balance} SLP in your wallet.'
                         'Cancel payments and adjust payments if you want to leave 0 SLP in it.')
        return True

    def prepare_payout(self):
        for acc in self.scholar_accounts:
            client = get_default_client(
                ui=CustomUI(passphrase=self.trezor_config[acc['AccountAddress'].lower()]['passphrase']))
            bip_path = parse_path(self.trezor_config[acc['AccountAddress'].lower()]['bip_path'])
            acc_balance = check_balance(acc['AccountAddress'].lower())
            total_payments = 0
            acc_payments = []
            # Scholar Payment
            scholar_amount = acc_balance * (acc["ScholarPercent"]/100)
            scholar_amount += acc.get("ScholarPayout", 0)
            scholar_amount = round(scholar_amount)
            acc_payments.append(TrezorPayment(
                f"Payment to scholar of {acc['Name']}",
                "scholar",
                client,
                bip_path,
                acc["AccountAddress"].lower(),
                acc["ScholarPayoutAddress"].lower(),
                scholar_amount,
                self.summary
            ))
            total_payments += scholar_amount
            if acc.get("TrainerPayoutAddress"):
                # Trainer Payment
                trainer_amount = acc_balance * (acc["TrainerPercent"]/100)
                trainer_amount += acc.get("TrainerPayout", 0)
                trainer_amount = round(trainer_amount)
                if trainer_amount > 0:
                    acc_payments.append(TrezorPayment(
                        f"Payment to trainer of {acc['Name']}",
                        "trainer",
                        client,
                        bip_path,
                        acc["AccountAddress"].lower(),
                        acc["TrainerPayoutAddress"].lower(),
                        trainer_amount,
                        self.summary
                    ))
                    total_payments += trainer_amount
            manager_payout = acc_balance - total_payments
            if self.donations:
                # Extra Donations
                for dono in self.donations:
                    dono_amount = round(manager_payout * (dono["Percent"]/100))
                    if dono_amount > 1:
                        acc_payments.append(TrezorPayment(
                                f"Donation to {dono['Name']} for {acc['Name']}",
                                "donation",
                                client,
                                bip_path,
                                acc["AccountAddress"].lower(),
                                dono["AccountAddress"].lower(),
                                dono_amount,
                                self.summary
                            ))
                        manager_payout -= dono_amount
                        total_payments += dono_amount
            # Fee Payments
            fee_amount = round(acc_balance * 0.01)
            if fee_amount > 0:
                acc_payments.append(TrezorPayment(
                            f"Donation to software creator for {acc['Name']}",
                            "donation",
                            client,
                            bip_path,
                            acc["AccountAddress"].lower(),
                            CREATOR_FEE_ADDRESS,
                            fee_amount,
                            self.summary
                        ))
                manager_payout -= fee_amount
                total_payments += fee_amount
            # Manager Payment
            if manager_payout > 0:
                acc_payments.append(TrezorPayment(
                    f"Payment to manager of {acc['Name']}",
                    "manager",
                    client,
                    bip_path,
                    acc["AccountAddress"].lower(),
                    self.manager_acc.lower(),
                    manager_payout,
                    self.summary
                ))
                total_payments += manager_payout
            else:
                logging.info("Important: Skipping manager payout as it resulted in 0 SLP.")
            if self.check_acc_has_enough_balance(acc['AccountAddress'], total_payments) and acc_balance > 0:
                self.payout_account(acc['Name'], acc_payments)
            else:
                logging.info(f"Important: Skipping payments for account '{acc['Name']}'. "
                             "Insufficient funds!")
        logging.info(f"Important: Transactions Summary:\n {self.summary}")

    def payout_account(self, acc_name, payment_list):
        logging.info(f"Payments for {acc_name}:")
        logging.info(",\n".join(str(p) for p in payment_list))
        accept = "y" if self.auto else None
        while accept not in ["y", "n", "Y", "N"]:
            accept = input("Do you want to proceed with these transactions?(y/n): ")
        if accept.lower() == "y":
            for p in payment_list:
                p.execute()
            logging.info(f"Transactions completed for account: '{acc_name}'")
        else:
            logging.info(f"Transactions canceled for account: '{acc_name}'")
