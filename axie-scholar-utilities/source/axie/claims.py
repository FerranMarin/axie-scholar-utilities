import sys
import asyncio
import logging
from datetime import datetime

from axie.utils import ImportantLogsFilter
from axie_utils import Claim

now = int(datetime.now().timestamp())
log_file = f'logs/results_{now}.log'
logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file, mode='w')
file_handler.setLevel(logging.INFO)
file_handler.addFilter(ImportantLogsFilter())
logger.addHandler(file_handler)


class AxieClaimsManager:
    def __init__(self, payments_file, secrets_file, force=False):
        self.secrets_file, self.acc_names = self.load_secrets_and_acc_name(secrets_file, payments_file)
        self.force = force

    def load_secrets_and_acc_name(self, secrets, payments):
        refined_secrets = {}
        acc_names = {}
        if 'Manager' in payments:
            for scholar in payments['Scholars']:
                key = scholar['AccountAddress']
                refined_secrets[key] = secrets[key]
                acc_names[key] = scholar['Name']
        else:
            for scholar in payments['scholars']:
                key = scholar['ronin']
                refined_secrets[key] = secrets[key]
                acc_names[key] = scholar['name']
        return refined_secrets, acc_names

    def verify_inputs(self):
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
        claims_list = [
            Claim(
                force=self.force,
                account=acc,
                private_key=self.secrets_file[acc],
                acc_name=self.acc_names[acc]) for acc in self.secrets_file]
        logging.info("Claiming starting...")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*[claim.execute() for claim in claims_list]))
        logging.info("Claiming completed!")
