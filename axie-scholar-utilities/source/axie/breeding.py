import sys
import logging
from datetime import datetime

from jsonschema import validate
from jsonschema.exceptions import ValidationError

from axie.schemas import breeding_schema
from axie.utils import load_json, ImportantLogsFilter
from axie.payments import PaymentsSummary, CREATOR_FEE_ADDRESS
from axie_utils import Breed, Payment, check_balance


now = int(datetime.now().timestamp())
log_file = f'logs/results_{now}.log'
logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.addFilter(ImportantLogsFilter())
logger.addHandler(file_handler)


class AxieBreedManager:
    def __init__(self, breeding_file, secrets_file, payment_account):
        self.secrets = load_json(secrets_file)
        self.breeding_file = load_json(breeding_file)
        self.payment_account = payment_account
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
            if acc['AccountAddress'] not in self.secrets:
                logging.critical(f"Account '{acc['AccountAddress']}' is not present in secret file, please add it.")
                validation_error = True
        if self.payment_account not in self.secrets:
            logging.critical(f"Payment account '{self.payment_account}' is not present in secret file, please add it.")
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
        elif 15 < number_of_breeds <= 30:
            cost = (15 * 30) + ((number_of_breeds - 15) * 25)
        elif 30 < number_of_breeds <= 50:
            cost = (15 * 30) + (15 * 25) + ((number_of_breeds - 30) * 20)
        else:
            cost = (15 * 30) + (15 * 25) + (20 * 20) + ((number_of_breeds - 50) * 15)
        return cost

    def execute(self):
        if check_balance(self.payment_account) < self.calculate_cost():
            logging.critical("Not enough SLP funds to pay for breeding and the fee")
            sys.exit()

        logging.info("About to start breeding axies")
        for bf in self.breeding_file:
            b = Breed(
                sire_axie=bf['Sire'],
                matron_axie=bf['Matron'],
                address=bf['AccountAddress'],
                private_key=self.secrets[bf['AccountAddress']]
            )
            b.execute()
        logging.info("Done breeding axies")
        fee = self.calculate_fee_cost()
        logging.info(f"Time to pay the fee for breeding. For this session it is: {fee} SLP")
        p = Payment(
            "Breeding Fee",
            "donation",
            self.payment_account,
            self.secrets[self.payment_account],
            CREATOR_FEE_ADDRESS,
            fee,
            PaymentsSummary()
        )
        p.execute()
