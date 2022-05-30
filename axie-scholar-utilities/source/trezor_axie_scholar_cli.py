""" Trezor Axie Scholar Utilities CLI.
This tool will help you perform various actions. If you use a trezor device.
They are: payout, claim, generate_payments, generate_QR, transfer_axies, axie_morphing,
axie_breeding, generate_breedings, scatter_ron and a few managed ones which mean
they have an integration with axie.management

Usage:
    trezor_axie_scholar_cli.py payout <payments_file> <config_file> [-y]
    trezor_axie_scholar_cli.py managed_payout <config_file> <token> [-y]
    trezor_axie_scholar_cli.py scatter_ron <payments_file> <config_file> <min_amount>
    trezor_axie_scholar_cli.py managed_scatter_ron <config_file> <token> <min_amount>
    trezor_axie_scholar_cli.py claim <payments_file> <config_file> [--force]
    trezor_axie_scholar_cli.py managed_claim <config_file> <token> [--force]
    trezor_axie_scholar_cli.py config_trezor <payments_file> [<config_file>]
    trezor_axie_scholar_cli.py managed_config_trezor <config_file> <token>
    trezor_axie_scholar_cli.py generate_payments <csv_file> [<payments_file>]
    trezor_axie_scholar_cli.py generate_QR <payments_file> <config_file>
    trezor_axie_scholar_cli.py managed_generate_QR <config_file> <token>
    trezor_axie_scholar_cli.py axie_morphing <config_file> <list_of_accounts>
    trezor_axie_scholar_cli.py axie_breeding <breedings_file> <config_file>
    trezor_axie_scholar_cli.py generate_breedings <csv_file> [<breedings_file>]
    trezor_axie_scholar_cli.py transfer_axies <transfers_file> <config_file> [--safe-mode]
    trezor_axie_scholar_cli.py generate_transfer_axies <csv_file> [<transfers_file>]
    trezor_axie_scholar_cli.py -h | --help
    trezor_axie_scholar_cli.py --version

Options:
    -h --help   Shows this extra help options
    -y --yes    Automatically say "yes" to all confirmation promts (they will not appear).
    --force     Forces claim even if last claim was less than 14 days ago. (Used to bypass possible issues)
    --version   Show version.
"""
import os
import sys
import csv
import json
import logging

import requests
from docopt import docopt

from axie_utils import Axies
from axie.utils import load_json
from trezor import (
    TrezorAccountsSetup,
    TrezorAxiePaymentsManager,
    TrezorAxieBreedManager,
    TrezorAxieClaimsManager,
    TrezorAxieTransferManager,
    TrezorAxieMorphingManager,
    TrezorQRCodeManager,
    TrezorScatterRonManager
)

# Setup logger
os.makedirs('logs', exist_ok=True)
log = logging.getLogger()
log.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)


def generate_transfers_file(csv_file_path, transfer_file_path=None):
    if not transfer_file_path:
        # Put transfer file in same folder where the csv is
        folder = os.path.dirname(csv_file_path)
        transfer_file_path = os.path.join(folder, 'transfers.json')
        with open(transfer_file_path, 'w', encoding='utf-8') as f:
            f.write("{}")

    transfers_dict = {}
    reader = csv.DictReader(open(csv_file_path, encoding='utf-8'))
    for row in reader:
        acc = row['AccountAddress']
        axie = row['AxieId']
        receiver = row['ReceiverAddress']
        ax_dict = {"AxieId": int(axie), "ReceiverAddress": receiver}
        if acc not in transfers_dict:
            transfers_dict[acc] = {"Transfers": [ax_dict]}
        else:
            transfers_dict[acc]['Transfers'].append(ax_dict)

    transfers_list = []
    for d in transfers_dict:
        transfers_list.append({"AccountAddress": d, "Transfers": transfers_dict[d]['Transfers']})

    with open(transfer_file_path, 'w', encoding='utf-8') as f:
        json.dump(transfers_list, f, ensure_ascii=False, indent=4)

    log.info("New transfers file saved")


