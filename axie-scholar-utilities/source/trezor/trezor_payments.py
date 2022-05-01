import sys
import logging
from datetime import datetime
from math import floor

from jsonschema import validate
from jsonschema.exceptions import ValidationError
from trezorlib.client import get_default_client

from axie.payments import PaymentsSummary
from axie.schemas import payments_schema, legacy_payments_schema
from axie.utils import ImportantLogsFilter
from axie_utils import CustomUI, check_balance, TrezorScatter


CREATOR_FEE_ADDRESS = "ronin:9fa1bc784c665e683597d3f29375e45786617550"

now = int(datetime.now().timestamp())
log_file = f'logs/results_{now}.log'
logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.addFilter(ImportantLogsFilter())
logger.addHandler(file_handler)


class TrezorAxiePaymentsManager:
    def __init__(self, payments_file, trezor_config, auto=False):
        self.payments_file = payments_file
        self.trezor_config = trezor_config
        self.manager_acc = None
        self.scholar_accounts = None
        self.donations = None
        self.type = None
        self.auto = auto
        self.summary = PaymentsSummary()

    def legacy_verify(self):
        validation_success = True
        # check manager ronin
        if len(self.payments_file["Manager"].replace("ronin:", "0x")) != 42:
            logging.critical(f"Check your manager ronin {self.payments_file['Manager']}, it has an incorrect format")
            validation_success = False
        # check donations do not exceed 100%
        if self.payments_file.get("Donations"):
            total = sum([x["Percent"] for x in self.payments_file["Donations"]])
            if total > 99:
                logging.critical("Payments file donations exeeds 100%, please review it")
                validation_success = False
            if any(len(dono['AccountAddress'].replace("ronin:", "0x")) != 42 for dono in self.payments_file["Donations"]): # noqa
                logging.critical("Please review the ronins in your donations. One or more are wrong!")
                validation_success = False
            self.donations = self.payments_file["Donations"]

        # Check we have private keys for all accounts
        for acc in self.payments_file["Scholars"]:
            if acc["AccountAddress"].lower() not in self.trezor_config:
                logging.critical(f"Account '{acc['Name']}' is not present in trezor_config file, please add it.")
                validation_success = False       
        if not validation_success:
            logging.critical("Please make sure your payments.json file looks like the legacy one in the wiki or the sample files.\n"
                             "Find it here: https://ferranmarin.github.io/axie-scholar-utilities/ \n"
                             "Make sure you have configured all accounts too!")
            sys.exit()
        return
    
    def verify(self):
        validation_success = True
        # check donations do not exceed 100%
        if self.payments_file.get("donations"):
            total = sum([x["percentage"] for x in self.payments_file["donations"]])
            if total > 99:
                logging.critical("Payments file donations exeeds 100% adding the 1% fee, please review it")
                validation_success = False
            if any(len(dono['ronin'].replace("ronin:", "0x")) != 42 for dono in self.payments_file["donations"]): # noqa
                logging.critical("Please review the ronins in your donations. One or more are wrong!")
                validation_success = False
            self.donations = self.payments_file["donations"]

        # Check we have private keys for all accounts
        for acc in self.payments_file["scholars"]:
            if acc["ronin"].lower() not in self.trezor_config:
                logging.critical(f"Account '{acc['name']}' is not present in trezor_config file, please add it.")
                validation_success = False
            # Check all splits have a "manager" persona
            personas = []
            for split in acc["splits"]:
                personas.append(split["persona"].lower())
            if "manager" not in personas:
                logging.critical(f"Account '{acc['name']}' has no manager in its splits. Please review it!")
                validation_success = False

        if not validation_success:
            logging.critical("Please make sure your payments.json file looks like the payments one in the wiki or the sample files.\n"
                             "Find it here: https://ferranmarin.github.io/axie-scholar-utilities/ \n"
                             "Make sure you have configured all accounts too!")
            sys.exit()
        return

    def verify_inputs(self):
        logging.info("Validating file inputs...")
        validation_success = True
        # Validate payments file
        legacy_msg = None
        new_msg = None

        try:
            validate(self.payments_file, payments_schema)
            self.type = "new"
        except ValidationError as ex:
            new_msg = ("If you were tyring to pay using the current format:\n"
                       f"Error given: {ex.message}\n"
                       f"For attribute in: {list(ex.path)}\n")
            validation_success = False

        if not self.type:
            try:
                validate(self.payments_file, legacy_payments_schema)
                self.type = "legacy"
                validation_success = True
            except ValidationError as ex:
                legacy_msg = ("If you were tyring to pay using the legacy format:\n"
                              f"Error given: {ex.message}\n"
                              f"For attribute in: {list(ex.path)}\n")
                validation_success = False
        
        if not validation_success:
            msg = "Payments file failed validation. Please review it.\n"
            if new_msg:
                msg += new_msg
            if legacy_msg:
                msg += legacy_msg
            logging.critical(msg)
            sys.exit()
        
        if self.type == 'legacy':
            self.legacy_verify()
        elif self.type == 'new':
            self.verify()
        else:
            # This should not be reachable!
            logging.critical(f"Unexpected error! Unrecognized payments mode")
       
        if not validation_success:
            logging.critical("There is a problem with your trezor_config.json, delete it and re-generate the file starting with an empty file.")
            sys.exit()
        
        if self.type == "legacy":
            self.manager_acc = self.payments_file["Manager"]
            self.scholar_accounts = self.payments_file["Scholars"]
        elif self.type == "new":
            self.scholar_accounts = self.payments_file["scholars"]
        logging.info("Files correctly validated!")

    def check_acc_has_enough_balance(self, account, balance):
        account_balance = check_balance(account)
        if account_balance < balance:
            logging.critical(f"Balance in account {account} is "
                             "inssuficient to cover all planned payments!")
            return False
        elif account_balance - balance > 0:
            logging.info(f'These payments will leave {account_balance - balance} SLP in your wallet.'
                         'Cancel payments and adjust payments if you want to leave 0 SLP in it.')
        return True
    
    def prepare_payout(self):
        if self.type == "new":
            self.prepare_new_payout()
        elif self.type == "legacy":
            self.prepare_old_payout()
        else:
            logging.critical(f"Unexpected error! Unrecognized payments mode")

    def prepare_new_payout(self):
        for acc in self.scholar_accounts:
            client = get_default_client(
                ui=CustomUI(passphrase=self.trezor_config[acc['ronin'].lower()]['passphrase']))
            bip_path = self.trezor_config[acc['ronin'].lower()]['bip_path']
            acc_balance = check_balance(acc['ronin'])
            total_payments = 0
            acc_payments = {}
            deductable_fees = 1
            for dono in self.donations:
                deductable_fees += dono['percentage']
            # Split payments
            for sacc in acc['splits']:
                if sacc['persona'].lower() == 'manager':
                    amount = floor(acc_balance * ((sacc['percentage'] - deductable_fees)/100))
                else:
                    amount = floor(acc_balance * (sacc['percentage']/100))
                if amount < 1:
                    logging.info(f'Important: Skipping payment to {sacc["persona"]} as it would be less than 1SLP')
                    continue
                total_payments += amount
                # define type
                if sacc['persona'].lower() == 'manager':
                    t = 'manager'
                elif sacc['persona'].lower() == 'scholar':
                    t = 'scholar'
                elif sacc['persona'].lower() in ['trainer', 'investor', 'trainer/investor', 'investor/trainer']:
                    t = 'trainer'
                else:
                    t = 'other'
                acc_payments[sacc['ronin']] = amount
                self.summary.increase_payout(amount=amount, address=sacc['ronin'], payout_type=t)
            # Dono Payments
            if self.donations:
                for dono in self.donations:
                    dono_amount = floor(acc_balance * (dono["percentage"]/100))
                    if dono_amount > 0:
                        acc_payments[dono['ronin']] = dono_amount
                        self.summary.increase_payout(amount=dono_amount, address=dono['ronin'], payout_type='donation')
                        total_payments += dono_amount
            # Fee Payments
            fee_amount = floor(acc_balance * 0.01)
            if fee_amount > 0:
                acc_payments[CREATOR_FEE_ADDRESS] = fee_amount
                self.summary.increase_payout(amount=fee_amount, address=CREATOR_FEE_ADDRESS, payout_type='donation')
                total_payments += fee_amount
            if self.check_acc_has_enough_balance(acc['ronin'], total_payments) and acc_balance > 0:
                accept = "y" if self.auto else None
                while accept not in ["y", "n", "Y", "N"]:
                    accept = input(f"Do you want to proceed with payments for {acc['name']} ({acc_payments})? (y/n): ")
                if accept.lower() == "y":
                    s = TrezorScatter('slp', acc['ronin'], client, bip_path, acc_payments)
                    s.execute()
                    logging.info(f"SLP scatter completed for account: '{acc['name']}'")
                else:
                    logging.info(f"SLP scatter canceled for account: '{acc['name']}'")
        logging.info(f"Important: Transactions Summary:\n {self.summary}")

    def prepare_old_payout(self):
        for acc in self.scholar_accounts:
            client = get_default_client(
                ui=CustomUI(passphrase=self.trezor_config[acc['AccountAddress'].lower()]['passphrase']))
            bip_path = self.trezor_config[acc['AccountAddress'].lower()]['bip_path']
            acc_balance = check_balance(acc['AccountAddress'].lower())
            total_payments = 0
            acc_payments = {}
            # Scholar Payment
            scholar_amount = acc_balance * (acc["ScholarPercent"]/100)
            scholar_amount += acc.get("ScholarPayout", 0)
            scholar_amount = round(scholar_amount)
            acc_payments[acc["ScholarPayoutAddress"]] = scholar_amount
            self.summary.increase_payout(amount=scholar_amount, address=acc["ScholarPayoutAddress"], payout_type='scholar')
            total_payments += scholar_amount
            if acc.get("TrainerPayoutAddress"):
                # Trainer Payment
                trainer_amount = acc_balance * (acc["TrainerPercent"]/100)
                trainer_amount += acc.get("TrainerPayout", 0)
                trainer_amount = round(trainer_amount)
                if trainer_amount > 0:
                    acc_payments[acc["TrainerPayoutAddress"]] = trainer_amount
                    self.summary.increase_payout(amount=trainer_amount, address=acc["TrainerPayoutAddress"], payout_type='trainer')
                    total_payments += trainer_amount
            manager_payout = acc_balance - total_payments
            if self.donations:
                # Extra Donations
                for dono in self.donations:
                    dono_amount = round(acc_balance * (dono["Percent"]/100))
                    if dono_amount > 1:
                        acc_payments[dono['AccountAddress']] = dono_amount
                        self.summary.increase_payout(amount=dono_amount, address=dono['AccountAddress'], payout_type='donation')
                        manager_payout -= dono_amount
                        total_payments += dono_amount
            # Fee Payments
            fee_amount = round(acc_balance * 0.01)
            if fee_amount > 0:
                acc_payments[CREATOR_FEE_ADDRESS] = fee_amount
                self.summary.increase_payout(amount=fee_amount, address=CREATOR_FEE_ADDRESS, payout_type='donation')
                manager_payout -= fee_amount
                total_payments += fee_amount
            # Manager Payment
            if manager_payout > 0:
                acc_payments[self.manager_acc] = manager_payout
                self.summary.increase_payout(amount=manager_payout, address=self.manager_acc, payout_type='manager')
                total_payments += manager_payout
            else:
                logging.info("Important: Skipping manager payout as it resulted in 0 SLP.")
            if self.check_acc_has_enough_balance(acc['AccountAddress'], total_payments) and acc_balance > 0:
                accept = "y" if self.auto else None
                while accept not in ["y", "n", "Y", "N"]:
                    accept = input(f"Do you want to proceed with payments for {acc['name']} ({acc_payments})? (y/n): ")
                if accept.lower() == "y":
                    s = TrezorScatter('slp', acc['AccountAddress'], client, bip_path, acc_payments)
                    s.execute()
                    logging.info(f"SLP scatter completed for account: '{acc['Name']}'")
                else:
                    logging.info(f"SLP scatter canceled for account: '{acc['Name']}'")
        logging.info(f"Important: Transactions Summary:\n {self.summary}")
