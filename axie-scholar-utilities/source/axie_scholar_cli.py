""" Axie Scholar Utilities CLI.

Usage:
    axie_scholar_payments_cli.py payout <payments_file> <secrets_file>
    axie_scholar_payments_cli.py claim <secrets_file>
    axie_scholar_payments_cli.py generate_QR <secrets_file>
    axie_scholar_payments_cli.py generate_secrets
"""
import os
import sys
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
        raise NotImplementedError('Sorry, I have yet to implement this command')


if __name__ == '__main__':
    run_cli()
