import json
import subprocess
from time import sleep
from web3 import Web3, exceptions
from axie.utils import get_nonce

TARGET_ADDRESS = "0xcac6cb4a85ba1925f96abc9a302b4a34dbb8c6b0"
ORIGIN_ADDRESS = "0x268bb18f139ee86f3bcdd46841d284e64d7a1716"

SLP_CONTRACT = "0xa8754b9fa15fc18bb59458815510e40a12cd2014"
RONIN_PROVIDER_FREE = "https://proxy.roninchain.com/free-gas-rpc"


w3 = Web3(Web3.HTTPProvider(RONIN_PROVIDER_FREE))
with open("axie/slp_abi.json") as f:
    slb_abi = json.load(f)
slp_contract = w3.eth.contract(
    address=Web3.toChecksumAddress(SLP_CONTRACT),
    abi=slb_abi
)
# Build transaction
transaction = slp_contract.functions.transfer(
    Web3.toChecksumAddress(TARGET_ADDRESS),
    1
).buildTransaction({
    "chainId": 2020,
    "gas": 100000,
    "gasPrice": w3.toWei("0", "gwei"),
    "nonce": get_nonce(ORIGIN_ADDRESS)
})
with open("transaction.json", "w") as tx_f:
    json.dump(transaction, tx_f)
# Trezor signature with CLI
p = subprocess.Popen(["trezorctl", "eth", "sign-tx", "transaction.json"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = p.communicate()
# Get signed transaction
with open("transaction.json", "w") as signed_tx_f:
    signed_tx = json.load(signed_tx_f)

w3.eth.send_raw_transaction(signed_tx.rawTransaction)
hash = w3.toHex(w3.keccak(signed_tx.rawTransaction))
while True:
    try:
        recepit = w3.eth.get_transaction_receipt(hash)
        if recepit["status"] == 1:
            success = True
        else:
            success = False
        break
    except exceptions.TransactionNotFound:
        print(f"Waiting for transaction to finish (Hash:{hash})...")
        # Sleep 5 seconds not to constantly send requests!
        sleep(5)
if success:
    print("Transaction hash: {hash} - Explorer: https://explorer.roninchain.com/tx/{str(hash)}")
else:
    print("FAIL!")