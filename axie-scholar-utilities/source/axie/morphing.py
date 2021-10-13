import logging

from eth_account.messages import encode_defunct
from requests.exceptions import RetryError
from web3 import Web3

from axie.utils import load_json, AxieGraphQL

class Morph(AxieGraphQL):

    def __init__(self, axie, **kwargs):
        super(Morph, self).__init__(**kwargs)
        self.axie = axie

    def execute(self):
        jwt = self.get_jwt()
        msg = f"axie_id={self.axie}&owner={self.account}"
        signed_msg = Web3().eth.account.sign_message(encode_defunct(text=msg),
                                                     private_key=self.private_key)
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
            response = self.request.post(url, headers=headers, json=payload)
        except RetryError:
            logging.critical(f"Important! Axie {self.axie} in {self.account} is not ready to be morphed!")
            return
        
        if 200 <= response.status_code <= 299:
            if response.json().get('data') and response.json()['data'].get('morphAxie') :
                logging.info(f"Important: Axie {self.axie} in {self.account} correctly morphed!")
            else:
                logging.info(f"Important: Somethin went wrong morphing axie {self.axie} in {self.account}")
        else:
            logging.critical(f"Important! Axie {self.axie} in {self.account} is not ready to be morphed!")

class MorphingManager:

    def __init__(self, axie_list, account, secrets_file):
        self.axie_list = axie_list
        self.account = account
        self.secrets = load_json(secrets_file)
    
    def execute(self):
        logging.info(f"About to start morphing axies for account {self.account}")
        for axie in self.axie_list:
            Morph(axie=axie, account=self.account, private_key=self.secrets[axie['account']])
        logging.info(f"Done morphing axies for account {self.account}")
