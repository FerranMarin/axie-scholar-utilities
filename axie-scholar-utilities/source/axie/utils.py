import os
import json
import logging

from web3 import Web3
from requests.packages.urllib3.util.retry import Retry


AXIE_CONTRACT = "0x32950db2a7164ae833121501c797d79e7b79d74c"
AXS_CONTRACT = "0x97a9107c1793bc407d6f527b77e7fff4d812bece"
SLP_CONTRACT = "0xa8754b9fa15fc18bb59458815510e40a12cd2014"
WETH_CONTRACT = "0xc99a6a985ed2cac1ef41640596c5a5f9f4e19ef5"
RONIN_PROVIDER_FREE = "https://proxy.roninchain.com/free-gas-rpc"
RONIN_PROVIDER = "https://api.roninchain.com/rpc"
RETRIES = Retry(
    total=5,
    backoff_factor=2,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=frozenset(['GET', 'POST'])
)
BALANCE_ABI = [
    {
      "constant": True,
      "inputs": [
          {
              "internalType": "address",
              "name": "",
              "type": "address"
          }
      ],
      "name": "balanceOf",
      "outputs": [
          {
              "internalType": "uint256",
              "name": "",
              "type": "uint256"
          }
      ],
      "payable": False,
      "stateMutability": "view",
      "type": "function"
    }
]


class ImportantLogsFilter(logging.Filter):
    """ Logging filter used to only keep important messages which will be
    written to the log file """
    def filter(self, record):
        return record.getMessage().startswith('Important:')


class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance

    def clear(cls):
        # We need this for testing purposes!
        try:
            del Singleton._instance
        except AttributeError:
            pass


def check_balance(account, token='slp'):
    if token == 'slp':
        contract = SLP_CONTRACT
    elif token == 'axs':
        contract = AXS_CONTRACT
    elif token == "axies":
        contract = AXIE_CONTRACT
    elif token == "weth":
        contract = WETH_CONTRACT
    else:
        return 0

    w3 = Web3(Web3.HTTPProvider(RONIN_PROVIDER))
    ctr = w3.eth.contract(
        address=Web3.toChecksumAddress(contract),
        abi=BALANCE_ABI
    )
    balance = ctr.functions.balanceOf(
        Web3.toChecksumAddress(account.replace("ronin:", "0x"))
    ).call()
    if token == 'weth':
        print(balance)
        return float(balance/1000000000000000000)
    return int(balance)


def get_nonce(account):
    w3 = Web3(Web3.HTTPProvider(RONIN_PROVIDER_FREE))
    nonce = w3.eth.get_transaction_count(
        Web3.toChecksumAddress(account.replace("ronin:", "0x"))
    )
    return nonce


def load_json(json_file):
    # This is a safe guard, it should never raise as we check this in the CLI.
    if not os.path.isfile(json_file):
        raise Exception(f"File path {json_file} does not exist. "
                        f"Please provide a correct one")
    try:
        with open(json_file) as f:
            data = json.load(f)
    except json.decoder.JSONDecodeError:
        raise Exception(f"File in path {json_file} is not a correctly encoded JSON.")
    return data


if __name__ == "__main__":
    slp = check_balance("ronin:9fa1bc784c665e683597d3f29375e45786617550")
    axs = check_balance("ronin:9fa1bc784c665e683597d3f29375e45786617550", "axs")
    axies = check_balance("ronin:9fa1bc784c665e683597d3f29375e45786617550", "axies")
    weth = check_balance("ronin:9fa1bc784c665e683597d3f29375e45786617550", "weth")
    print(f"SLP: {slp}, AXS: {axs}, AXIES: {axies}, WETH: {weth}")