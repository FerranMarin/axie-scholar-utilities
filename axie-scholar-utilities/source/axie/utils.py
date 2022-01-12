import os
import json
import logging

from eth_account.messages import encode_defunct
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RetryError
from requests.packages.urllib3.util.retry import Retry
from web3 import Web3



USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36" # noqa
TIMEOUT_MINS = 5
AXIE_CLAIM_COOLDOWN_SECONDS = 60 * 60 * 24 * 14 # Timezone agnostic comparisons
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

    w3 = Web3(
            Web3.HTTPProvider(
                RONIN_PROVIDER,
                request_kwargs={"headers": {"content-type": "application/json", "user-agent": USER_AGENT}}))
    ctr = w3.eth.contract(
        address=Web3.toChecksumAddress(contract),
        abi=BALANCE_ABI
    )
    balance = ctr.functions.balanceOf(
        Web3.toChecksumAddress(account.replace("ronin:", "0x"))
    ).call()
    if token == 'weth':
        return float(balance/1000000000000000000)
    return int(balance)


def get_nonce(account):
    w3 = Web3(
            Web3.HTTPProvider(
                RONIN_PROVIDER_FREE,
                request_kwargs={"headers": {"content-type": "application/json", "user-agent": USER_AGENT}}))
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
        with open(json_file, encoding='utf-8') as f:
            data = json.load(f)
    except json.decoder.JSONDecodeError:
        raise Exception(f"File in path {json_file} is not a correctly encoded JSON.")
    return data


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


class AxieGraphQL:

    def __init__(self, **kwargs):
        self.account = kwargs.get('account').replace("ronin:", "0x")
        self.private_key = kwargs.get('private_key')
        self.request = requests.Session()
        self.request.mount('https://', HTTPAdapter(max_retries=RETRIES))
        self.user_agent = USER_AGENT

    def create_random_msg(self):
        payload = {
            "operationName": "CreateRandomMessage",
            "variables": {},
            "query": "mutation CreateRandomMessage{createRandomMessage}"
        }
        url = "https://graphql-gateway.axieinfinity.com/graphql"
        try:
            response = self.request.post(url, json=payload)
        except RetryError as e:
            logging.critical(f"Error! Creating random msg! Error: {e}")
            return None
        if (200 <= response.status_code <= 299 and response.json().get('data') and
           response.json()['data'].get('createRandomMessage')):
            return response.json()['data']['createRandomMessage']
        return None

    def get_jwt(self):
        msg = self.create_random_msg()
        if not msg:
            return None
        signed_msg = Web3().eth.account.sign_message(encode_defunct(text=msg),
                                                     private_key=self.private_key)
        hex_msg = signed_msg['signature'].hex()
        payload = {
            "operationName": "CreateAccessTokenWithSignature",
            "variables": {
                "input": {
                    "mainnet": "ronin",
                    "owner": f"{self.account}",
                    "message": f"{msg}",
                    "signature": f"{hex_msg}"
                }
            },
            "query": "mutation CreateAccessTokenWithSignature($input: SignatureInput!)"
            "{createAccessTokenWithSignature(input: $input) "
            "{newAccount result accessToken __typename}}"
        }
        url = "https://graphql-gateway.axieinfinity.com/graphql"
        try:
            response = self.request.post(url, headers={"User-Agent": self.user_agent}, json=payload)
        except RetryError as e:
            logging.critical(f"Error! Getting JWT! Error: {e}")
            return None
        if 200 <= response.status_code <= 299:
            if (not response.json().get('data') or not response.json()['data'].get('createAccessTokenWithSignature') or
               not response.json()['data']['createAccessTokenWithSignature'].get('accessToken')):
                logging.critical("Could not retreive JWT, probably your private key for this account is wrong. "
                                 f"Account: {self.account.replace('0x','ronin:')} \n AccountName: {self.acc_name}")
                return None
            return response.json()['data']['createAccessTokenWithSignature']['accessToken']
        return None
