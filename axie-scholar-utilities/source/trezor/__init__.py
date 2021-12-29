__version__ = '1.15.1'
__all__ = [
    'TrezorAccountsSetup',
    'TrezorAxiePaymentsManager',
    'TrezorAxieBreedManager',
    'TrezorAxieClaimsManager',
    'TrezorAxieTransferManager',
    'TrezorAxieMorphingManager',
    'TrezorQRCodeManager'
]

from trezor.trezor_setup import TrezorAccountsSetup
from trezor.trezor_payments import TrezorAxiePaymentsManager
from trezor.trezor_breeding import TrezorAxieBreedManager
from trezor.trezor_claims import TrezorAxieClaimsManager
from trezor.trezor_transfers import TrezorAxieTransferManager
from trezor.trezor_morphing import TrezorAxieMorphingManager
from trezor.trezor_qr_code import TrezorQRCodeManager
