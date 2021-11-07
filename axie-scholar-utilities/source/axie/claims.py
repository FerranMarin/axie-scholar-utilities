import sys
import asyncio
import json
import logging
from datetime import datetime


from requests.exceptions import RetryError
from web3 import Web3, exceptions
import requests

from axie.utils import (
    check_balance,
    get_nonce,
    load_json,
    ImportantLogsFilter,
    SLP_CONTRACT,
    RONIN_PROVIDER_FREE,
    AxieGraphQL
)


now = int(datetime.now().timestamp())
log_file = f'logs/claim_results_{now}.log'
logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file, mode='w')
file_handler.setLevel(logging.INFO)
file_handler.addFilter(ImportantLogsFilter())
logger.addHandler(file_handler)


class Claim(AxieGraphQL):
    def __init__(self, acc_name, **kwargs):
        super(Claim, self).__init__(**kwargs)
        self.w3 = Web3(Web3.HTTPProvider(RONIN_PROVIDER_FREE))
        with open("axie/slp_abi.json", encoding='utf-8') as f:
            slp_abi = json.load(f)
        self.slp_contract = self.w3.eth.contract(
            address=Web3.toChecksumAddress(SLP_CONTRACT),
            abi=slp_abi
        )
        self.acc_name = acc_name
        self.request = requests.Session()

    def has_unclaimed_slp(self):
        url = f"https://game-api.skymavis.com/game-api/clients/{self.account}/items/1"
        try:
            response = self.request.get(url, headers={"User-Agent": self.user_agent})
        except RetryError:
            logging.critical(f"Failed to check if there is unclaimed SLP for acc {self.acc_name} "
                             f"({self.account.replace('0x','ronin:')})")
            return None
        if 200 <= response.status_code <= 299:
            return int(response.json()['total'])
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
            logging.critical(f"Important: Skipping claiming, we could not get the JWT for account {self.account.replace('0x', 'ronin:')}")
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
        ).buildTransaction({'gas': 1000000, 'gasPrice': 0, 'nonce': nonce})
        # Sign claim
        signed_claim = self.w3.eth.account.sign_transaction(
            claim,
            private_key=self.private_key
        )
        # Send raw transaction
        self.w3.eth.send_raw_transaction(signed_claim.rawTransaction)
        # Get transaction hash
        hash = self.w3.toHex(self.w3.keccak(signed_claim.rawTransaction))
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
        else:
            logging.info(f"Important: Claim for account {self.acc_name} ({self.account.replace('0x', 'ronin:')}) "
                         "failed")


class AxieClaimsManager:
    def __init__(self, payments_file, secrets_file):
        self.secrets_file, self.acc_names = self.load_secrets_and_acc_name(secrets_file, payments_file)

    def load_secrets_and_acc_name(self, secrets_file, payments_file):
        secrets = load_json(secrets_file)
        payments = load_json(payments_file)
        refined_secrets = {}
        acc_names = {}
        for scholar in payments['Scholars']:
            key = scholar['AccountAddress']
            refined_secrets[key] = secrets[key]
            acc_names[key] = scholar['Name']
        return refined_secrets, acc_names

    def verify_inputs(self):
        validation_success = True
        # Check secrets file is not empty
        if not self.secrets_file:
            logging.warning("No secrets contained in secrets file")
            validation_success = False
        # Check keys and secrets have proper format
        for acc in self.secrets_file:
            if not acc.startswith("ronin:"):
                logging.critical(f"Public address {acc} needs to start with ronin:")
                validation_success = False
            if len(self.secrets_file[acc]) != 66 or self.secrets_file[acc][:2] != "0x":
                logging.critical(f"Private key for account {acc} is not valid, please review it!")
                validation_success = False
        if not validation_success:
            sys.exit()
        logging.info("Secret file correctly validated")

    def prepare_claims(self):
        claims_list = [
            Claim(
                account=acc,
                private_key=self.secrets_file[acc],
                acc_name=self.acc_names[acc]) for acc in self.secrets_file]
        logging.info("Claiming starting...")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*[claim.execute() for claim in claims_list]))
        logging.info("Claiming completed!")
