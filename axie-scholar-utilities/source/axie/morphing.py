import logging

import requests
from eth_account.messages import encode_defunct
from web3 import Web3


class Morph:

    def __init__(self, axie, account, secret):
        self.axie = axie
        self.account = account.replace("ronin:", "0x")
        self.secret = secret
        self.user_agent = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36")

    def get_signature(self):
        msg = self.create_random_msg()
        signed_msg = Web3().eth.account.sign_message(encode_defunct(text=msg),
                                                     private_key=self.secret)
        return signed_msg['signature'].hex()

    def create_random_msg(self):
        payload = {
            "operationName": "CreateRandomMessage",
            "variables": {},
            "query": "mutation CreateRandomMessage{createRandomMessage}"
        }
        url = "https://graphql-gateway.axieinfinity.com/graphql"
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise Exception(f"Error! Creating random msg! Error: {e}")
        return response.json()['data']['createRandomMessage']

    def get_jwt(self):
        msg = self.create_random_msg()
        signed_msg = Web3().eth.account.sign_message(encode_defunct(text=msg),
                                                     private_key=self.secret)
        signature = signed_msg['signature'].hex()
        payload = {
            "operationName": "CreateAccessTokenWithSignature",
            "variables": {
                "input": {
                    "mainnet": "ronin",
                    "owner": f"{self.account}",
                    "message": f"{msg}",
                    "signature": f"{signature}"
                }
            },
            "query": "mutation CreateAccessTokenWithSignature($input: SignatureInput!)"
            "{createAccessTokenWithSignature(input: $input) "
            "{newAccount result accessToken __typename}}"
        }
        url = "https://graphql-gateway.axieinfinity.com/graphql"
        try:
            response = requests.post(url, headers={"User-Agent": self.user_agent}, json=payload)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise Exception(f"Error! Getting JWT! Error: {e}")
        if (not response.json()['data'].get('createAccessTokenWithSignature') or 
            not response.json()['data']['createAccessTokenWithSignature'].get('accessToken')):
            raise Exception("Could not retreive JWT, probably your private key for this account is wrong. "
                            f"Account: {self.account}")
        return response.json()['data']['createAccessTokenWithSignature']['accessToken']

    def execute(self):
        jwt = self.get_jwt()
        msg = f"axie_id={self.axie}&owner={self.account}"
        signed_msg = Web3().eth.account.sign_message(encode_defunct(text=msg),
                                                     private_key=self.secret)
        signature = signed_msg['signature'].hex()
        headers = {
            "User-Agent": self.user_agent,
            "authorization": f"Bearer {jwt}"
        }
        payload = {
            "operationName": "MorphAxie",
            "variables": {
                "axieId": f"{self.axie}",
                "owner": f"{self.account}",
                "signature": f"{signature}"
            },
            "query": "mutation MorphAxie($axieId: ID!, $owner: String!, $signature: String!) "
            "{morphAxie(axieId: $axieId, owner: $owner, signature: $signature)}"
        }
        url = 'https://graphql-gateway.axieinfinity.com/graphql'
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logging.info(f"Important! Axie {self.axie} in {self.account} is not ready to be morphed!")
            return

        if response.json().get('data') and response.json()['data'].get('morphAxie') :
            logging.info(f"Important: Axie {self.axie} in {self.account} correctly morphed!")
        else:
            logging.info(f"Important: Somethin went wrong morphing axie {self.axie} in {self.account}")
