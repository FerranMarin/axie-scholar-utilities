import sys
import asyncio
import json
import logging
from datetime import datetime, timedelta

from fake_useragent import UserAgent
from eth_account.messages import encode_defunct
from web3 import Web3, exceptions
import requests

from axie.utils import check_balance, get_nonce, load_json

SLP_CONTRACT = "0xa8754b9fa15fc18bb59458815510e40a12cd2014"
RONIN_PROVIDER = "https://api.roninchain.com/rpc"


class Claim:
    def __init__(self, account, private_key):
        self.w3 = Web3(Web3.HTTPProvider(RONIN_PROVIDER))
        with open("axie/slp_abi.json") as f:
            slp_abi = json.load(f)
        self.slp_contract = self.w3.eth.contract(
            address=Web3.toChecksumAddress(SLP_CONTRACT),
            abi=slp_abi
        )
        self.account = account.replace("ronin:", "0x")
        self.private_key = private_key
        self.user_agent = UserAgent().chrome

    def has_unclaimed_slp(self):
        url = f"https://game-api.skymavis.com/game-api/clients/{self.account}/items/1"
        response = requests.get(url, headers={"User-Agent": self.user_agent})
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            logging.critical("Failed to check if there is unclaimed SLP")
            return None
        unclaimed_slp = int(response.json()['total'])
        last_claim = datetime.utcfromtimestamp(int(response.json()["last_claimed_item_at"]))
        if datetime.utcnow() - timedelta(days=14) >= last_claim and unclaimed_slp > 0:
            return unclaimed_slp
        return None

    def create_random_msg(self):
        payload = {
            "operationName": "CreateRandomMessage",
            "variables": {},
            "query": "mutation CreateRandomMessage{createRandomMessage}"
        }
        url = "https://graphql-gateway.axieinfinity.com/graphql"
        response = requests.post(url, headers={"User-Agent": self.user_agent}, json=payload)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise Exception(f"Error! Creating random msg! Error: {e}")
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
                    "owner": f"{self.account}",
                    "message": f"{msg}",
                    "signature": f"{hex_msg}"
                }
            },
            "query": "mutation CreateAccessTokenWithSignature($input: SignatureInput!)"
            "{createAccessTokenWithSignature(input: $input) "
            "{newAccount result accessToken __typename}}"
        }
        url = "https://graphql-gateway.axieinfinity.com/graphql"
        response = requests.post(url, headers={"User-Agent": self.user_agent}, json=payload)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
           raise Exception(f"Error! Getting JWT! Error: {e}")
        return response.json()['data']['createAccessTokenWithSignature']['accessToken']

    async def execute(self):
        unclaimed =self.has_unclaimed_slp()
        if not unclaimed:
            logging.info(f"Account {self.account.replace('0x', 'ronin:')} has no claimable SLP")
            return
        logging.info(f"Account {self.account.replace('0x', 'ronin:')} has "
                     f"{unclaimed} unclaimed SLP")
        jwt = self.get_jwt()
        headers = {
            "User-Agent": self.user_agent,
            "authorization": f"Bearer {jwt}"
        }
        url = f"https://game-api.skymavis.com/game-api/clients/{self.account}/items/1/claim"
        response = requests.post(url, headers=headers)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise Exception("Error! Executing SLP claim API call for account "
                            f"{self.account.replace('0x', 'ronin:')}. Error {e}")
        signature = response.json()["blockchain_related"]["signature"]
        nonce = get_nonce(self.account)
        # Build claim
        claim = self.slp_contract.functions.checkpoint(
            Web3.toChecksumAddress(self.account),
            signature['amount'],
            signature['timestamp'],
            signature['signature'].replace("0x", "")
        ).buildTransaction({'gas': 1000000, 'gasPrice': 0, 'nonce': nonce})
        # Sign claim
        signed_claim = self.w3.eth.account.sign_transaction(
            claim,
            private_key=bytearray.fromhex(self.private_key.replace("0x", ""))
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
                logging.info(f"Waiting for claim for '{self.account.replace('0x', 'ronin:')}' to finish (Nonce:{nonce})...")
                # Sleep 5 seconds not to constantly send requests!
                await asyncio.sleep(5)
        
        if success:
            logging.info(f"Claimed SLP {signature['amount']} for account {self.account.replace('0x', 'ronin:')}")
            logging.info(f"New balance for account {self.account.replace('0x', 'ronin:')} is: "
                         f"{check_balance(self.account)}")
        else:
            logging.info(f"Claim for account {self.account.replace('0x', 'ronin:')} failed")


class AxieClaimsManager:
    def __init__(self, secrets_file):
        self.secrets_file = load_json(secrets_file)

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
        claims_list = [Claim(acc, self.secrets_file[acc]) for acc in self.secrets_file]
        logging.info("Claiming starting...")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*[claim.execute() for claim in claims_list]))
        logging.info("Claiming completed!")
