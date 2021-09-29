import os
import json
import logging

from web3 import Web3

SLP_CONTRACT = "0xa8754b9fa15fc18bb59458815510e40a12cd2014"
RONIN_PROVIDER_FREE = "https://proxy.roninchain.com/free-gas-rpc"
RONIN_PROVIDER = "https://api.roninchain.com/rpc"


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


def check_balance(account):
    w3 = Web3(Web3.HTTPProvider(RONIN_PROVIDER))
    with open("axie/slp_abi.json") as f:
        min_abi = json.load(f)
    slp_contract = w3.eth.contract(
        address=Web3.toChecksumAddress(SLP_CONTRACT),
        abi=min_abi
    )
    balance = slp_contract.functions.balanceOf(
        Web3.toChecksumAddress(account.replace("ronin:", "0x"))
    ).call()
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
