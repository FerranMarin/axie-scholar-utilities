import sys
import asyncio
import logging
from datetime import datetime
from trezorlib.client import get_default_client

from axie.utils import ImportantLogsFilter
from axie_utils import CustomUI, TrezorClaim


now = int(datetime.now().timestamp())
log_file = f'logs/results_{now}.log'
logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file, mode='w')
file_handler.setLevel(logging.INFO)
file_handler.addFilter(ImportantLogsFilter())
logger.addHandler(file_handler)


class TrezorAxieClaimsManager:
    def __init__(self, payments_file, trezor_config, force=False):
        self.trezor_config, self.acc_names = self.load_trezor_config_and_acc_name(trezor_config, payments_file)
        self.force = force

    def load_trezor_config_and_acc_name(self, trezor_config, payments_file):
        config = trezor_config
        payments = payments_file
        refined_config = {}
        acc_names = {}
        if 'Manager' in payments:
            for scholar in payments['Scholars']:
                key = scholar['AccountAddress'].lower()
                refined_config[key] = config[key]
                acc_names[key] = scholar['Name']
        else:
            for scholar in payments['scholars']:
                key = scholar['ronin']
                refined_config[key] = config[key]
                acc_names[key] = scholar['name']
        return refined_config, acc_names

    def verify_inputs(self):
        validation_success = True
        if not self.trezor_config:
            logging.warning("No configuration found for trezor")
            validation_success = False
        for acc in self.trezor_config:
            if not acc.startswith("ronin:"):
                logging.critical(f"Public address {acc} needs to start with ronin:")
                validation_success = False
        if not validation_success:
            sys.exit()
        logging.info("Files correctly validated")

    def prepare_claims(self):
        claims_list = [
            TrezorClaim(
                account=acc,
                force=self.force,
                client=get_default_client(ui=CustomUI(passphrase=self.trezor_config[acc]['passphrase'])),
                bip_path=self.trezor_config[acc]['bip_path'],
                acc_name=self.acc_names[acc]) for acc in self.trezor_config]
        logging.info("Claiming starting...")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*[claim.execute() for claim in claims_list]))
        logging.info("Claiming completed!")
