import sys
import logging
from datetime import datetime

from axie.utils import load_json, ImportantLogsFilter
from axie_utils import Morph


now = int(datetime.now().timestamp())
log_file = f'logs/results_{now}.log'
logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.addFilter(ImportantLogsFilter())
logger.addHandler(file_handler)


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
