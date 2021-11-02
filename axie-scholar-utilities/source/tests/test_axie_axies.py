import builtins
from datetime import date, datetime, timedelta

from mock import patch, call, mock_open
from freezegun import freeze_time
import requests_mock
import pytest

from axie import Axies
from axie.utils import AXIE_CONTRACT


@freeze_time('2021-01-14 01:10:05')
@patch("web3.eth.Eth.contract", return_value="contract")
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("web3.Web3.HTTPProvider", return_value="provider")
def test_axies_init(mocked_provider, mocked_checksum, mocked_contract):
    with patch.object(builtins,
                      "open",
                      mock_open(read_data='{"foo": "bar"}')):
        a = Axies("ronin:abc1")
    mocked_provider.assert_called()
    mocked_checksum.assert_called_with(AXIE_CONTRACT)
    mocked_contract.assert_called_with(address="checksum", abi={"foo": "bar"})
    assert a.acc == "0xabc1"
    assert a.now == datetime(2021, 1, 14, 1, 10, 5)
    assert a.contract == "contract"


@patch("axie.axies.check_balance", return_value=100)
@patch("web3.eth.Eth.contract")
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
def test_number_of_axies(mocked_checksum, mocked_contract, mocked_balance_of):
    with patch.object(builtins,
                      "open",
                      mock_open(read_data='{"foo": "bar"}')):
        a = Axies("ronin:abc1")
    number = a.number_of_axies()
    assert number == 100
    mocked_balance_of.assert_called_with(a.acc, 'axies')
    mocked_checksum.assert_called_with(AXIE_CONTRACT)
    mocked_contract.assert_called_with(address="checksum", abi={"foo": "bar"})


@patch("web3.eth.Eth.contract.functions.tokenOfOwnerByIndex")
@patch("web3.eth.Eth.contract")
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("axie.Axies.number_of_axies", return_value=5)
def test_get_axies(mocked_number_of_axies, mocked_checksum, mocked_contract, _):
    with patch.object(builtins,
                      "open",
                      mock_open(read_data='{"foo": "bar"}')):
        a = Axies("ronin:abc1")
    axies = a.get_axies()
    mocked_contract.assert_called_with(address="checksum", abi={"foo": "bar"})
    mocked_number_of_axies.assert_called()
    mocked_checksum.assert_has_calls(calls=[
        call(AXIE_CONTRACT), call(a.acc)
    ])
    assert len(axies) == 5


@freeze_time('2021-01-14 01:10:05')
@patch("web3.eth.Eth.contract.functions.tokenOfOwnerByIndex")
@patch("axie.Axies.get_morph_date_and_body", return_value=(None, None))
@patch("web3.eth.Eth.contract")
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("axie.Axies.number_of_axies", return_value=1)
def test_find_axies_to_morph_none_morph_date_shape(mocked_number_of_axies,
                                                   mocked_checksum,
                                                   mocked_contract,
                                                   mocked_get_data,
                                                   _):
    with patch.object(builtins,
                      "open",
                      mock_open(read_data='{"foo": "bar"}')):
        a = Axies("ronin:abc1")
    axies_to_morph = a.find_axies_to_morph()
    mocked_contract.assert_called_with(address="checksum", abi={"foo": "bar"})
    mocked_number_of_axies.assert_called()
    mocked_checksum.assert_has_calls(calls=[
        call(AXIE_CONTRACT), call(a.acc)
    ])
    mocked_get_data.assert_called()
    assert axies_to_morph == []


@freeze_time('2021-01-14 01:10:05')
@patch("web3.eth.Eth.contract.functions.tokenOfOwnerByIndex")
@patch("axie.Axies.get_morph_date_and_body", return_value=(datetime(2021, 1, 14, 1, 0, 0), "Normal"))
@patch("web3.eth.Eth.contract")
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("axie.Axies.number_of_axies", return_value=1)
def test_find_axies_to_morph_already_adult(mocked_number_of_axies,
                                           mocked_checksum,
                                           mocked_contract,
                                           mocked_get_data,
                                           _):
    with patch.object(builtins,
                      "open",
                      mock_open(read_data='{"foo": "bar"}')):
        a = Axies("ronin:abc1")
    axies_to_morph = a.find_axies_to_morph()
    mocked_contract.assert_called_with(address="checksum", abi={"foo": "bar"})
    mocked_number_of_axies.assert_called()
    mocked_checksum.assert_has_calls(calls=[
        call(AXIE_CONTRACT), call(a.acc)
    ])
    mocked_get_data.assert_called()
    assert axies_to_morph == []


