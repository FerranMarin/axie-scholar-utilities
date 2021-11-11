__version__ = '1.12.0'
__all__ = [
    'TrezorAccountsSetup',
    'TrezorPayment'
]

from trezor.accounts_setup import TrezorAccountsSetup
from trezor.payments_trezor import TrezorPayment