def generate_breedings_file(csv_file_path, breeding_file_path=None):
    if not breeding_file_path:
        # Put breeding file in same folder where the csv is
        folder = os.path.dirname(csv_file_path)
        breeding_file_path = os.path.join(folder, 'breedings.json')
        with open(breeding_file_path, 'w', encoding='utf-8') as f:
            f.write("{}")

    reader = csv.DictReader(open(csv_file_path, encoding='utf-8'))
    breed_list = []
    for row in reader:
        clean_row = {k: v for k, v in row.items() if v is not None and v != ''}
        integer_row = {k: int(v) for k, v in clean_row.items() if v.isdigit()}
        clean_row.update(integer_row)
        breed_list.append(clean_row)

    with open(breeding_file_path, 'w', encoding='utf-8') as f:
        json.dump(breed_list, f, ensure_ascii=False, indent=4)

    log.info('New breeds file saved')


def generate_payments_file(csv_file_path, payments_file_path=None):
    if not payments_file_path:
        # Put payments file in same folder where the csv is
        folder = os.path.dirname(csv_file_path)
        payments_file_path = os.path.join(folder, 'payments.json')
        with open(payments_file_path, 'w', encoding='utf-8') as f:
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

    reader = csv.DictReader(open(csv_file_path, encoding='utf-8'))
    scholars_list = []
    for row in reader:
        clean_row = {k: v for k, v in row.items() if v is not None and v != ''}
        integer_row = {k: int(v) for k, v in clean_row.items() if v.isdigit() and k != "Name"}
        clean_row.update(integer_row)
        scholars_list.append(clean_row)

    payments_dict = {"Manager": manager_acc, "Scholars": scholars_list}

    with open(payments_file_path, 'w', encoding='utf-8') as f:
        json.dump(payments_dict, f, ensure_ascii=False, indent=4)

    log.info('New payments file saved')


def load_payments_file(token):
    url = "https://api.axie.management/external/epithslayer/user/scholars"
    r = requests.post(url, json={"accessToken": token})
    if r.status_code == 500:
        logging.critical('Something went wrong on axie.management side. Go to their Discord see what is it about!')
    if r.status_code == 426:
        logging.critical('You have been doing too many requests to axie.management, please wait 5min before a retry')
    if r.status_code != 200:
        logging.critical('Could not retrieve your information from axie.management, double check your token')
        sys.exit()
    # Only for testing!
    else:
        return r.json()


def check_file(file):
    if not os.path.isfile(file):
        logging.critical('Please provide a correct path to the file. '
                         f'Path provided: {file}')
        return False
    return True


