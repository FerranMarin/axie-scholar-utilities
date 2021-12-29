import sys
import logging
from datetime import datetime

from hexbytes import HexBytes
from trezorlib import ethereum
from trezorlib.client import get_default_client
from requests.exceptions import RetryError

from axie.utils import load_json, ImportantLogsFilter
from trezor.trezor_utils import TrezorAxieGraphQL, CustomUI

now = int(datetime.now().timestamp())
log_file = f'logs/results_{now}.log'
logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.addFilter(ImportantLogsFilter())
logger.addHandler(file_handler)


class TrezorMorph(TrezorAxieGraphQL):

    def __init__(self, axie, **kwargs):
        self.axie = axie
        super().__init__(**kwargs)

    def execute(self):
        jwt = self.get_jwt()
        msg = f"axie_id={self.axie}&owner={self.account}"
        signed_msg = ethereum.sign_message(self.client, self.bip_path, msg)
        signature = HexBytes(signed_msg.signature).hex()
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
                logging.info(f"Important: Somethin went wrong morphing axie {self.axie} in {self.account}")
        else:
            logging.critical(f"Important! Axie {self.axie} in {self.account} is not ready to be morphed!")


class TrezorAxieMorphingManager:

    def __init__(self, axie_list, account, trezor_config):
        self.axie_list = axie_list
        self.account = account.lower()
        self.trezor_config = load_json(trezor_config)

    def verify_inputs(self):
        if self.account not in self.trezor_config:
            logging.critical(f"Account '{self.account}' is not present in trezor config, please re-run trezor setup.")
            sys.exit()

    def execute(self):
        logging.info(f"About to start morphing axies for account {self.account}")
        for axie in self.axie_list:
            m = TrezorMorph(
                axie=axie,
                account=self.account,
                client=get_default_client(ui=CustomUI(passphrase=self.trezor_config[self.account]['passphrase'])),
                bip_path=self.trezor_config[self.account]['bip_path'])
            m.execute()
        logging.info(f"Done morphing axies for account {self.account}")
