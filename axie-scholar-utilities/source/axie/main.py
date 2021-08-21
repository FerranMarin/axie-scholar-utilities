import os
import json
import logging

from jsonschema import validate
from jsonschema.exceptions import ValidationError

from axie.schemas import payments_schema


class AxiePaymentsManager:
    def __init__(self, payments_file, secrets_file):
        self.payments_file = self.load_json(payments_file)
        self.secrets_file = self.load_json(secrets_file)

    @staticmethod
    def load_json(json_file):
        # This is a safe guard, it should never raise as we check this in the CLI bit.
        if not os.path.isfile(json_file):
            raise Exception(f"File path {json_file} does not exist. "
                            f"Please provide a correct one")
        with open(json_file) as f:
            data = json.load(f)
        return data

    def verify_inputs(self):
        logging.info("Validating file inputs...")
        validation_success = True
        # Validate payments file
        try:
            validate(self.payments_file, payments_schema)
        except ValidationError as ex:
            logging.critical("Payments file failed validation. Please review it. "
                             f"Error given: {ex.message}")
            validation_success = False
        # check donations do not exceed 100%
        if self.payments_file.get("Donations"):
            total = sum([x["Percent"] for x in self.payments_file.get("Donations")])
            if total > 1:
                logging.critical("Payments file donations exeeds 100%, please review it")
                validation_success = False
        # Check we have private keys for all accounts
        for acc in self.payments_file["Scholars"]:
            if acc["AccountAddress"] not in self.secrets_file:
                logging.critical(f"Account {acc} is not present in secret file, please add it.")
                validation_success = False
        if not validation_success:
            exit()
        logging.info("Files correctly validated!")
