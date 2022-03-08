import os
import sys
import logging
from datetime import datetime

import qrcode

from axie.utils import AxieGraphQL


class QRCode(AxieGraphQL):

    def __init__(self, acc_name, path, **kwargs):
        self.acc_name = acc_name
        self.path = os.path.join(path, f'{self.acc_name.lower()}-{int(datetime.timestamp(datetime.now()))}.png')
        super().__init__(**kwargs)

    def generate_qr(self):
        jwt = self.get_jwt()
        logging.info('Create QR Code')
        qr = qrcode.make(jwt)
        logging.info(f'Saving QR Code for account {self.acc_name} at {self.path}')
        qr.save(self.path)


class QRCodeManager:

    def __init__(self, payments_file, secrets_file):
        self.secrets_file, self.acc_names = self.load_secrets_and_acc_name(secrets_file, payments_file)
        self.path = os.path.dirname(secrets_file)

    def load_secrets_and_acc_name(self, secrets_file, payments_file):
        secrets = secrets_file
        payments = payments_file
        refined_secrets = {}
        acc_names = {}
        for scholar in payments['Scholars']:
            key = scholar['AccountAddress']
            refined_secrets[key] = secrets[key]
            acc_names[key] = scholar['Name']
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

    def execute(self):
        qrcode_list = [
            QRCode(
                account=acc,
                private_key=self.secrets_file[acc],
                acc_name=self.acc_names[acc],
                path=self.path
            ) for acc in self.secrets_file
        ]
        for qr in qrcode_list:
            qr.generate_qr()