def run_cli():
    """ Wrapper function for testing purposes"""
    args = docopt(__doc__, version='Trezor Axie Scholar Payments CLI v3.2.2')
    if args['payout']:
        logging.info("I shall help you pay!")
        payments_file_path = args['<payments_file>']
        config_file_path = args['<config_file>']
        if check_file(payments_file_path) and check_file(config_file_path):
            logging.info('I shall pay my scholars!')
            if args['--yes']:
                logging.info("Automatic acceptance active, it won't ask before each execution")
            apm = TrezorAxiePaymentsManager(load_json(payments_file_path), load_json(config_file_path), auto=args['--yes'])
            apm.verify_inputs()
            apm.prepare_payout()
        else:
            logging.critical("Please review your file paths and re-try.")
    if args['managed_payout']:
        logging.info("I shall help you pay!")
        token = args['<token>']
        payments = load_payments_file(token)
        config_file_path = args['<config_file>']
        if check_file(config_file_path):
            logging.info('I shall pay my scholars!')
            if args['--yes']:
                logging.info("Automatic acceptance active, it won't ask before each execution")
            apm = TrezorAxiePaymentsManager(payments, load_json(config_file_path), auto=args['--yes'])
            apm.verify_inputs()
            apm.prepare_payout()
        else:
            logging.critical("Please review your file paths and re-try.")
    elif args['scatter_ron']:
        logging.info("I shall help you scatter ron!")
        payments_file_path = args['<payments_file>']
        config_file_path = args['<config_file>']
        try:
            min_ron = float(args['<min_amount>'])
        except ValueError:
            logging.warning(f"Min amount {args['min_amount']} has to be a number!")
            sys.exit()
        if check_file(payments_file_path) and check_file(config_file_path):
            payment_account = ''
            while payment_account == '':
                msg = input("Provide ronin account that will provide the RON to scatter: ")
                if len(msg) == 46 and msg.startswith('ronin:'):
                    # Make sure is a valid Hex
                    try:
                        int(msg[6:], 16)
                    except ValueError:
                        continue
                    payment_account = msg
                else:
                    logging.info(f'Ronin provided ({msg}) looks wrong, try again.')
            logging.info('I shall scatter ron for my scholars!')
            scm = TrezorScatterRonManager(payment_account, load_json(payments_file_path), load_json(config_file_path), min_ron)
            scm.execute()
        else:
            logging.critical("Please review your file paths and re-try.")
    elif args['managed_scatter_ron']:
        logging.info("I shall help you scatter ron!")
        config_file_path = args['<config_file>']
        token = args['<token>']
        payments = load_payments_file(token)
        try:
            min_ron = float(args['<min_amount>'])
        except ValueError:
            logging.warning(f"Min amount {args['min_amount']} has to be a number!")
            sys.exit()
        if check_file(config_file_path):
            payment_account = ''
            while payment_account == '':
                msg = input("Provide ronin account that will provide the RON to scatter: ")
                if len(msg) == 46 and msg.startswith('ronin:'):
                    # Make sure is a valid Hex
                    try:
                        int(msg[6:], 16)
                    except ValueError:
                        continue
                    payment_account = msg
                else:
                    logging.info(f'Ronin provided ({msg}) looks wrong, try again.')
            logging.info('I shall scatter ron for my scholars!')
            scm = TrezorScatterRonManager(payment_account, payments, load_json(config_file_path), min_ron)
            scm.execute()
        else:
            logging.critical("Please review your file paths and re-try.")
    elif args['claim']:
        payments_file_path = args['<payments_file>']
        config_file_path = args['<config_file>']
        force = args['--force']
        if check_file(payments_file_path) and check_file(config_file_path):
            # Claim SLP
            logging.info('I shall claim SLP')
            acm = TrezorAxieClaimsManager(load_json(payments_file_path), load_json(config_file_path), force)
            acm.verify_inputs()
            acm.prepare_claims()
        else:
            logging.critical("Please review your file paths and re-try.")
    elif args['managed_claim']:
        token = args['<token>']
        payments = load_payments_file(token)
        config_file_path = args['<config_file>']
        force = args['--force']
        if check_file(config_file_path):
            # Claim SLP
            logging.info('I shall claim SLP')
            acm = TrezorAxieClaimsManager(payments, load_json(config_file_path), force)
            acm.verify_inputs()
            acm.prepare_claims()
        else:
            logging.critical("Please review your file paths and re-try.")
    elif args['config_trezor']:
        # Configure Trezor
        logging.info('I shall help you configure your trezor device to use this tool!')
        payments_file_path = args['<payments_file>']
        config_file_path = args.get('<config_file>')
        if (config_file_path and check_file(config_file_path) and check_file(payments_file_path) or
           not config_file_path and check_file(payments_file_path)):
            logging.info('You will be asked to introduce passphrases and number of accounts per passphrase until you '
                         'have configured the tool for all the accounts present in payments.json')
            if not config_file_path:
                tas = TrezorAccountsSetup(load_json(payments_file_path), None, None)
            else:
                tas = TrezorAccountsSetup(load_json(payments_file_path), load_json(config_file_path), config_file_path)
            tas.update_trezor_config()
        else:
            logging.critical("Please review your file paths and re-try.")
    elif args['managed_config_trezor']:
        # Configure Trezor
        logging.info('I shall help you configure your trezor device to use this tool!')
        token = args['<token>']
        payments = load_payments_file(token)
        config_file_path = args.get('<config_file>')
        if config_file_path and check_file(config_file_path):
            logging.info('You will be asked to introduce passphrases and number of accounts per passphrase until you '
                         'have configured the tool for all the accounts present in payments.json')
            tas = TrezorAccountsSetup(payments, load_json(config_file_path), config_file_path, type='new')
            tas.update_trezor_config()
        else:
            logging.critical("Please review your file paths and re-try.")
    elif args['generate_transfer_axies']:
        # Generate Axie Transfer Files
        logging.info('I shall help you create axie transfers file')
        csv_file_path = args['<csv_file>']
        transfers_file_path = args.get('<transfers_file>')
        if (transfers_file_path and check_file(transfers_file_path) and
           check_file(csv_file_path) or not transfers_file_path and check_file(csv_file_path)):
            generate_transfers_file(csv_file_path, transfers_file_path)
        else:
            logging.critical("Please review your file paths and re-try.")
    elif args['transfer_axies']:
        # Make Axie Transfers
        logging.info('I shall send axies around')
        transfers_file_path = args['<transfers_file>']
        config_file_path = args['<config_file>']
        secure = args.get("--safe-mode", None)
        if check_file(transfers_file_path) and check_file(config_file_path):
            atm = TrezorAxieTransferManager(transfers_file_path, config_file_path, secure=secure)
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
        config_file_path = args['<config_file>']
        if check_file(config_file_path):
            accs_list = accs.split(',')
            for acc in accs_list:
                axies_to_morph = Axies(acc).find_axies_to_morph()
                if axies_to_morph:
                    axm = TrezorAxieMorphingManager(axies_to_morph, acc, config_file_path)
                    axm.verify_inputs()
                    axm.execute()
                else:
                    logging.critical("No axies to be morphed found")
        else:
            logging.critical("Please review your file paths and re-try.")
    elif args['axie_breeding']:
        # Breed axies
        logging.info('I shall breed your axies')
        breedings_file_path = args['<breedings_file>']
        config_file_path = args['<config_file>']
        if check_file(breedings_file_path) and check_file(config_file_path):
            payment_account = ''
            while payment_account == '':
                msg = input("Provide ronin account that will pay the fee for breeding: ")
                if len(msg) == 46 and msg.startswith('ronin:'):
                    # Make sure is a valid Hex
                    try:
                        int(msg[6:], 16)
                    except ValueError:
                        continue
                    payment_account = msg
                else:
                    logging.info(f'Ronin provided ({msg}) looks wrong, try again.')
            abm = TrezorAxieBreedManager(breedings_file_path, config_file_path, payment_account)
            abm.verify_inputs()
            abm.execute()
        else:
            logging.critical("Please review your file paths and re-try.")
    elif args['generate_breedings']:
        # Generate breedings file
        logging.info('I shall help you generate a breedings file')
        breedings_file_path = args.get('<breedings_file>')
        csv_file_path = args['<csv_file>']
        if (breedings_file_path and check_file(breedings_file_path) and
           check_file(csv_file_path) or not breedings_file_path and check_file(csv_file_path)):
            generate_breedings_file(csv_file_path, breedings_file_path)
        else:
            logging.critical("Please review your file paths and re-try.")
    elif args['generate_QR']:
        # Generate QR codes
        logging.info('I shall generate QR codes')
        payments_file_path = args['<payments_file>']
        config_file_path = args['<config_file>']
        if check_file(payments_file_path) and check_file(config_file_path):
            qr = TrezorQRCodeManager(load_json(payments_file_path), load_json(config_file_path), os.path.dirname(config_file_path))
            qr.execute()
        else:
            logging.critical("Please review your file paths and re-try.")
    elif args['managed_generate_QR']:
        # Generate QR codes
        logging.info('I shall generate QR codes')
        token = args['<token>']
        payments = load_payments_file(token)
        config_file_path = args['<config_file>']
        if check_file(config_file_path):
            qr = TrezorQRCodeManager(payments, load_json(config_file_path), os.path.dirname(config_file_path))
            qr.execute()
        else:
            logging.critical("Please review your file paths and re-try.")


if __name__ == '__main__':
    run_cli()
