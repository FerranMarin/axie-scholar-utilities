import json
import logging

from web3 import Web3, exceptions

from utils import get_nonce, RONIN_PROVIDER_FREE, AXIE_CONTRACT


class Breed:
    def __init__(self, sire_axie, matron_axie, address, secret, nonce=None):
        self.w3 = Web3(Web3.HTTPProvider(RONIN_PROVIDER_FREE))
        self.sire_axie = sire_axie
        self.matron_axie = matron_axie
        self.address = address.replace("ronin:", "0x")
        self.secret = secret
        if not nonce:
            self.nonce = get_nonce(self.address)
        else:
            self.nonce = max(get_nonce(self.address), nonce)

    def execute(self):
        #Prepare transaction
        with open("axie/axie_abi.json") as f:
            axie_abi = json.load(f)
        axie_contract = self.w3.eth.contract(
            address=Web3.toChecksumAddress(AXIE_CONTRACT),
            abi=axie_abi
        )
        # Build transaction
        transaction = axie_contract.functions.breedAxies(
            self.sire_axie,
            self.matron_axie
        ).buildTransaction({
            "chainId": 2020,
            "gas": 500000,
            "gasPrice": self.w3.toWei("0", "gwei"),
            "nonce": self.nonce
        })
        # Sign transaction
        signed = self.w3.eth.account.sign_transaction(
            transaction,
            private_key=self.secret
        )
        # Send raw transaction
        self.w3.eth.send_raw_transaction(signed.rawTransaction)
        # get transaction hash
        hash = self.w3.toHex(self.w3.keccak(signed.rawTransaction))
        # Wait for transaction to finish
        logging.info("{self} about to start!")
        try:
            recepit = self.w3.eth.wait_for_transaction_receipt(hash, timeout=300, poll_latency=5)
        except exceptions.TimeExhausted:
            logging.info("{self}, Transaction could not be processed within 5min, skipping it!")
        
        if recepit['status'] == 1:
            logging.info("Important: {self} completed successfully")
        else:
            logging.info("Important: {self} failed")

    def __str__(self):
        return (f"Breeding axie {self.sire_axie} with {self.matron_axie} in account "
                f"{self.address.replace('0x', 'ronin:')}")
