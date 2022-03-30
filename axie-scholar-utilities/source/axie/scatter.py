import logging

from axie_utils import check_balance, Scatter

class ScatterRonManager:
    def __init__(self, from_acc, payments, secrets, min_ron):
        self.min_ron = min_ron
        self.from_acc = from_acc
        self.from_private = secrets[self.from_acc]
        self.scatter_accounts_amounts = self.load_scatter(payments)

    def load_scatter(self, payments):
        scatter_dict = {}
        if 'Manager' in payments:
            for scholar in payments['Scholars']:
                # check how much ron to scatter
                missing_ron = self.min_ron - check_balance(scholar['AccountAddress'], 'ron')
                if missing_ron > 0:
                    scatter_dict[scholar['AccountAddress']] = missing_ron
                else:
                    logging.info(f'Account {scholar["AccountAddress"]} already has more than the min ron desired')
        else:
            for scholar in payments['scholars']:
                # check how much ron to scatter
                missing_ron = self.min_ron - check_balance(scholar['ronin'], 'ron')
                if missing_ron > 0:
                    scatter_dict[scholar['ronin']] = missing_ron
                else:
                    logging.info(f'Account {scholar["ronin"]} already has more than the min ron desired')
        return scatter_dict
    
    def execute(self):
        s = Scatter('ron', self.from_acc, self.from_private, self.scatter_accounts_amounts)
        s.execute()
