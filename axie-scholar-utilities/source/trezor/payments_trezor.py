import json
import rlp
from time import sleep
from datetime import datetime, timedelta

from trezorlib.client import get_default_client
from trezorlib.tools import parse_path
from trezorlib import ethereum
from web3 import Web3, exceptions
from axie.utils import (
    check_balance,
    get_nonce,
    load_json,
    Singleton,
    ImportantLogsFilter,
    SLP_CONTRACT,
    RONIN_PROVIDER_FREE,
    TIMEOUT_MINS
)


SLP_CONTRACT = "0xa8754b9fa15fc18bb59458815510e40a12cd2014"
RONIN_PROVIDER_FREE = "https://proxy.roninchain.com/free-gas-rpc"


class TrezorPayment:

    def __init__(self, name, client, from_acc, bip_path, to_acc, amount):
        self.w3 = Web3(Web3.HTTPProvider(RONIN_PROVIDER_FREE))
        self.name = name
        self.from_acc = from_acc.replace("ronin:", "0x")
        self.to_acc = to_acc.replace("ronin:", "0x")
        self.amount = amount
        with open("axie/slp_abi.json", encoding='utf-8') as f:
            slb_abi = json.load(f)
        self.contract = self.w3.eth.contract(
            address=Web3.toChecksumAddress(SLP_CONTRACT),
            abi=slb_abi
        )
        self.client = client
        self.bip_path = bip_path
        self.gwei = self.w3.toWei('0', 'gwei')
        self.gas = 250000

    def execute(self):
         # Get Nonce
        nonce = get_nonce(self.from_acc)
        # Build transaction
        send_tx =  self.contract.functions.transfer(
            Web3.toChecksumAddress(self.to_acc),
            self.amount
        ).buildTransaction({
            "chainId": 2020,
            "gas": self.gas,
            "gasPrice": self.gwei,
            "nonce": nonce
        })
        data = self.w3.toBytes(hexstr=send_tx['data'])
        to = self.w3.toBytes(hexstr=SLP_CONTRACT)

        sig = ethereum.sign_tx(
            self.client,
            n=self.bip_path,
            nonce=nonce,
            gas_price=self.gwei,
            gas_limit=self.gas,
            to=SLP_CONTRACT,
            value=0,
            data=data,
            chain_id=2020
        )
        transaction = rlp.encode((nonce, self.gwei, self.gas, to, 0, data) + sig)
        # Send raw transaction
        self.w3.eth.send_raw_transaction(transaction)
        hash = self.w3.toHex(self.w3.keccak(transaction))
        # Wait for transaction to finish or timeout
        start_time = datetime.now()
        while True:
            # We will wait for max 10minutes for this tx to respond, if it does not, we will re-try
            if datetime.now() - start_time > timedelta(minutes=TIMEOUT_MINS):
                success = False
                print(f"Transaction {self}, timed out!")
                break
            try:
                recepit = self.w3.eth.get_transaction_receipt(hash)
                if recepit["status"] == 1:
                    success = True
                else:
                    success = False
                break
            except exceptions.TransactionNotFound:
                # Sleep 10s while waiting
                sleep(10)
                print(f"Waiting for transaction '{self}' to finish (Nonce:{nonce})...")

        if success:
            print(f"Important: Transaction {self} completed! Hash: {hash} - "
                  f"Explorer: https://explorer.roninchain.com/tx/{str(hash)}")
        else:
            print(f"Important: Transaction {self} failed.")

    def __str__(self):
        return f"{self.name}({self.to_acc.replace('0x', 'ronin:')}) for the amount of {self.amount} SLP"


