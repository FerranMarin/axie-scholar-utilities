""" Axie Scholar Utilities CLI.

Usage:
    axie_scholar_payments_cli.py payout <payments_file> <secrets_file>
    axie_scholar_payments_cli.py claim <secrets_file>
    axie_scholar_payments_cli.py generate_QR <secrets_file>
    axie_scholar_payments_cli.py generate_secrets <payments_file> [<secrets_file>]
"""
import os
import sys
import json
import logging

from docopt import docopt

from axie import AxiePaymentsManager

# Setup logger
log = logging.getLogger()
log.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

def generate_secrets_file(payments_file_path, secrets_file_path=None):
    if not secrets_file_path:
        fn = "secrets.json"
        with open(fn, "w") as f:
            f.write("{}")
        secrets_file_path = "secrets.json"
    payments = AxiePaymentsManager.load_json(payments_file_path)
    secrets = AxiePaymentsManager.load_json(secrets_file_path)
    changed = False
    for acc in payments["Scholars"]:
        if acc["AccountAddress"] not in secrets:
            changed = True
            new_secret = ''
            while new_secret == '':
                new_secret = input(f"Please provide secret key for account {acc['Name']}."
                                   f"({acc['AccountAddress']}): ")
            secrets[acc["AccountAddress"]] = new_secret
    
    if changed:
        logging.info(f"Saving secrets file at {secrets_file_path}")
        with open(secrets_file_path, "w", encoding="utf-8") as f:
            json.dump(secrets, f, ensure_ascii=False, indent=4)
        logging.info(f"File saved!")
    else:
        logging.info("Secrets file already had all needed secrets!")


def run_cli():
    """ Wrapper function for testing purposes"""
    args = docopt(__doc__, version='Axie Scholar Payments CLI v0.1')
    if args['payout']:
        payments_file_path = args['<payments_file>']
        secrets_file_path = args['<secrets_file>']
        file_error = False
        if not os.path.isfile(payments_file_path):
            logging.critical("Please provide a correct path to the Payments file. "
                            f"Path provided: {payments_file_path}")
            file_error = True
        if not os.path.isfile(secrets_file_path):
            logging.critical("Please provide a correct path to the Secrets file. "
                            f"Path provided: {secrets_file_path}")
            file_error = True
        if file_error:
            raise Exception("Please review your file paths and re-try.")
        # Do Payout
        logging.info("I shall pay my scholars!")
        apm = AxiePaymentsManager(payments_file_path, secrets_file_path)
        apm.verify_inputs()
        apm.prepare_payout() 
    elif args['claim']:
        # Claim SLP
        logging.info('I shall claim SLP')
        raise NotImplementedError('Sorry, I have yet to implement this command')
    elif args['generate_QR']:
        # Generate QR codes
        logging.info('I shall generate QR codes')
        raise NotImplementedError('Sorry, I have yet to implement this command')
    elif args['generate_secrets']:
        # Generate Secrets
        logging.info('I shall help you generate your secrets file')
        payments_file_path = args['<payments_file>']
        secrets_file_path = args.get('<secrets_file>')
        file_error = False
        if not os.path.isfile(payments_file_path):
            logging.critical("Please provide a correct path to the Payments file. "
                            f"Path provided: {payments_file_path}")
            file_error = True
        if secrets_file_path and not os.path.isfile(secrets_file_path):
            logging.critical("Please provide a correct path to the Secrets file. "
                            f"Path provided: {secrets_file_path}")
            file_error = True
        if file_error:
            raise Exception("Please review your file paths and re-try.")
        generate_secrets_file(payments_file_path, secrets_file_path)


if __name__ == '__main__':
    run_cli()
