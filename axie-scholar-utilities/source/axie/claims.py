import os
import sys
import asyncio
import json
import logging
from datetime import datetime

from fake_useragent import UserAgent
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from eth_account.messages import encode_defunct
from web3 import Web3, exceptions
import requests

from .payments import AxiePaymentsManager
from .schemas import payments_schema
from .utils import check_balance, get_nonce

SLP_CONTRACT = "0xa8754b9fa15fc18bb59458815510e40a12cd2014"

RONIN_PROVIDER = "https://api.roninchain.com/rpc"


class Claim:
    def __init__(self, account, private_key):
        self.w3 = Web3(Web3.HTTPProvider(RONIN_PROVIDER))
        with open("axie/min_abi.json") as f:
            min_abi = json.load(f)
        self.slp_contract = self.w3.eth.contract(
            address=Web3.toChecksumAddress(SLP_CONTRACT),
            abi=min_abi
        )
        self.account = account.replace("ronin:", "0x")
        self.private_key = private_key
        self.initial_balance = check_balance()
        self.final_balance = None
        self.unclaimed_slp = self.has_unclaimed_slp()

    async def execute(self):
        if not self.unclaimed_slp:
            logging.info(f"Account {self.account.replace('0x', 'ronin:')} has no claimable SLP")
            return
        logging.info(f"Account {self.account.replace('0x', 'ronin:')} has "
                     f"{self.unclaimed_slp} unclaimed SLP")
        jwt = self.get_jwt()
        headers = {
            "User-Agent": UserAgent().random,
            "authorisation": f"Bearer {jwt}"
        }
        url = f"https://game-api.skymavis.com/game-api/clients/{self.account}/items/1/claim"
        response = requests.post(url, headers=headers)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            return "Error! it was not 200!"
        signature = response.json()["blockchain_related"]["signature"]
        nonce = get_nonce(self.account)
        claim = self.slp_contract.functions.checkpoint(
            self.account,
            signature['amount'],
            signature['timestamp'],
            signature['signature'].replace("0x", "")
        ).buildTransaction({'gas': 1000000, 'gasPrice': 0, 'nonce': nonce})
        signed_claim = self.w3.eth.account.sign_transaction(
            claim,
            private_key=bytearray.fromhex(self.private_key.replace("0x", ""))
        )
        self.w3.eth.send_raw_transaction(signed_claim)
        while True:
            try:
                recepit = self.w3.eth.get_transaction_receipt(hash)
                if recepit["status"] == 1:
                    success = True
                else:
                    success = False
                break
            except exceptions.TransactionNotFound:
                logging.info(f"Waiting for claim for '{self.account.replace('0x', 'ronin:')}' to finish (Nonce:{nonce})...")
                # Sleep 5 seconds not to constantly send requests!
                await asyncio.sleep(5)
        
        if success:
            logging.info(f"Claimed SLP for account {self.account.replace('0x', 'ronin:')}")
            logging.info(f"New balance  for account {self.account.replace('0x', 'ronin:')} is: "
                         f"{check_balance(self.account)}")
        else:
            logging.info(f"Claim for account {self.account.replace('0x', 'ronin:')} failed")

    def has_unclaimed_slp(self):
        url = f"https://game-api.skymavis.com/game-api/clients/{self.account}/items/1"
        response = requests.get(url, headers={"User-Agent": UserAgent().random})
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            logging.criticaal("Failed to check if there is unclaimed SLP")
            return None
        unclaimed_slp = response.json()['total']
        last_claim = datetime.utcfromtimestamp(int(response.json())["last_claimed_item_at"])
        if datetime.utcnow() + datetime.timedelta(days=-14) < last_claim and unclaimed_slp > 0:
            return unclaimed_slp
        return None

    @staticmethod
    def create_random_msg():
        payload = {
            "operationName": "CreateRandomMessage",
            "variables": {},
            "query": "mutation CreateRandomMessage{createRandomMessage}"
        }
        url = "https://axieinfinity.com/graphql-server-v2/graphql"
        response = requests.post(url, headers={"User-Agent": UserAgent().random}, json=payload)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return f"Error! it was not 200! {e}"
        return response.json()['data']['createRandomMessage']

    def get_jwt(self):
        msg = self.create_random_msg()
        signed_msg = Web3().eth.account.sign_message(encode_defunct(text=msg),
                                                     private_key=self.private_key)
        hex_msg = signed_msg['signature'].hex()
        payload = {
            "operationName": "CreateAccessTokenWithSignature",
            "variables": {
                "input": {
                    "mainnet": "ronin",
                    "owner": f"{Web3.toChecksumAddress(self.account)}",
                    "message": f"{msg}",
                    "signature": f"{hex_msg}"
                }
            },
            "query": "mutation CreateAccessTokenWithSignature($input: SignatureInput!)"
            "{createAccessTokenWithSignature(input: $input) "
            "{newAccount result accessToken __typename}}"
        }
        url = "https://axieinfinity.com/graphql-server-v2/graphql"
        response = requests.post(url, headers={"User-Agent": UserAgent().chrome}, json=payload)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return f"Error! it was not 200!  {e}"
        return response.json()['data']['createAccessTokenWithSignature']['accessToken']


class AxieClaimsManager:
    def __init__(self, secrets_file):
        self.secrets_file = AxiePaymentsManager.load_json(secrets_file)

    def verify_input(self):
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
        claims = [Claim(acc, acc[acc]).execute() for acc in self.secrets_file]
        loop = asyncio.get_event_loop()
        logging.info("Caliming starting...")
        loop.run_until_complete(asyncio.gather(*claims))
        logging.info("Caliming completed!")
