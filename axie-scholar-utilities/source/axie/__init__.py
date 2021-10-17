__version__ = '1.9.0'
__all__ = [
    'AxiePaymentsManager',
    'AxieClaimsManager',
    'AxieTransferManager',
    'MorphingManager',
    'Axies',
    'BreedManager',
    'QRCodeManager'
]

from axie.payments import AxiePaymentsManager
from axie.claims import AxieClaimsManager
from axie.transfers import AxieTransferManager
from axie.morphing import MorphingManager
from axie.axies import Axies
from axie.breeding import BreedManager
from axie.qr_code import QRCodeManager
