import sys
import logging
from datetime import datetime

from trezorlib.client import get_default_client

from axie.utils import load_json, ImportantLogsFilter
from axie_utils import TrezorMorph, CustomUI

now = int(datetime.now().timestamp())
log_file = f'logs/results_{now}.log'
logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.addFilter(ImportantLogsFilter())
logger.addHandler(file_handler)


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
