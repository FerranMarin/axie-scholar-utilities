import logging

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RetryError
from hexbytes import HexBytes
from trezorlib import ethereum
from trezorlib.ui import ClickUI
from trezorlib.tools import parse_path 

from axie.utils import RETRIES


class CustomUI(ClickUI):
    def __init__(self, passphrase=None, *args, **kwargs):
        self.passphrase = passphrase
        super().__init__(*args, **kwargs)

    def get_passphrase(self, *args, **kwargs):
        return self.passphrase


class TrezorAxieGraphQL:
    
    def __init__(self, **kwargs):
        self.account = kwargs.get('account').replace("ronin:", "0x")
        self.request = requests.Session()
        self.request.mount('https://', HTTPAdapter(max_retries=RETRIES))
        self.user_agent = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36")
        self.client = kwargs.get('account')
        self.bip_path = parse_path(kwargs.get('bip_path'))

    def create_random_msg(self):
        payload = {
            "operationName": "CreateRandomMessage",
            "variables": {},
            "query": "mutation CreateRandomMessage{createRandomMessage}"
        }
        url = "https://graphql-gateway.axieinfinity.com/graphql"
        try:
            response = self.request.post(url, json=payload)
        except RetryError as e:
            logging.critical(f"Error! Creating random msg! Error: {e}")
            return None
        if 200 <= response.status_code <= 299:
            return response.json()['data']['createRandomMessage']
        return None

    def get_jwt(self):
        msg = self.create_random_msg()
        if not msg:
            return None
        signed_msg = ethereum.sign_message(self.client, self.bip_path, msg)
        hex_msg = HexBytes(signed_msg.signature).hex()
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
        try:
            response = self.request.post(url, headers={"User-Agent": self.user_agent}, json=payload)
        except RetryError as e:
            logging.critical(f"Error! Getting JWT! Error: {e}")
            return None
        if 200 <= response.status_code <= 299:
            if (not response.json()['data'].get('createAccessTokenWithSignature') or
               not response.json()['data']['createAccessTokenWithSignature'].get('accessToken')):
                logging.critical("Could not retreive JWT, probably your private key for this account is wrong. "
                                 f"Account: {self.account.replace('0x','ronin:')} \n AccountName: {self.acc_name}")
                return None
            return response.json()['data']['createAccessTokenWithSignature']['accessToken']
        return None
