import json

from web3 import Web3

SLP_CONTRACT = "0xa8754b9fa15fc18bb59458815510e40a12cd2014"
RONIN_PROVIDER_FREE = "https://proxy.roninchain.com/free-gas-rpc"
RONIN_PROVIDER = "https://api.roninchain.com/rpc"

def check_balance(account):
        w3 = Web3(Web3.HTTPProvider(RONIN_PROVIDER))
        with open("axie/min_abi.json") as f:
            min_abi = json.load(f)
        slp_contract = w3.eth.contract(
            address=Web3.toChecksumAddress(SLP_CONTRACT),
            abi=min_abi
        )
        balance = slp_contract.functions.get_balance(
            Web3.toChecksumAddress(account.replace("ronin:", "0x"))
        ).call()
        return int(balance)
