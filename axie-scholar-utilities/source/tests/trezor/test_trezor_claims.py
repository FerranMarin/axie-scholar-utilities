import sys
import json
import builtins
from glob import glob
from datetime import datetime, timedelta

import pytest
from mock import patch, mock_open, call
import requests_mock
from hexbytes import HexBytes

from trezor import TrezorAxieClaimsManager
from trezor.trezor_claims import TrezorClaim
from axie.utils import SLP_CONTRACT, RONIN_PROVIDER_FREE, USER_AGENT
from tests.test_utils import async_cleanup_log_file, LOG_FILE_PATH, MockedSignedMsg


@patch("trezor.TrezorAxieClaimsManager.load_trezor_config_and_acc_name", return_value=("foo", "bar"))
def test_claims_manager_init(mocked_load_secrets_and_acc_name):
    config_file = "config_file.json"
    payments_file = "payments_file.json"
    tacm = TrezorAxieClaimsManager(payments_file, config_file)
    mocked_load_secrets_and_acc_name.assert_called_with(config_file, payments_file)
    assert tacm.trezor_config == "foo"
    assert tacm.acc_names == "bar"


def test_claims_manager_verify_input_success(tmpdir):
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*4)
    p_file = tmpdir.join("p.json")
    data = {
        "Manager": "ronin:<Manager address here>",
        "Scholars": [
            {
                "Name": "Scholar 1",
                "AccountAddress": f"{scholar_acc}",
                "ScholarPayoutAddress": "ronin:<scholar_address>",
                "ScholarPayout": 100,
                "TrainerPayoutAddress": "ronin:<trainer_address>",
                "TrainerPayout": 10,
                "ManagerPayout": 90
            }]
    }
    p_file.write(json.dumps(data))
    c_file = tmpdir.join("s.json")
    config_data = {scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    c_file.write(json.dumps(config_data))
    axc = TrezorAxieClaimsManager(p_file, c_file)
    axc.verify_inputs()
    assert axc.trezor_config == config_data
    assert axc.acc_names == {scholar_acc: "Scholar 1"}


def test_claims_manager_verify_only_accounts_in_payments_get_claimed(tmpdir):
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*4)
    p_file = tmpdir.join("p.json")
    data = {
        "Manager": "ronin:<Manager address here>",
        "Scholars": [
            {
                "Name": "Scholar 1",
                "AccountAddress": f"{scholar_acc}",
                "ScholarPayoutAddress": "ronin:<scholar_address>",
                "ScholarPayout": 100,
                "TrainerPayoutAddress": "ronin:<trainer_address>",
                "TrainerPayout": 10,
                "ManagerPayout": 90
            }]
    }
    p_file.write(json.dumps(data))
    c_file = tmpdir.join("s.json")
    config_data = {
        scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"},
        "ronin:abc1": {"passphrase": "", "bip_path": "m/44'/60'/0'/0/1"}
    }
    c_file.write(json.dumps(config_data))
    axc = TrezorAxieClaimsManager(p_file, c_file)
    axc.verify_inputs()
    assert axc.trezor_config == {scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    assert axc.acc_names == {scholar_acc: "Scholar 1"}


def test_claims_manager_verify_inputs_wrong_public_ronin(tmpdir, caplog):
    scholar_acc = '<account_s1_address>' + "".join([str(x) for x in range(10)]*4)
    p_file = tmpdir.join("p.json")
    data = {
        "Manager": "ronin:<Manager address here>",
        "Scholars": [
            {
                "Name": "Scholar 1",
                "AccountAddress": f"{scholar_acc}",
                "ScholarPayoutAddress": "ronin:<scholar_address>",
                "ScholarPayout": 100,
                "TrainerPayoutAddress": "ronin:<trainer_address>",
                "TrainerPayout": 10,
                "ManagerPayout": 90
            }]
    }
    p_file.write(json.dumps(data))
    c_file = tmpdir.join("s.json")
    config_data = {scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    c_file.write(json.dumps(config_data))
    with patch.object(sys, "exit") as mocked_sys:
        axc = TrezorAxieClaimsManager(p_file, c_file)
        axc.verify_inputs()

    mocked_sys.assert_called_once()
    assert f"Public address {scholar_acc} needs to start with ronin:" in caplog.text


@patch("trezor.trezor_claims.get_default_client", return_value="client")
@patch("trezor.trezor_claims.TrezorClaim.execute")
def test_claims_manager_prepare_claims(mocked_claim_execute, mock_client, tmpdir):
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*4)
    p_file = tmpdir.join("p.json")
    data = {
        "Manager": "ronin:<Manager address here>",
        "Scholars": [
            {
                "Name": "Scholar 1",
                "AccountAddress": f"{scholar_acc}",
                "ScholarPayoutAddress": "ronin:<scholar_address>",
                "ScholarPayout": 100,
                "TrainerPayoutAddress": "ronin:<trainer_address>",
                "TrainerPayout": 10,
                "ManagerPayout": 90
            }]
    }
    p_file.write(json.dumps(data))
    c_file = tmpdir.join("s.json")
    config_data = {scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    c_file.write(json.dumps(config_data))
    axc = TrezorAxieClaimsManager(p_file, c_file)
    axc.prepare_claims()
    mocked_claim_execute.assert_called_once()
    mock_client.assert_called()


@patch("trezor.trezor_utils.parse_path", return_value="parsed_path")
@patch("web3.eth.Eth.contract")
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("web3.Web3.HTTPProvider", return_value="provider")
def test_claim_init(mocked_provider, mocked_checksum, mocked_contract, mocked_parse):
    with patch.object(builtins,
                      "open",
                      mock_open(read_data='{"foo": "bar"}')):
        c = TrezorClaim(account="ronin:foo", acc_name="test_acc", bip_path="m/44'/60'/0'/0/0", client="client")
    mocked_provider.assert_called_with(
        RONIN_PROVIDER_FREE,
        request_kwargs={"headers":{"content-type":"application/json","user-agent": USER_AGENT}}
    )
    mocked_checksum.assert_called_with(SLP_CONTRACT)
    mocked_contract.assert_called_with(address="checksum", abi={"foo": "bar"})
    mocked_parse.assert_called_with("m/44'/60'/0'/0/0")
    assert c.bip_path == "parsed_path"
    assert c.client == "client"
    assert c.account == "0xfoo"
    assert c.acc_name == "test_acc"


@patch("trezor.trezor_utils.parse_path", return_value="parsed_path")
@patch("web3.eth.Eth.contract")
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("web3.Web3.HTTPProvider", return_value="provider")
def test_has_unclaimed_slp(mocked_provider, mocked_checksum, mocked_contract, mocked_parse):
    last_claimed_date = datetime.now() - timedelta(days=15)
    with requests_mock.Mocker() as req_mocker:
        req_mocker.get("https://game-api.skymavis.com/game-api/clients/0xfoo/items/1",
                       json={"total": 12,
                             "last_claimed_item_at": round(last_claimed_date.timestamp()),
                             "claimable_total": 0})
        with patch.object(builtins,
                          "open",
                          mock_open(read_data='{"foo": "bar"}')):
            c = TrezorClaim(account="ronin:foo", acc_name="test_acc", bip_path="m/44'/60'/0'/0/0", client="client")
            unclaimed = c.has_unclaimed_slp()
            assert unclaimed == 12
        mocked_parse.assert_called_with("m/44'/60'/0'/0/0")
        mocked_provider.assert_called_with(
            RONIN_PROVIDER_FREE,
            request_kwargs={"headers":{"content-type":"application/json","user-agent": USER_AGENT}}
        )
        mocked_checksum.assert_called_with(SLP_CONTRACT)
        mocked_contract.assert_called_with(address="checksum", abi={"foo": "bar"})


@patch("trezor.trezor_utils.parse_path", return_value="parsed_path")
@patch("web3.eth.Eth.contract")
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("web3.Web3.HTTPProvider", return_value="provider")
def test_has_unclaimed_slp_failed_req(mocked_provider, mocked_checksum, mocked_contract, mocked_parse):
    with requests_mock.Mocker() as req_mocker:
        req_mocker.get("https://game-api.skymavis.com/game-api/clients/0xfoo/items/1",
                       status_code=500)
        with patch.object(builtins,
                          "open",
                          mock_open(read_data='{"foo": "bar"}')):
            c = TrezorClaim(account="ronin:foo", acc_name="test_acc", bip_path="m/44'/60'/0'/0/0", client="client")
            unclaimed = c.has_unclaimed_slp()
            assert unclaimed is None
        mocked_parse.assert_called_with("m/44'/60'/0'/0/0")
        mocked_provider.assert_called_with(
            RONIN_PROVIDER_FREE,
            request_kwargs={"headers":{"content-type":"application/json","user-agent": USER_AGENT}}
        )
        mocked_checksum.assert_called_with(SLP_CONTRACT)
        mocked_contract.assert_called_with(address="checksum", abi={"foo": "bar"})


@patch("trezor.trezor_utils.parse_path", return_value="parsed_path")
def test_create_random_msg(mocked_parse):
    with requests_mock.Mocker() as req_mocker:
        req_mocker.post("https://graphql-gateway.axieinfinity.com/graphql",
                        json={"data": {"createRandomMessage": "random_msg"}})
        resp = TrezorClaim(account="ronin:foo", acc_name="test_acc", bip_path="m/44'/60'/0'/0/0", client="client").create_random_msg()
        assert resp == "random_msg"
    mocked_parse.assert_called_with("m/44'/60'/0'/0/0")

@patch("trezor.trezor_utils.parse_path", return_value="parsed_path")
def test_create_random_msg_fail_req(mocked_parse):
    with requests_mock.Mocker() as req_mocker:
        req_mocker.post("https://graphql-gateway.axieinfinity.com/graphql",
                        status_code=500)
        c = TrezorClaim(account="ronin:foo", acc_name="test_acc", bip_path="m/44'/60'/0'/0/0", client="client")
        random_msg = c.create_random_msg()
        assert random_msg is None
    mocked_parse.assert_called_with("m/44'/60'/0'/0/0")


@patch("trezor.trezor_utils.parse_path", return_value="parsed_path")
@patch("web3.eth.Eth.contract")
@patch("trezor.trezor_claims.ethereum.sign_message", return_value=MockedSignedMsg())
@patch("trezor.trezor_claims.TrezorClaim.create_random_msg", return_value="random_msg")
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("web3.Web3.HTTPProvider", return_value="provider")
def test_get_jwt(mocked_provider, mocked_checksum, mocked_random_msg, mock_sign_message, _, mocked_parse):
    with requests_mock.Mocker() as req_mocker:
        req_mocker.post("https://graphql-gateway.axieinfinity.com/graphql",
                        json={"data": {"createAccessTokenWithSignature": {"accessToken": "test-token"}}})
        c = TrezorClaim(account="ronin:foo", acc_name="test_acc", bip_path="m/44'/60'/0'/0/0", client="client")
        resp = c.get_jwt()
        assert resp == "test-token"
        expected_payload = {
             "operationName": "CreateAccessTokenWithSignature",
             "variables": {
                "input": {
                    "mainnet": "ronin",
                    "owner": "0xfoo",
                    "message": "random_msg",
                    "signature": f"{HexBytes(b'123').hex()}"
                }
             },
             "query": "mutation CreateAccessTokenWithSignature($input: SignatureInput!)"
             "{createAccessTokenWithSignature(input: $input) "
             "{newAccount result accessToken __typename}}"
        }
        assert req_mocker.request_history[0].json() == expected_payload
    mocked_parse.assert_called_with("m/44'/60'/0'/0/0")
    mocked_provider.assert_called_with(
        RONIN_PROVIDER_FREE,
        request_kwargs={"headers":{"content-type":"application/json","user-agent": USER_AGENT}}
    )
    mocked_checksum.assert_called_with(SLP_CONTRACT)
    mocked_random_msg.assert_called_once()
    mock_sign_message.assert_called()


@patch("trezor.trezor_utils.parse_path", return_value="parsed_path")
@patch("web3.eth.Eth.contract")
@patch("trezor.trezor_claims.ethereum.sign_message", return_value=MockedSignedMsg())
@patch("trezor.trezor_claims.TrezorClaim.create_random_msg", return_value="random_msg")
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("web3.Web3.HTTPProvider", return_value="provider")
def test_get_jwt_fail_req(mocked_provider, mocked_checksum, mocked_random_msg, mock_sign_message, _, mocked_parse):
    with requests_mock.Mocker() as req_mocker:
        req_mocker.post("https://graphql-gateway.axieinfinity.com/graphql",
                        status_code=500)
        c = TrezorClaim(account="ronin:foo", acc_name="test_acc", bip_path="m/44'/60'/0'/0/0", client="client")
        jwt = c.get_jwt()
        assert jwt is None
        mocked_parse.assert_called_with("m/44'/60'/0'/0/0")
        mocked_provider.assert_called_with(
            RONIN_PROVIDER_FREE,
            request_kwargs={"headers":{"content-type":"application/json","user-agent": USER_AGENT}}
        )
        mocked_checksum.assert_called_with(SLP_CONTRACT)
        mocked_random_msg.assert_called_once()
        mock_sign_message.assert_called()
        expected_payload = {
            "operationName": "CreateAccessTokenWithSignature",
            "variables": {
                "input": {
                    "mainnet": "ronin",
                    "owner": "0xfoo",
                    "message": "random_msg",
                    "signature": f"{HexBytes(b'123').hex()}"
                }
            },
            "query": "mutation CreateAccessTokenWithSignature($input: SignatureInput!)"
            "{createAccessTokenWithSignature(input: $input) "
            "{newAccount result accessToken __typename}}"
        }
        assert req_mocker.request_history[0].json() == expected_payload


@patch("trezor.trezor_utils.parse_path", return_value="parsed_path")
@patch("web3.eth.Eth.contract")
@patch("trezor.trezor_claims.ethereum.sign_message", return_value=MockedSignedMsg())
@patch("trezor.trezor_claims.TrezorClaim.create_random_msg", return_value="random_msg")
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("web3.Web3.HTTPProvider", return_value="provider")
def test_jwq_fail_req_content(mocked_provider, mocked_checksum, mocked_random_msg, mock_sign_message, _, mocked_parse):
    with requests_mock.Mocker() as req_mocker:
        req_mocker.post("https://graphql-gateway.axieinfinity.com/graphql", json={"data": {}})
        c = TrezorClaim(account="ronin:foo", acc_name="test_acc", bip_path="m/44'/60'/0'/0/0", client="client")
        jwt = c.get_jwt()
        expected_payload = {
            "operationName": "CreateAccessTokenWithSignature",
            "variables": {
                "input": {
                    "mainnet": "ronin",
                    "owner": "0xfoo",
                    "message": "random_msg",
                    "signature": f"{HexBytes(b'123').hex()}"
                }
            },
            "query": "mutation CreateAccessTokenWithSignature($input: SignatureInput!)"
            "{createAccessTokenWithSignature(input: $input) "
            "{newAccount result accessToken __typename}}"
        }
        assert jwt is None
        mocked_parse.assert_called_with("m/44'/60'/0'/0/0")
        assert req_mocker.request_history[0].json() == expected_payload
        mocked_provider.assert_called_with(
            RONIN_PROVIDER_FREE,
            request_kwargs={"headers":{"content-type":"application/json","user-agent": USER_AGENT}}
        )
        mocked_checksum.assert_called_with(SLP_CONTRACT)
        mocked_random_msg.assert_called_once()
        mock_sign_message.assert_called()


@patch("trezor.trezor_utils.parse_path", return_value="parsed_path")
@patch("web3.eth.Eth.contract")
@patch("trezor.trezor_claims.ethereum.sign_message", return_value=MockedSignedMsg())
@patch("trezor.trezor_claims.TrezorClaim.create_random_msg", return_value="random_msg")
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("web3.Web3.HTTPProvider", return_value="provider")
def test_jwq_fail_req_content_2(mocked_provider, mocked_checksum, mocked_random_msg, mock_sign_message, _, mocked_parse):
    with requests_mock.Mocker() as req_mocker:
        req_mocker.post("https://graphql-gateway.axieinfinity.com/graphql",
                        json={"data": {"createAccessTokenWithSignature": {}}})
        c = TrezorClaim(account="ronin:foo", acc_name="test_acc", bip_path="m/44'/60'/0'/0/0", client="client")
        jwt = c.get_jwt()
        expected_payload = {
            "operationName": "CreateAccessTokenWithSignature",
            "variables": {
                "input": {
                    "mainnet": "ronin",
                    "owner": "0xfoo",
                    "message": "random_msg",
                    "signature": f"{HexBytes(b'123').hex()}"
                }
            },
            "query": "mutation CreateAccessTokenWithSignature($input: SignatureInput!)"
            "{createAccessTokenWithSignature(input: $input) "
            "{newAccount result accessToken __typename}}"
        }
        assert req_mocker.request_history[0].json() == expected_payload
        assert jwt is None
        mocked_parse.assert_called_with("m/44'/60'/0'/0/0")
        mocked_provider.assert_called_with(
            RONIN_PROVIDER_FREE,
            request_kwargs={"headers":{"content-type":"application/json","user-agent": USER_AGENT}}
        )
        mocked_checksum.assert_called_with(SLP_CONTRACT)
        mocked_random_msg.assert_called_once()
        mock_sign_message.assert_called()


@pytest.mark.asyncio
@patch("trezor.trezor_utils.parse_path", return_value="parsed_path")
@patch("trezor.trezor_claims.rlp.encode")
@patch("web3.Web3.toBytes")
@patch("web3.Web3.toHex", return_value="transaction_hash")
@patch("web3.Web3.keccak", return_value='result_of_keccak')
@patch("web3.eth.Eth.get_transaction_receipt", return_value={'status': 1})
@patch("web3.eth.Eth.send_raw_transaction", return_value="raw_tx")
@patch('trezor.trezor_claims.ethereum.sign_tx')
@patch("trezor.trezor_claims.get_nonce", return_value=1)
@patch("trezor.trezor_claims.TrezorClaim.get_jwt", return_value="token")
@patch("trezor.trezor_claims.TrezorClaim.has_unclaimed_slp", return_value=456)
@patch("trezor.trezor_claims.check_balance", return_value=123)
@patch("web3.eth.Eth.contract")
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("web3.Web3.HTTPProvider", return_value="provider")
async def test_claim_execution(mocked_provider,
                               mocked_checksum,
                               mocked_contract,
                               moocked_check_balance,
                               mocked_unclaimed_slp,
                               mock_get_jwt,
                               mock_get_nonce,
                               mocked_sign_transaction,
                               mock_raw_send,
                               mock_receipt,
                               mock_keccak,
                               mock_to_hex,
                               mocked_to_bytes,
                               mock_rlp,
                               mocked_parse,
                               caplog):
    # Make sure file is clean to start
    log_file= glob(LOG_FILE_PATH+'logs/results_*.log')[0][9:]
    await async_cleanup_log_file(log_file)
    with patch.object(builtins,
                      "open",
                      mock_open(read_data='{"foo": "bar"}')):
        with requests_mock.Mocker() as req_mocker:
            req_mocker.post(
                "https://game-api.skymavis.com/game-api/clients/0xfoo/items/1/claim",
                json={
                    "blockchain_related": {
                        "signature": {
                            "amount": "456",
                            "timestamp": str(int(datetime.now().timestamp())),
                            "signature": "0xsignature"
                        }
                    }
                }
            )
            c = TrezorClaim(account="ronin:foo", acc_name="test_acc", bip_path="m/44'/60'/0'/0/0", client="client")
            await c.execute()
    mocked_provider.assert_called_with(
        RONIN_PROVIDER_FREE,
        request_kwargs={"headers":{"content-type":"application/json","user-agent": USER_AGENT}}
    )
    mocked_to_bytes.assert_called()
    mock_rlp.assert_called()
    mocked_checksum.assert_has_calls([call(SLP_CONTRACT), call("0xfoo")])
    mocked_contract.assert_called_with(address="checksum", abi={"foo": "bar"})
    moocked_check_balance.assert_called_with("0xfoo")
    mocked_unclaimed_slp.assert_called_once()
    mocked_parse.assert_called_with("m/44'/60'/0'/0/0")
    assert c.bip_path == "parsed_path"
    assert c.client == "client"
    assert c.account == "0xfoo"
    mock_get_jwt.assert_called_once()
    mock_get_nonce.assert_called_with("0xfoo")
    mocked_sign_transaction.assert_called_once()
    mock_raw_send.assert_called_once()
    mock_receipt.assert_called_with("transaction_hash")
    mock_keccak.assert_called_once()
    mock_to_hex.assert_called_with("result_of_keccak")
    assert "Account test_acc (ronin:foo) has 456 unclaimed SLP" in caplog.text
    assert "SLP Claimed! New balance for account test_acc (ronin:foo) is: 123" in caplog.text
    with open(log_file) as f:
        lf = f.readlines()
        assert len(lf) == 1
    assert "Important: SLP Claimed! New balance for account test_acc (ronin:foo) is: 123" in lf[0]
    await async_cleanup_log_file(log_file)


@pytest.mark.asyncio
@patch("trezor.trezor_utils.parse_path", return_value="parsed_path")
@patch("trezor.trezor_claims.rlp.encode")
@patch("web3.Web3.toBytes")
@patch("web3.Web3.toHex", return_value="transaction_hash")
@patch("web3.Web3.keccak", return_value='result_of_keccak')
@patch("web3.eth.Eth.get_transaction_receipt", return_value={'status': 1})
@patch("web3.eth.Eth.send_raw_transaction", return_value="raw_tx")
@patch('trezor.trezor_claims.ethereum.sign_tx')
@patch("trezor.trezor_claims.get_nonce", return_value=1)
@patch("trezor.trezor_claims.TrezorClaim.get_jwt", return_value="token")
@patch("trezor.trezor_claims.TrezorClaim.has_unclaimed_slp", return_value=456)
@patch("trezor.trezor_claims.check_balance", return_value=123)
@patch("web3.eth.Eth.contract")
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("web3.Web3.HTTPProvider", return_value="provider")
async def test_execution_failed_get_blockchain(mocked_provider,
                                               mocked_checksum,
                                               mocked_contract,
                                               moocked_check_balance,
                                               mocked_unclaimed_slp,
                                               mock_get_jwt,
                                               mock_get_nonce,
                                               mocked_sign_transaction,
                                               mock_raw_send,
                                               mock_receipt,
                                               mock_keccak,
                                               mock_to_hex,
                                               mocked_to_bytes,
                                               mock_rlp,
                                               mocked_parse):
    with patch.object(builtins,
                      "open",
                      mock_open(read_data='{"foo": "bar"}')):
        with requests_mock.Mocker() as req_mocker:
            req_mocker.post(
                "https://game-api.skymavis.com/game-api/clients/0xfoo/items/1/claim",
                json={
                    "blockchain_related": {
                        "signature": {
                            "amount": "",
                            "timestamp": 0,
                            "signature": ""
                        }
                    }
                }
            )
            c = TrezorClaim(account="ronin:foo", acc_name="test_acc", bip_path="m/44'/60'/0'/0/0", client="client")
            await c.execute()
        mocked_provider.assert_called_with(
            RONIN_PROVIDER_FREE,
            request_kwargs={"headers":{"content-type":"application/json","user-agent": USER_AGENT}}
        )
        mocked_checksum.assert_called_with('0xa8754b9fa15fc18bb59458815510e40a12cd2014')
        mocked_contract.assert_called_with(address="checksum", abi={"foo": "bar"})
        moocked_check_balance.assert_not_called()
        mocked_unclaimed_slp.assert_called_once()
        mocked_parse.assert_called_with("m/44'/60'/0'/0/0")
        assert c.bip_path == "parsed_path"
        assert c.client == "client"
        assert c.account == "0xfoo"
        mock_get_jwt.assert_called_once()
        mock_get_nonce.assert_not_called()
        mocked_sign_transaction.assert_not_called()
        mock_raw_send.assert_not_called()
        mock_receipt.assert_not_called()
        mock_keccak.assert_not_called()
        mock_to_hex.assert_not_called()
        mock_rlp.assert_not_called()
        mocked_to_bytes.assert_not_called()
