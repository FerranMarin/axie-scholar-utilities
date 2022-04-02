import sys
import logging
from datetime import datetime

from jsonschema import validate
from jsonschema.exceptions import ValidationError
from trezorlib.client import get_default_client

from axie.schemas import transfers_schema
from axie.utils import load_json, ImportantLogsFilter
 
from axie_utils import CustomUI, TrezorTransfer, Axies


now = int(datetime.now().timestamp())
log_file = f'logs/results_{now}.log'
logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file, mode='w')
file_handler.setLevel(logging.INFO)
file_handler.addFilter(ImportantLogsFilter())
logger.addHandler(file_handler)


class TrezorAxieTransferManager:
    def __init__(self, transfers_file, trezor_config, secure=None):
        self.transfers_file = load_json(transfers_file)
        self.trezor_config = load_json(trezor_config)
        self.secure = secure

    def verify_inputs(self):
        logging.info("Validating file inputs...")
        validation_success = True
        # Validate transfers file
        try:
            validate(self.transfers_file, transfers_schema)
        except ValidationError as ex:
            logging.critical("Transfers file failed validation. Please review it. "
                             f"Error given: {ex.message}. "
                             f"For attribute in: {list(ex.path)}")
            validation_success = False
        # Check we have private keys for all accounts
        for acc in self.transfers_file:
            if acc["AccountAddress"].lower() not in self.trezor_config:
                logging.critical(f"Account '{acc['AccountAddress']}' is not present in trezor config file, "
                                 "please re-run trezor setup command.")
                validation_success = False
        if not validation_success:
            logging.critical("Please make sure your transfers.json file looks like the one in the README.md\n"
                             "Find it here: https://ferranmarin.github.io/axie-scholar-utilities/")
            sys.exit()
        logging.info("Files correctly validated!")

    def prepare_transfers(self):
        transfers = []
        logging.info("Preparing transfers")
        for acc in self.transfers_file:
            a = Axies(acc['AccountAddress'].lower())
            for axie in acc['Transfers']:
                if not self.secure or (self.secure and axie['ReceiverAddress'].lower() in self.trezor_config):
                    # Check axie in account
                    if a.check_axie_owner(axie['AxieId']):
                        t = TrezorTransfer(
                            to_acc=axie['ReceiverAddress'].lower(),
                            client=get_default_client(
                                ui=CustomUI(
                                    passphrase=self.trezor_config[acc['AccountAddress'].lower()]['passphrase'])),
                            bip_path=self.trezor_config[acc['AccountAddress'].lower()]['bip_path'],
                            from_acc=acc['AccountAddress'].lower(),
                            axie_id=axie['AxieId']
                        )
                        transfers.append(t)
                        logging.info(f"Added transaction to the list: {t}")
                    else:
                        logging.info(f"Axie ({axie['AxieId']}) not in account ({acc['AccountAddress']}), skipping.")
                else:
                    logging.info(f"Receiver address {axie['ReceiverAddress']} not in secrets.json, skipping transfer.")
            self.execute_transfers(transfers)

    def execute_transfers(self, transfers):
        logging.info("Starting to transfer axies")
        for t in transfers:
            t.execute()
        logging.info("Axie transfers finished")
