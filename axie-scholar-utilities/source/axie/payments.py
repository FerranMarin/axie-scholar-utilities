import os
import sys
import json
import logging
from time import sleep

from jsonschema import validate
from jsonschema.exceptions import ValidationError
from web3 import Web3, exceptions

from axie.schemas import payments_schema

CREATOR_FEE_ADDRESS = "ronin:cac6cb4a85ba1925f96abc9a302b4a34dbb8c6b0"
SLP_CONTRACT = "0xa8754b9fa15fc18bb59458815510e40a12cd2014"
RONIN_PROVIDER = "https://proxy.roninchain.com/free-gas-rpc"


class Payment(object):
    def __init__(self, name, from_acc, from_private, to_acc, amount, nonce=None):
        self.w3 = Web3(Web3.HTTPProvider(RONIN_PROVIDER))
        self.name = name
        self.from_acc = from_acc.replace("ronin:", "0x")
        self.from_private = from_private
        self.to_acc = to_acc.replace("ronin:", "0x")
        self.amount = amount
        if not nonce:
            self.nonce = self.get_nonce()
        else:
            self.nonce = max(self.get_nonce(), nonce)

    def get_nonce(self):
        return self.w3.eth.get_transaction_count(Web3.toChecksumAddress(self.from_acc))

    def execute(self):
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
        # send raw transaction
        self.w3.eth.send_raw_transaction(signed.rawTransaction)
        # get transaction hash
        hash = self.w3.toHex(self.w3.keccak(signed.rawTransaction))
        # wait for transaction to finish
        while True:
            try:
                recepit = self.w3.eth.get_transaction_receipt(hash)
                if recepit["status"] == 1:
                    success = True
                else:
                    success = False
                break
            except exceptions.TransactionNotFound:
                logging.info("Waiting for transaction to finish...")
                # Sleep 5 seconds not to constantly send requests!
                sleep(5)

        return hash, success

    def __str__(self):
        return f"{self.name}({self.to_acc.replace('0x', 'ronin:')}) for the ammount of {self.amount} SLP"


class AxiePaymentsManager:
    def __init__(self, payments_file, secrets_file, auto=False):
        self.payments_file = self.load_json(payments_file)
        self.secrets_file = self.load_json(secrets_file)
        self.manager_acc = None
        self.scholar_accounts = None
        self.donations = None
        self.auto = auto

    @staticmethod
    def load_json(json_file):
        # This is a safe guard, it should never raise as we check this in the CLI bit.
        if not os.path.isfile(json_file):
            raise Exception(f"File path {json_file} does not exist. "
                            f"Please provide a correct one")
        try:
            with open(json_file) as f:
                data = json.load(f)
        except json.decoder.JSONDecodeError:
            raise Exception(f"File in path {json_file} is not a correctly encoded JSON.")
        return data

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
            sys.exit()
        self.manager_acc = self.payments_file["Manager"]
        self.scholar_accounts = self.payments_file["Scholars"]
        logging.info("Files correctly validated!")
    
    def prepare_payout(self):
        fee = 0
        for acc in self.scholar_accounts:
            acc_payments = []
            # scholar_payment
            scholar_payment = Payment(
                "Payment to scholar",
                acc["AccountAddress"],
                self.secrets_file[acc["AccountAddress"]],
                acc["ScholarPayoutAddress"],
                acc["ScholarPayout"]
            )
            fee += acc["ScholarPayout"]
            nonce = scholar_payment.get_nonce() + 1
            acc_payments.append(scholar_payment)
            if acc.get("TrainerPayoutAddress"):
                # trainer_payment
                acc_payments.append(Payment(
                    "Payment to trainer",
                    acc["AccountAddress"],
                    self.secrets_file[acc["AccountAddress"]],
                    acc["TrainerPayoutAddress"],
                    acc["TrainerPayout"],
                    nonce
                ))
                fee += acc["TrainerPayout"]
            nonce += 1
            manager_payout = acc["ManagerPayout"]
            fee += manager_payout
            total_dono = 0
            if self.donations:
                for dono in self.donations:
                    amount = round(manager_payout * dono["Percent"])
                    if amount > 1:
                        total_dono += amount
                        # donation payment
                        acc_payments.append(Payment(
                            f"Donation to {dono['Name']}",
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
                            "Donation to software creator",
                            acc["AccountAddress"],
                            self.secrets_file[acc["AccountAddress"]],
                            CREATOR_FEE_ADDRESS,
                            fee_payout,
                            nonce
                        ))
                nonce += 1
            # manager payment
            acc_payments.append(Payment(
                "Payment to manager",
                acc["AccountAddress"],
                self.secrets_file[acc["AccountAddress"]],
                self.manager_acc,
                manager_payout - total_dono,
                nonce
            ))
            self.payout_account(acc["Name"], acc_payments)

    def payout_account(self, acc_name, payment_list):
        logging.info(f"Payments for {acc_name}:")
        logging.info(",\n".join(str(p) for p in payment_list))
        accept = "y" if self.auto else None
        while accept not in ["y", "n", "Y", "N"]:
            accept = input("Do you want to proceed with these transactions?(y/n): ")
        if accept.lower() == "y":
            for payment in payment_list:
                hash, success = payment.execute()
                if success:
                    logging.info(f"{payment} Transaction Sent!")
                    logging.info(f"Transaction hash: {hash} - Explorer: https://explorer.roninchain.com/tx/{str(hash)}")
                else:
                    logging.info(f"Transaction reverted by EVM (Ethereum Virtual machine)")
            logging.info(f"Transactions completed for account: '{acc_name}'")
        else:
            logging.info(f"Transactions canceled for account: '{acc_name}'")
