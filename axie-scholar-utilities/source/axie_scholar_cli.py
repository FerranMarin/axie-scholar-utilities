""" Axie Scholar Utilities CLI.
This tool will help you perform various actions.
They are: payout, claim, generate_secrets, mass_update_secrets, generate_payments, generate_QR, transfer_axies, axie_morphing

Usage:
    axie_scholar_cli.py payout <payments_file> <secrets_file> [-y]
    axie_scholar_cli.py claim <payments_file> <secrets_file>
    axie_scholar_cli.py generate_secrets <payments_file> [<secrets_file>]
    axie_scholar_cli.py mass_update_secrets <csv_file> <secrets_file>
    axie_scholar_cli.py generate_payments <csv_file> [<payments_file>]
    axie_scholar_cli.py generate_QR <secrets_file>
    axie_scholar_cli.py axie_morphing <secrets_file> <list_of_accounts>
    axie_scholar_cli.py transfer_axies <transfers_file> <secrets_file>
    axie_scholar_cli.py -h | --help
    axie_scholar_cli.py --version

Options:
    -h --help   Shows this extra help options
    -y --yes    Automatically say "yes" to all confirmation promts (they will not appear).
    --version   Show version.
"""
import os
import sys
import csv
import json
import logging

from docopt import docopt

from axie import AxiePaymentsManager, AxieClaimsManager, AxieTransferManager, Axies, MorphingManager
from axie.utils import load_json

# Setup logger
log = logging.getLogger()
log.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)


def generate_payments_file(csv_file_path, payments_file_path=None):
    if not payments_file_path:
        # Put payments file in same folder where the csv is
        folder = os.path.dirname(payments_file_path)
        payments_file_path = os.path.join(folder, 'payments.json')
        with open(payments_file_path, 'w') as f:
            f.write("{}")
    manager_acc = ''
    while manager_acc == '':
        msg = input('Please provide your manager ronin: ')
        if len(msg) == 46 and msg.startswith('ronin:'):
            # Make sure is a valid Hex
            try:
                int(msg[6:], 16)
            except ValueError:
                continue
            manager_acc = msg
        else:
            logging.info(f'Ronin provided ({msg}) looks wrong, try again.')

    with open(csv_file_path) as csv_file:
        reader = csv.DictReader(csv_file)
        scholars_list = []
        for row in reader:
            clean_row = {k: v for k, v in row.items() if v is not None and v != ''}
            integer_row = {k: int(v) for k, v in clean_row.items() if v.isdigit()}
            clean_row.update(integer_row)
            scholars_list.append(clean_row)

    payments_dict = {"Manager": manager_acc, "Scholars": scholars_list}

    with open(payments_file_path, 'w', encoding='utf-8') as f:
        json.dump(payments_dict, f, ensure_ascii=False, indent=4)
    log.info('New payments file saved')


def generate_secrets_file(payments_file_path, secrets_file_path=None):
    if not secrets_file_path:
        # Put secrets file in same folder where payments_file is
        folder = os.path.dirname(payments_file_path)
        secrets_file_path = os.path.join(folder, 'secrets.json')
        with open(secrets_file_path, 'w') as f:
            f.write('{}')
    payments = load_json(payments_file_path)
    secrets = load_json(secrets_file_path)
    changed = False
    for acc in payments['Scholars']:
        if acc['AccountAddress'] not in secrets:
            changed = True
            new_secret = ''
            while new_secret == '':
                msg = (f"Please provide private key for account {acc['Name']}. "
                       f"({acc['AccountAddress']}):")
                new_secret = input(msg)
            secrets[acc['AccountAddress']] = new_secret
    if changed:
        logging.info('Saving secrets file')
        with open(secrets_file_path, 'w', encoding='utf-8') as f:
            json.dump(secrets, f, ensure_ascii=False, indent=4)
        logging.info('File saved!')
    else:
        logging.info('Secrets file already had all needed secrets!')


