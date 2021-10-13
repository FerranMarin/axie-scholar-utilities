import json
from datetime import datetime, timedelta

from web3 import Web3
import requests

from axie.utils import RONIN_PROVIDER, AXIE_CONTRACT


class Axies:
    def __init__(self, account):
        self.w3 = Web3(Web3.HTTPProvider(RONIN_PROVIDER))
        self.acc = account.replace("ronin:", "0x")
        with open("axie/axie_abi.json") as f:
            axie_abi = json.load(f)
        self.contract = self.w3.eth.contract(
            address=Web3.toChecksumAddress(AXIE_CONTRACT),
            abi=axie_abi
        )
        self.now = datetime.now()

    def number_of_axies(self):
        return self.contract.functions.balanceOf(
            Web3.toChecksumAddress(self.acc)
        ).call()
    
    def find_axies_to_morph(self):
        num_axies = self.number_of_axies()
        axies = []
        for i in range(num_axies):
            axie = self.contract.functions.tokenOfOwnerByIndex(
                _owner=Web3.toChecksumAddress(self.acc),
                _index=i
            ).call()
            morph_date, body_shape = self.get_morph_date_and_body(axie)
            if self.now >= morph_date and not body_shape:
                axies.append(axie)
            elif not body_shape:
                print(f"Axie {axie} cannot be morphed until {morph_date}")
            else:
                print(f"Axie {axie} is already an adult!")
        return axies

    def get_morph_date_and_body(self, axie_id):
        payload = {
            "operationName": "GetAxieDetail",
            "variables":
                {"axieId": axie_id},
            "query": "query GetAxieDetail($axieId: ID!) { axie(axieId: $axieId) "
            "{ ...AxieDetail __typename}} fragment AxieDetail on Axie "
            "{ id birthDate bodyShape __typename }"
        }
        url = "https://graphql-gateway.axieinfinity.com/graphql"
        response = requests.post(url, json=payload)
        # In case we want to check correctly morphed
        body_shape = response.json()["data"]["axie"]["bodyShape"]
        birth_date = response.json()["data"]["axie"]["birthDate"]
        morph_date = datetime.fromtimestamp(birth_date) + timedelta(days=5)        
        return morph_date, body_shape


if __name__ == "__main__":
    a = Axies(
        "ronin:<ronin_acc>"
    )
    print(a.find_axies_to_morph())