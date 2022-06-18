import sys
import logging
from datetime import datetime
from math import floor

from jsonschema import validate
from jsonschema.exceptions import ValidationError

from axie.schemas import payments_schema, legacy_payments_schema
from axie.utils import Singleton, ImportantLogsFilter
from axie_utils import Scatter, check_balance


CREATOR_FEE_ADDRESS = "ronin:9fa1bc784c665e683597d3f29375e45786617550"

now = int(datetime.now().timestamp())
log_file = f'logs/results_{now}.log'
logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.addFilter(ImportantLogsFilter())
logger.addHandler(file_handler)


class AxiePaymentsManager:
    def __init__(self, payments_file, secrets_file, auto=False):
        self.payments_file = payments_file
        self.secrets_file = secrets_file
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
            if acc["AccountAddress"] not in self.secrets_file:
                logging.critical(f"Account '{acc['Name']}' is not present in secret file, please add it.")
                validation_success = False       
        if not validation_success:
            logging.critical("Please make sure your payments.json file looks like the legacy one in the wiki or the sample files.\n"
                             "Find it here: https://ferranmarin.github.io/axie-scholar-utilities/ \n"
                             "Make sure you have configured all secrets too!")
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

        for acc in self.payments_file["scholars"]:
            # Check we have private keys for all accounts
            if acc["ronin"] not in self.secrets_file:
                logging.critical(f"Account '{acc['name']}' is not present in secret file, please add it.")
                validation_success = False
            # Check all splits have a "manager" persona
            personas = []
            for split in acc["splits"]:
                personas.append(split["persona"].lower())
            if "manager" not in personas:
                logging.critical(f"Account '{acc['name']}' has no manager in its splits. Please review it!")
                validation_success = False
        
        if not validation_success:
            logging.critical("Please make sure your payments.json file looks like the payments one in "
                             "the wiki or the sample files.\n"
                             "Find it here: https://ferranmarin.github.io/axie-scholar-utilities/ \n"
                             "Make sure you have configured all secrets too!")
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

        for sf in self.secrets_file:
            if len(self.secrets_file[sf]) != 66 or self.secrets_file[sf][:2] != "0x":
                logging.critical(f"Private key for account {sf} is not valid, please review it!")
                validation_success = False
        
        if not validation_success:
            logging.critical("There is a problem with your secrets.json, delete it and re-generate the file starting with an empty secrets file."
                             "Or open it and see what is wrong with the keys of the accounts reported above.")
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
            logging.critical(f"Unexpected error! Unrecognized payments mode {self.type}")

    def prepare_new_payout(self):
        for acc in self.scholar_accounts:
            acc_balance = check_balance(acc['ronin'])
            total_payments = 0
            acc_payments = {}
            deductable_fees = 1
            if self.donations:
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
            # Donation Payments
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
                    s = Scatter('slp', acc['ronin'], self.secrets_file[acc['ronin']], acc_payments)
                    s.execute()
                    logging.info(f"SLP scatter completed for account: '{acc['name']}'")
                else:
                    logging.info(f"SLP scatter canceled for account: '{acc['name']}'")
        logging.info(f"Important: Transactions Summary:\n {self.summary}")

    def prepare_old_payout(self):
        for acc in self.scholar_accounts:
            acc_balance = check_balance(acc['AccountAddress'])
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
                    accept = input(f"Do you want to proceed with payments for {acc['Name']} ({acc_payments})? (y/n): ")
                if accept.lower() == "y":
                    s = Scatter('slp', acc['AccountAddress'], self.secrets_file[acc['AccountAddress']], acc_payments)
                    s.execute()
                    logging.info(f"SLP scatter completed for account: '{acc['Name']}'")
                else:
                    logging.info(f"SLP scatter canceled for account: '{acc['Name']}'")
        logging.info(f"Important: Transactions Summary:\n {self.summary}")


class PaymentsSummary(Singleton):

    def __init__(self):
        self.manager = {"accounts": [], "slp": 0}
        self.trainer = {"accounts": [], "slp": 0}
        self.scholar = {"accounts": [], "slp": 0}
        self.other = {"accounts": [], "slp": 0}
        self.donations = {"accounts": [], "slp": 0}

    def increase_payout(self, amount, address, payout_type):
        if payout_type == "manager":
            self.increase_manager_payout(amount, address)
        elif payout_type == "scholar":
            self.increase_scholar_payout(amount, address)
        elif payout_type == "donation":
            self.increase_donations_payout(amount, address)
        elif payout_type == "trainer":
            self.increase_trainer_payout(amount, address)
        elif payout_type == "other":
            self.increase_other_payout(amount, address)

    def increase_manager_payout(self, amount, address):
        self.manager["slp"] += amount
        if address not in self.manager["accounts"]:
            self.manager["accounts"].append(address)

    def increase_trainer_payout(self, amount, address):
        self.trainer["slp"] += amount
        if address not in self.trainer["accounts"]:
            self.trainer["accounts"].append(address)

    def increase_scholar_payout(self, amount, address):
        self.scholar["slp"] += amount
        if address not in self.scholar["accounts"]:
            self.scholar["accounts"].append(address)

    def increase_donations_payout(self, amount, address):
        self.donations["slp"] += amount
        if address not in self.donations["accounts"]:
            self.donations["accounts"].append(address)
    
    def increase_other_payout(self, amount, address):
        self.other["slp"] += amount
        if address not in self.other["accounts"]:
            self.other["accounts"].append(address)

    def __str__(self):
        msg = "No payments made!"
        if self.manager["accounts"] and self.scholar["accounts"]:
            msg = f'Paid {len(self.manager["accounts"])} managers, {self.manager["slp"]} SLP.\n'
            msg += f'Paid {len(self.scholar["accounts"])} scholars, {self.scholar["slp"]} SLP.\n'
        if self.manager["accounts"] and not self.scholar["accounts"]:
            msg = f'Paid {len(self.manager["accounts"])} managers, {self.manager["slp"]} SLP.\n'
        if self.scholar["accounts"] and not self.manager["accounts"]:
            msg = f'Paid {len(self.scholar["accounts"])} scholars, {self.scholar["slp"]} SLP.\n'
        if self.trainer["slp"] > 0:
            msg += f'Paid {len(self.trainer["accounts"])} trainers, {self.trainer["slp"]} SLP.\n'
        if self.other["slp"] > 0:
            msg += f'Paid {len(self.other["accounts"])} other accounts, {self.other["slp"]} SLP.\n'
        if self.donations["slp"] > 0:
            msg += f'Donated to {len(self.donations["accounts"])} organisations, {self.donations["slp"]} SLP.\n'

        # TODO: Find a fix for this!
        msg += "---------------------- \n"
        msg += "This summary assumes all trasactions went fine, please do NOT trust it!\n"
        return msg