def mass_update_secret_file(csv_file_path, secrets_file_path):
    new_secrets = {}
    with open(csv_file_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            new_secrets[row[0]] = row[1]

    old_secrets = load_json(secrets_file_path)
    merge = {**new_secrets, **old_secrets}
    with open(secrets_file_path, 'w') as f:
        json.dump(merge,  f, ensure_ascii=False, indent=4)


def check_file(file):
    if not os.path.isfile(file):
        logging.critical('Please provide a correct path to the file. '
                         f'Path provided: {file}')
        return False
    return True


def run_cli():
    """ Wrapper function for testing purposes"""
    args = docopt(__doc__, version='Axie Scholar Payments CLI v1.8.0')
    if args['payout']:
        logging.info("I shall help you pay!")
        payments_file_path = args['<payments_file>']
        secrets_file_path = args['<secrets_file>']
        if check_file(payments_file_path) and check_file(secrets_file_path):
            logging.info('I shall pay my scholars!')
            if args['--yes']:
                logging.info("Automatic acceptance active, it won't ask before each execution")
            apm = AxiePaymentsManager(payments_file_path, secrets_file_path, auto=args['--yes'])
            apm.verify_inputs()
            apm.prepare_payout()
        else:
            logging.critical("Please review your file paths and re-try.")
    elif args['claim']:
        payments_file_path = args['<payments_file>']
        secrets_file_path = args['<secrets_file>']
        if check_file(payments_file_path) and check_file(secrets_file_path):
            # Claim SLP
            logging.info('I shall claim SLP')
            acm = AxieClaimsManager(payments_file_path, secrets_file_path)
            acm.verify_inputs()
            acm.prepare_claims()
        else:
            logging.critical("Please review your file paths and re-try.")
    elif args['generate_secrets']:
        # Generate Secrets
        logging.info('I shall help you generate your secrets file')
        payments_file_path = args['<payments_file>']
        secrets_file_path = args.get('<secrets_file>')
        if (secrets_file_path and check_file(secrets_file_path) and check_file(payments_file_path) or
           not secrets_file_path and check_file(payments_file_path)):
            logging.info('If you do not know how to get your private keys, check: '
                         'https://ferranmarin.github.io/axie-scholar-utilities/pages/faq.html')
            generate_secrets_file(payments_file_path, secrets_file_path)
        else:
            logging.critical("Please review your file paths and re-try.")
    elif args['mass_update_secrets']:
        # Mass update secrets
        logging.info('I shall help you mass update your secrets file')
        csv_file_path = args['<csv_file>']
        secrets_file_path = args['<secrets_file>']
        if check_file(csv_file_path) and check_file(secrets_file_path):
            mass_update_secret_file(csv_file_path, secrets_file_path)
        else:
            logging.critical("Please review your file paths and re-try.")
    elif args['transfer_axies']:
        # Make Axie Transfers
        logging.info('I shall send axies around')
        transfers_file_path = args['<transfers_file>']
        secrets_file_path = args['<secrets_file>']
        if check_file(transfers_file_path) and check_file(secrets_file_path):
            atm = AxieTransferManager(transfers_file_path, secrets_file_path)
            atm.verify_inputs()
            atm.prepare_transfers()
        else:
            logging.critical("Please review your file paths and re-try.")
    elif args['generate_payments']:
        # Generate Payments File
        logging.info('I shall help you generate your payments file')
        csv_file_path = args['<csv_file>']
        payments_file_path = args.get('<payments_file>')
        if (payments_file_path and check_file(payments_file_path) and
           check_file(csv_file_path) or not payments_file_path and check_file(csv_file_path)):
            generate_payments_file(csv_file_path, payments_file_path)
        else:
            logging.critical("Please review your file paths and re-try.")
    elif args['axie_morphing']:
        # Morph axies from all accounts given
        logging.info('I shall morph all axies I can!')
        accs = args['<list_of_accounts>']
        secrets_file_path = args['<secrets_file>']
        if check_file(secrets_file_path):
            accs_list = accs.split(',')
            for acc in accs_list:
                axies_to_morph = Axies(acc).find_axies_to_morph()
                MorphingManager(axies_to_morph, acc, secrets_file_path).execute()
        else:
            logging.critical("Please review your file paths and re-try.")
    elif args['generate_QR']:
        # Generate QR codes
        logging.info('I shall generate QR codes')
        raise NotImplementedError('Sorry, I have yet to implement this command')


if __name__ == '__main__':
    run_cli()
