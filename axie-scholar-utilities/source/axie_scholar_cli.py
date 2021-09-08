""" Axie Scholar Utilities CLI.
This tool will help you perform various actions.
They are: payout, claim, generate_secrets, generate_QR

Usage:
    axie_scholar_cli.py payout <payments_file> <secrets_file> [-y]
    axie_scholar_cli.py claim <secrets_file>
    axie_scholar_cli.py generate_secrets <payments_file> [<secrets_file>]
    axie_scholar_cli.py generate_QR <secrets_file>
    axie_scholar_cli.py -h | --help
    axie_scholar_cli.py --version

Options:
    -h --help   Shows this extra help options
    -y --yes    Automatically say "yes" to all confirmation promts (they will not appear).
    --version   Show version.
"""
import os
import sys
import json
import logging

from docopt import docopt

from axie import AxiePaymentsManager, AxieClaimsManager
from axie.utils import load_json

# Setup logger
log = logging.getLogger()
log.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)


def generate_secrets_file(payments_file_path, secrets_file_path=None):
    if not secrets_file_path:
        # Put secrets file in same folder where payments_file is
        folder = os.path.dirname(payments_file_path)
        secrets_file_path = os.path.join(folder, "secrets.json")
        with open(secrets_file_path, "w") as f:
            f.write("{}")
    payments =load_json(payments_file_path)
    secrets = load_json(secrets_file_path)
    changed = False
    for acc in payments["Scholars"]:
        if acc["AccountAddress"] not in secrets:
            changed = True
            new_secret = ''
            while new_secret == '':
                msg = (f"Please provide secret key for account {acc['Name']}. "
                       f"({acc['AccountAddress']}):")
                new_secret = input(msg)
            secrets[acc["AccountAddress"]] = new_secret

    if changed:
        logging.info(f"Saving secrets file at {secrets_file_path}")
        with open(secrets_file_path, "w", encoding="utf-8") as f:
            json.dump(secrets, f, ensure_ascii=False, indent=4)
        logging.info(f"File saved at {secrets_file_path}!")
    else:
        logging.info("Secrets file already had all needed secrets!")


def run_cli():
    """ Wrapper function for testing purposes"""
    args = docopt(__doc__, version='Axie Scholar Payments CLI v1.1')
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
        if args['--yes']:
            logging.info("Automatic acceptance active, it won't ask before each execution")
        apm = AxiePaymentsManager(payments_file_path, secrets_file_path, auto=args['--yes'])
        apm.verify_inputs()
        apm.prepare_payout()
    elif args['claim']:
        secrets_file_path = args['<secrets_file>']
        if not os.path.isfile(secrets_file_path):
            logging.critical("Please provide a correct path to the Secrets file. "
                             f"Path provided: {secrets_file_path}")
            raise Exception("Please review your file paths and re-try.")
        # Claim SLP
        logging.info('I shall claim SLP')
        acm = AxieClaimsManager(secrets_file_path)
        acm.verify_input()
        acm.prepare_claims()
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
