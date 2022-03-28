import sys
import logging
from datetime import datetime

from jsonschema import validate
from jsonschema.exceptions import ValidationError
from trezorlib.client import get_default_client
from trezorlib.tools import parse_path

from axie.schemas import breeding_schema
from axie.utils import load_json, ImportantLogsFilter
from axie.payments import PaymentsSummary, CREATOR_FEE_ADDRESS
from axie_utils import CustomUI, TrezorBreed, TrezorPayment, check_balance


now = int(datetime.now().timestamp())
log_file = f'logs/results_{now}.log'
logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.addFilter(ImportantLogsFilter())
logger.addHandler(file_handler)


class TrezorAxieBreedManager:

    def __init__(self, breeding_file, trezor_config, payment_account):
        self.trezor_config = load_json(trezor_config)
        self.breeding_file = load_json(breeding_file)
        self.payment_account = payment_account.lower()
        self.breeding_costs = 0

    def verify_inputs(self):
        validation_error = False
        logging.info("Validating file inputs...")
        try:
            validate(self.breeding_file, breeding_schema)
        except ValidationError as ex:
            logging.critical(f'Validation of breeding file failed. Error given: {ex.message}\n'
                             f'For attribute in: {list(ex.path)}')
            validation_error = True
        for acc in self.breeding_file:
            if acc['AccountAddress'].lower() not in self.trezor_config:
                logging.critical(f"Account '{acc['AccountAddress']}' is not present in trezor config, "
                                 "please re-run setup.")
                validation_error = True
        if self.payment_account not in self.trezor_config:
            logging.critical(f"Payment account '{self.payment_account}' is not present in trezor config, "
                             "please re-run setup.")
            validation_error = True
        if validation_error:
            sys.exit()

    def calculate_cost(self):
        return self.calculate_fee_cost() + self.breeding_costs

    def calculate_breeding_cost(self):
        # TODO: We need to calculate how much will all breeding cost, pending for the future!
        return 0

    def calculate_fee_cost(self):
        number_of_breeds = len(self.breeding_file)
        if number_of_breeds <= 15:
            cost = number_of_breeds * 30
        if 15 < number_of_breeds <= 30:
            cost = (15 * 30) + ((number_of_breeds - 15) * 25)
        if 30 < number_of_breeds <= 50:
            cost = (15 * 30) + (15 * 25) + ((number_of_breeds - 30) * 20)
        if number_of_breeds > 50:
            cost = (15 * 30) + (15 * 25) + (20 * 20) + ((number_of_breeds - 50) * 15)
        return cost

    def execute(self):
        if check_balance(self.payment_account) < self.calculate_cost():
            logging.critical("Not enough SLP funds to pay for breeding and the fee")
            sys.exit()

        logging.info("About to start breeding axies")
        for bf in self.breeding_file:
            b = TrezorBreed(
                sire_axie=bf['Sire'],
                matron_axie=bf['Matron'],
                address=bf['AccountAddress'].lower(),
                client=get_default_client(ui=CustomUI(self.trezor_config[bf['AccountAddress'].lower()]['passphrase'])),
                bip_path=self.trezor_config[bf['AccountAddress'].lower()]['bip_path']
            )
            b.execute()
        logging.info("Done breeding axies")
        fee = self.calculate_fee_cost()
        logging.info(f"Time to pay the fee for breeding. For this session it is: {fee} SLP")
        p = TrezorPayment(
            "Breeding Fee",
            "donation",
            get_default_client(ui=CustomUI(passphrase=self.trezor_config[self.payment_account]['passphrase'])),
            parse_path(self.trezor_config[self.payment_account]['bip_path']),
            self.payment_account,
            CREATOR_FEE_ADDRESS,
            fee,
            PaymentsSummary()
        )
        p.execute()
