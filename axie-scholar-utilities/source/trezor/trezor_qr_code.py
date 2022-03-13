import os
import sys
import logging
from datetime import datetime

from trezorlib.client import get_default_client
import qrcode

from axie.utils import load_json
from trezor.trezor_utils import TrezorAxieGraphQL, CustomUI


class TrezorQRCode(TrezorAxieGraphQL):

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


class TrezorQRCodeManager:

    def __init__(self, payments_file, trezor_config, path):
        self.trezor_config, self.acc_names = self.load_trezor_config_and_acc_name(trezor_config, payments_file)
        self.path = path

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
            for scholar in payments['scholar']:
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

    def execute(self):
        qrcode_list = [
            TrezorQRCode(
                acc_name=self.acc_names[acc],
                account=acc,
                client=get_default_client(ui=CustomUI(passphrase=self.trezor_config[acc]['passphrase'])),
                bip_path=self.trezor_config[acc]['bip_path'],
                path=self.path
            ) for acc in self.trezor_config
        ]
        for qr in qrcode_list:
            qr.generate_qr()