@freeze_time('2021-01-14 01:10:05')
@patch("web3.eth.Eth.contract.functions.tokenOfOwnerByIndex")
@patch("axie.Axies.get_morph_date_and_body", return_value=(datetime(2021, 1, 14, 1, 10, 5)+timedelta(days=2), None))
@patch("web3.eth.Eth.contract")
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("axie.Axies.number_of_axies", return_value=1)
def test_find_axies_to_morph_not_hatch_time(mocked_number_of_axies,
                                            mocked_checksum,
                                            mocked_contract,
                                            mocked_get_data,
                                            _):
    with patch.object(builtins,
                      "open",
                      mock_open(read_data='{"foo": "bar"}')):
        a = Axies("ronin:abc1")
    axies_to_morph = a.find_axies_to_morph()
    mocked_contract.assert_called_with(address="checksum", abi={"foo": "bar"})
    mocked_number_of_axies.assert_called()
    mocked_checksum.assert_has_calls(calls=[
        call(AXIE_CONTRACT), call(a.acc)
    ])
    mocked_get_data.assert_called()
    assert axies_to_morph == []


@patch("web3.eth.Eth.contract.functions.tokenOfOwnerByIndex")
@patch("axie.Axies.get_morph_date_and_body", return_value=(datetime(2021, 1, 14, 0, 0, 0), None))
@patch("web3.eth.Eth.contract")
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("axie.Axies.number_of_axies", return_value=1)
@freeze_time('2021-01-14 01:10:05')
def test_find_axies_to_morph(mocked_number_of_axies,
                             mocked_checksum,
                             mocked_contract,
                             mocked_get_data,
                             _):
    with patch.object(builtins,
                      "open",
                      mock_open(read_data='{"foo": "bar"}')):
        a = Axies("ronin:abc1")
    axies_to_morph = a.find_axies_to_morph()
    mocked_contract.assert_called_with(address="checksum", abi={"foo": "bar"})
    mocked_number_of_axies.assert_called()
    mocked_checksum.assert_has_calls(calls=[
        call(AXIE_CONTRACT), call(a.acc)
    ])
    mocked_get_data.assert_called()
    assert len(axies_to_morph) == 1


@freeze_time('2021-01-14 01:10:05')
def test_get_morph_date_body():
    birth_date = datetime.timestamp(datetime.now())
    morph_date = datetime.fromtimestamp(birth_date) + timedelta(days=5)
    body_shape = "foo"
    with requests_mock.Mocker() as req_mocker:
        req_mocker.post("https://graphql-gateway.axieinfinity.com/graphql",
                        json={"data": {"axie": {"bodyShape": body_shape, "birthDate": birth_date}}})
        a = Axies("ronin:abc1")
        resp = a.get_morph_date_and_body(123)
    
    assert resp == (morph_date, body_shape)


@freeze_time('2021-01-14 01:10:05')
def test_get_morph_date_body_no_json():
    with requests_mock.Mocker() as req_mocker:
        req_mocker.post("https://graphql-gateway.axieinfinity.com/graphql")
        a = Axies("ronin:abc1")
        resp = a.get_morph_date_and_body(123)
    
    assert resp == (None, None)


@pytest.mark.parametrize("mocked_json", [
    ({}),
    ({"foo": "bar"}),
    ({"data": {"foo": "bar"}}),
    ({"data": {"axie": "bar"}}),
    ({"data": {"axie": {"bar": "foo"}}}),
    ({"data": {"axie": {"bodyShape": "foo"}}}),
    ({"data": {"axie": {"birthDate": "foo"}}})
])
@freeze_time('2021-01-14 01:10:05')
def test_get_morph_date_body_malformed_json(mocked_json):
    with requests_mock.Mocker() as req_mocker:
        req_mocker.post("https://graphql-gateway.axieinfinity.com/graphql", json=mocked_json)
        a = Axies("ronin:abc1")
        resp = a.get_morph_date_and_body(123)
    
    assert resp == (None, None)
