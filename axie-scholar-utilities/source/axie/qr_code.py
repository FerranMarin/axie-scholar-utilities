import os
import logging
from datetime import datetime

import qrcode

from axie.utils import AxieGraphQL, load_json


class QRCode(AxieGraphQL):

    def __init__(self, acc_name, path, **kwargs):
        super(QRCode, self).__init__(**kwargs)
        self.acc_name = acc_name
        self.path = os.path.join(path , f'{self.acc_name.lower()}-{int(datetime.timestamp(datetime.now()))}.png')

    def generate_qr(self):
        jwt = self.get_jwt()
        logging.info('Create QR Code')
        qr = qrcode.make(jwt)
        logging.info(f'Saving QR Code for account {self.acc_name} at {self.path}')
        qr.save(self.path)


class QRCodeManager:

    def __init__(self, payments_file, secrets_file):
        self.secrets_file, self.acc_names = self.load_secrets_and_acc_name(secrets_file, payments_file)
        self.path = os.path.dirname(self.secrets_file)

    def load_secrets_and_acc_name(self, secrets_file, payments_file):
        secrets = load_json(secrets_file)
        payments = load_json(payments_file)
        refined_secrets = {}
        acc_names = {}
        for scholar in payments['Scholars']:
            key = scholar['AccountAddress']
            refined_secrets[key] = secrets[key]
            acc_names[key] = scholar['Name']
        return refined_secrets, acc_names
    
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
            qr.execute()
