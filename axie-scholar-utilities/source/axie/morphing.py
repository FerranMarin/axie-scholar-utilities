import sys
import logging
from datetime import datetime

from eth_account.messages import encode_defunct
from requests.exceptions import RetryError
from web3 import Web3

from axie.utils import load_json, AxieGraphQL, ImportantLogsFilter


now = int(datetime.now().timestamp())
log_file = f'logs/results_{now}.log'
logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.addFilter(ImportantLogsFilter())
logger.addHandler(file_handler)


class Morph(AxieGraphQL):

    def __init__(self, axie, **kwargs):
        self.axie = axie
        super().__init__(**kwargs)

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
            if response.json().get('data') and response.json()['data'].get('morphAxie'):
                logging.info(f"Important: Axie {self.axie} in {self.account} correctly morphed!")
            else:
                logging.info(f"Important: Something went wrong morphing axie {self.axie} in {self.account}")
        else:
            logging.critical(f"Important! Axie {self.axie} in {self.account} is not ready to be morphed!")


class AxieMorphingManager:

    def __init__(self, axie_list, account, secrets_file):
        self.axie_list = axie_list
        self.account = account
        self.secrets = load_json(secrets_file)

    def verify_inputs(self):
        if self.account not in self.secrets:
            logging.critical(f"Account '{self.account}' is not present in secret file, please add it.")
            sys.exit()

    def execute(self):
        logging.info(f"About to start morphing axies for account {self.account}")
        for axie in self.axie_list:
            m = Morph(axie=axie, account=self.account, private_key=self.secrets[self.account])
            m.execute()
        logging.info(f"Done morphing axies for account {self.account}")
