import sys
import asyncio
import json
import logging

from jsonschema import validate
from jsonschema.exceptions import ValidationError
from web3 import Web3, exceptions

from axie.schemas import payments_schema
from axie.utils import check_balance, get_nonce, load_json, ImportantLogsFilter

CREATOR_FEE_ADDRESS = "ronin:9fa1bc784c665e683597d3f29375e45786617550"
SLP_CONTRACT = "0xa8754b9fa15fc18bb59458815510e40a12cd2014"
RONIN_PROVIDER_FREE = "https://proxy.roninchain.com/free-gas-rpc"

logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('results.log', mode='w')
file_handler.setLevel(logging.INFO)
file_handler.addFilter(ImportantLogsFilter())
logger.addHandler(file_handler)


class Payment:
    def __init__(self, name, from_acc, from_private, to_acc, amount, nonce=None):
        self.w3 = Web3(Web3.HTTPProvider(RONIN_PROVIDER_FREE))
        self.name = name
        self.from_acc = from_acc.replace("ronin:", "0x")
        self.from_private = from_private
        self.to_acc = to_acc.replace("ronin:", "0x")
        self.amount = amount
        if not nonce:
            self.nonce = get_nonce(self.from_acc)
        else:
            self.nonce = max(get_nonce(self.from_acc), nonce)

    async def execute(self):
        # Prepare transaction
        with open("axie/slp_abi.json") as f:
            slb_abi = json.load(f)
        slp_contract = self.w3.eth.contract(
            address=Web3.toChecksumAddress(SLP_CONTRACT),
            abi=slb_abi
        )
        # Build transaction
        transaction = slp_contract.functions.transfer(
            Web3.toChecksumAddress(self.to_acc),
            self.amount
        ).buildTransaction({
            "chainId": 2020,
            "gas": 100000,
            "gasPrice": self.w3.toWei("0", "gwei"),
            "nonce": self.nonce
        })
        # Sign Transaction
        signed = self.w3.eth.account.sign_transaction(
            transaction,
            private_key=self.from_private
        )
        # Send raw transaction
        self.w3.eth.send_raw_transaction(signed.rawTransaction)
        # get transaction hash
        hash = self.w3.toHex(self.w3.keccak(signed.rawTransaction))
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
                logging.info(f"Waiting for transaction '{self}' to finish (Nonce:{self.nonce})...")
                # Sleep 5 seconds not to constantly send requests!
                await asyncio.sleep(5)

        if success:
            logging.info(f"Important: Transaction {self} completed! Hash: {hash} - "
                         f"Explorer: https://explorer.roninchain.com/tx/{str(hash)}")
        else:
            logging.info(f"Important: Transaction {self} failed")

    def __str__(self):
        return f"{self.name}({self.to_acc.replace('0x', 'ronin:')}) for the ammount of {self.amount} SLP"


