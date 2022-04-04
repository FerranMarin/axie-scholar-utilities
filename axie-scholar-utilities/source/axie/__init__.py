__version__ = '3.0.7'
__all__ = [
    'AxiePaymentsManager',
    'AxieClaimsManager',
    'AxieTransferManager',
    'AxieMorphingManager',
    'AxieBreedManager',
    'QRCodeManager',
    'ScatterRonManager'
]

from axie.payments import AxiePaymentsManager
from axie.claims import AxieClaimsManager
from axie.transfers import AxieTransferManager
from axie.scatter import ScatterRonManager
from axie.morphing import AxieMorphingManager
from axie.breeding import AxieBreedManager
from axie.qr_code import QRCodeManager
