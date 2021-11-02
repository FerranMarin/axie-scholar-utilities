__version__ = '1.11.0'
__all__ = [
    'AxiePaymentsManager',
    'AxieClaimsManager',
    'AxieTransferManager',
    'AxieMorphingManager',
    'Axies',
    'AxieBreedManager',
    'QRCodeManager'
]

from axie.payments import AxiePaymentsManager
from axie.claims import AxieClaimsManager
from axie.transfers import AxieTransferManager
from axie.morphing import AxieMorphingManager
from axie.axies import Axies
from axie.breeding import AxieBreedManager
from axie.qr_code import QRCodeManager