class AxiePaymentsManager:
    def __init__(self, payments_file, secrets_file, auto=False):
        self.payments_file = load_json(payments_file)
        self.secrets_file = load_json(secrets_file)
        self.manager_acc = None
        self.scholar_accounts = None
        self.donations = None
        self.auto = auto

    def verify_inputs(self):
        logging.info("Validating file inputs...")
        validation_success = True
        # Validate payments file
        try:
            validate(self.payments_file, payments_schema)
        except ValidationError as ex:
            logging.critical("Payments file failed validation. Please review it. "
                             f"Error given: {ex.message}. "
                             f"For attribute in: {list(ex.path)}")
            validation_success = False
        if len(self.payments_file["Manager"].replace("ronin:", "0x")) != 42:
            logging.critical(f"Check your manager ronin {self.payments_file['Manager']}, it has an incorrect format")
            validation_success = False
        # check donations do not exceed 100%
        if self.payments_file.get("Donations"):
            total = sum([x["Percent"] for x in self.payments_file.get("Donations")])
            if total > 0.99:
                logging.critical("Payments file donations exeeds 100%, please review it")
                validation_success = False
            self.donations = self.payments_file["Donations"]
        # Check we have private keys for all accounts
        for acc in self.payments_file["Scholars"]:
            if acc["AccountAddress"] not in self.secrets_file:
                logging.critical(f"Account '{acc['Name']}' is not present in secret file, please add it.")
                validation_success = False
        for sf in self.secrets_file:
            if len(self.secrets_file[sf]) != 66 or self.secrets_file[sf][:2] != "0x":
                logging.critical(f"Private key for account {sf} is not valid, please review it!")
                validation_success = False
        if not validation_success:
            logging.critical("Please make sure your payments.json file looks like the one in the README.md\n"
                             "Find it here: https://github.com/FerranMarin/axie-scholar-utilities/#payments-utility")
            logging.critical("If your problem is with secrets.json, "
                             "delete it and re-generate the file starting with an empty secrets file.")
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
            fee = 0
            total_payments = 0
            acc_payments = []
            # scholar_payment
            scholar_payment = Payment(
                f"Payment to scholar of {acc['Name']}",
                acc["AccountAddress"],
                self.secrets_file[acc["AccountAddress"]],
                acc["ScholarPayoutAddress"],
                acc["ScholarPayout"]
            )
            fee += acc["ScholarPayout"]
            total_payments += acc["ScholarPayout"]
            nonce = get_nonce(acc["AccountAddress"]) + 1
            acc_payments.append(scholar_payment)
            if acc.get("TrainerPayoutAddress"):
                # trainer_payment
                acc_payments.append(Payment(
                    f"Payment to trainer of {acc['Name']}",
                    acc["AccountAddress"],
                    self.secrets_file[acc["AccountAddress"]],
                    acc["TrainerPayoutAddress"],
                    acc["TrainerPayout"],
                    nonce
                ))
                fee += acc["TrainerPayout"]
                total_payments += acc["TrainerPayout"]
                nonce += 1
            manager_payout = acc["ManagerPayout"]
            fee += manager_payout
            total_payments += acc["ManagerPayout"]
            total_dono = 0
            if self.donations:
                for dono in self.donations:
                    amount = round(manager_payout * dono["Percent"])
                    if amount > 1:
                        total_dono += amount
                        # donation payment
                        acc_payments.append(Payment(
                            f"Donation to {dono['Name']} for {acc['Name']}",
                            acc["AccountAddress"],
                            self.secrets_file[acc["AccountAddress"]],
                            dono["AccountAddress"],
                            amount,
                            nonce
                        ))
                        nonce += 1
            # Creator fee
            fee_payout = round(fee * 0.01)
            if fee_payout > 1:
                total_dono += fee_payout
                acc_payments.append(Payment(
                            f"Donation to software creator for {acc['Name']}",
                            acc["AccountAddress"],
                            self.secrets_file[acc["AccountAddress"]],
                            CREATOR_FEE_ADDRESS,
                            fee_payout,
                            nonce
                        ))
                nonce += 1
            # manager payment
            acc_payments.append(Payment(
                f"Payment to manager of {acc['Name']}",
                acc["AccountAddress"],
                self.secrets_file[acc["AccountAddress"]],
                self.manager_acc,
                manager_payout - total_dono,
                nonce
            ))
            if self.check_acc_has_enough_balance(acc["AccountAddress"],
                                                 total_payments):
                self.payout_account(acc["Name"], acc_payments)
            else:
                logging.info(f"Important: Skipping payments for account '{acc['Name']}'. "
                             "Insufficient funds!")

    def payout_account(self, acc_name, payment_list):
        logging.info(f"Payments for {acc_name}:")
        logging.info(",\n".join(str(p) for p in payment_list))
        accept = "y" if self.auto else None
        while accept not in ["y", "n", "Y", "N"]:
            accept = input("Do you want to proceed with these transactions?(y/n): ")
        if accept.lower() == "y":
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.gather(*[payment.execute() for payment in payment_list]))
            logging.info(f"Transactions completed for account: '{acc_name}'")
        else:
            logging.info(f"Transactions canceled for account: '{acc_name}'")
