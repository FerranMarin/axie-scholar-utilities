import sys
import json
import builtins
from datetime import datetime, timedelta

import pytest
from mock import patch, mock_open, call
import requests_mock
from hexbytes import HexBytes
from eth_account.messages import encode_defunct

from axie import AxieClaimsManager
from axie.claims import Claim, RONIN_PROVIDER_FREE, SLP_CONTRACT
from tests.test_utils import LOG_FILE_PATH, cleanup_log_file


@patch("axie.AxieClaimsManager.load_secrets")
def test_claims_manager_init(mocked_load_secrets):
    secrets_file = "sample_secrets_file.json"
    payments_file = "sample_payments_file.json"
    AxieClaimsManager(payments_file, secrets_file)
    mocked_load_secrets.assert_called_with(secrets_file, payments_file)


def test_claims_manager_verify_input_success(tmpdir):
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*4)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
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
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    axc = AxieClaimsManager(p_file, s_file)
    axc.verify_inputs()
    axc.secrets_file = {scholar_acc: scholar_private_acc}


def test_claims_manager_verify_only_accounts_in_payments_get_claimed(tmpdir):
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*4)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
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
    s_file = tmpdir.join("s.json")
    s_data = {
        scholar_acc: scholar_private_acc,
        "ronin:acc": "ronin:secret"
    }
    s_file.write(json.dumps(s_data))
    axc = AxieClaimsManager(p_file, s_file)
    axc.verify_inputs()
    axc.secrets_file = {scholar_acc: scholar_private_acc}


def test_claims_manager_verify_inputs_wrong_public_ronin(tmpdir, caplog):
    scholar_acc = '<account_s1_address>' + "".join([str(x) for x in range(10)]*4)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
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
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    with patch.object(sys, "exit") as mocked_sys:
        axc = AxieClaimsManager(p_file, s_file)
        axc.verify_inputs()

    mocked_sys.assert_called_once()
    assert f"Public address {scholar_acc} needs to start with ronin:" in caplog.text


def test_claims_manager_verify_input_wrong_public_private_ronin(tmpdir, caplog):
    scholar_acc = '<account_s1_address>' + "".join([str(x) for x in range(10)]*4)
    scholar_private_acc = 'ronin:<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
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
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    with patch.object(sys, "exit") as mocked_sys:
        axc = AxieClaimsManager(p_file, s_file)
        axc.verify_inputs()

    mocked_sys.assert_called_once()
    assert f"Private key for account {scholar_acc} is not valid, please review it!" in caplog.text


def test_claims_manager_verify_input_wrong_public_private_short(tmpdir, caplog):
    scholar_acc = '<account_s1_address>' + "".join([str(x) for x in range(10)]*4)
    scholar_private_acc = 'ronin:<account_s1_private_address>012345'
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
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    with patch.object(sys, "exit") as mocked_sys:
        axc = AxieClaimsManager(p_file, s_file)
        axc.verify_inputs()

    mocked_sys.assert_called_once()
    assert f"Private key for account {scholar_acc} is not valid, please review it!" in caplog.text


@patch("axie.claims.Claim.execute")
def test_claims_manager_prepare_claims(mocked_claim_execute, tmpdir):
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*4)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
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
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    axc = AxieClaimsManager(p_file, s_file)
    axc.prepare_claims()
    mocked_claim_execute.assert_called_once()


@patch("web3.eth.Eth.contract")
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("web3.Web3.HTTPProvider", return_value="provider")
def test_claim_init(mocked_provider, mocked_checksum, mocked_contract):
    with patch.object(builtins,
                      "open",
                      mock_open(read_data='{"foo": "bar"}')):
        c = Claim("ronin:foo", "bar")
    mocked_provider.assert_called_with(RONIN_PROVIDER_FREE)
    mocked_checksum.assert_called_with(SLP_CONTRACT)
    mocked_contract.assert_called_with(address="checksum", abi={"foo": "bar"})
    assert c.private_key == "bar"
    assert c.account == "0xfoo"


@patch("web3.eth.Eth.contract")
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("web3.Web3.HTTPProvider", return_value="provider")
def test_has_unclaimed_slp(mocked_provider, mocked_checksum, mocked_contract):
    last_claimed_date = datetime.now() - timedelta(days=15)
    with requests_mock.Mocker() as req_mocker:
        req_mocker.get("https://game-api.skymavis.com/game-api/clients/0xfoo/items/1",
                       json={"total": 12,
                             "last_claimed_item_at": round(last_claimed_date.timestamp()),
                             "claimable_total": 0})
        with patch.object(builtins,
                          "open",
                          mock_open(read_data='{"foo": "bar"}')):
            c = Claim("ronin:foo", "0xbar")
            unclaimed = c.has_unclaimed_slp()
            assert unclaimed == 12
        mocked_provider.assert_called_with(RONIN_PROVIDER_FREE)
        mocked_checksum.assert_called_with(SLP_CONTRACT)
        mocked_contract.assert_called_with(address="checksum", abi={"foo": "bar"})


@patch("web3.eth.Eth.contract")
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("web3.Web3.HTTPProvider", return_value="provider")
def test_has_unclaimed_slp_failed_req(mocked_provider, mocked_checksum, mocked_contract, caplog):
    with requests_mock.Mocker() as req_mocker:
        req_mocker.get("https://game-api.skymavis.com/game-api/clients/0xfoo/items/1",
                       status_code=500)
        with patch.object(builtins,
                          "open",
                          mock_open(read_data='{"foo": "bar"}')):
            c = Claim("ronin:foo", "0xbar")
            unclaimed = c.has_unclaimed_slp()
            assert unclaimed is None
            assert "Failed to check if there is unclaimed SLP" in caplog.text
        mocked_provider.assert_called_with(RONIN_PROVIDER_FREE)
        mocked_checksum.assert_called_with(SLP_CONTRACT)
        mocked_contract.assert_called_with(address="checksum", abi={"foo": "bar"})


def test_create_random_msg():
    with requests_mock.Mocker() as req_mocker:
        req_mocker.post("https://graphql-gateway.axieinfinity.com/graphql",
                        json={"data": {"createRandomMessage": "random_msg"}})
        resp = Claim("ronin:foo", "0xbar").create_random_msg()
        assert resp == "random_msg"


def test_create_random_msg_fail_req():
    with requests_mock.Mocker() as req_mocker:
        req_mocker.post("https://graphql-gateway.axieinfinity.com/graphql",
                        status_code=500)
        with pytest.raises(Exception) as ex:
            Claim("ronin:foo", "0xbar").create_random_msg()
        assert str(ex.value) == ("Error! Creating random msg! "
                                 "Error: 500 Server Error: None for url: "
                                 "https://graphql-gateway.axieinfinity.com/graphql")


@patch("web3.eth.Eth.contract")
@patch("web3.eth.Eth.account.sign_message", return_value={"signature": HexBytes(b"123")})
@patch("axie.claims.Claim.create_random_msg", return_value="random_msg")
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("web3.Web3.HTTPProvider", return_value="provider")
def test_get_jwt(mocked_provider, mocked_checksum, mocked_random_msg, mock_sign_message, _):
    with requests_mock.Mocker() as req_mocker:
        req_mocker.post("https://graphql-gateway.axieinfinity.com/graphql",
                        json={"data": {"createAccessTokenWithSignature": {"accessToken": "test-token"}}})
        c = Claim("ronin:foo", "0xbar")
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
    mocked_provider.assert_called_with(RONIN_PROVIDER_FREE)
    mocked_checksum.assert_called_with(SLP_CONTRACT)
    mocked_random_msg.assert_called_once()
    mock_sign_message.assert_called_with(encode_defunct(text="random_msg"), private_key=c.private_key)


@patch("web3.eth.Eth.contract")
@patch("web3.eth.Eth.account.sign_message", return_value={"signature": HexBytes(b"123")})
@patch("axie.claims.Claim.create_random_msg", return_value="random_msg")
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("web3.Web3.HTTPProvider", return_value="provider")
def test_get_jwt_fail_req(mocked_provider, mocked_checksum, mocked_random_msg, mock_sign_message, _):
    with requests_mock.Mocker() as req_mocker:
        req_mocker.post("https://graphql-gateway.axieinfinity.com/graphql",
                        status_code=500)
        c = Claim("ronin:foo", "0xbar")
        with pytest.raises(Exception) as e:
            c.get_jwt()
            expected_payload = {
                "operationName": "CreateAccessTokenWithSignature",
                "variables": {
                    "input": {
                        "mainnet": "ronin",
                        "owner": "checksum",
                        "message": "random_msg",
                        "signature": f"{HexBytes(b'123').hex()}"
                    }
                },
                "query": "mutation CreateAccessTokenWithSignature($input: SignatureInput!)"
                "{createAccessTokenWithSignature(input: $input) "
                "{newAccount result accessToken __typename}}"
            }
            assert req_mocker.request_history[0].json() == expected_payload
    assert str(e.value) == ("Error! Getting JWT! Error: 500 Server Error: None for url: "
                            "https://graphql-gateway.axieinfinity.com/graphql")
    mocked_provider.assert_called_with(RONIN_PROVIDER_FREE)
    mocked_checksum.assert_called_with(SLP_CONTRACT)
    mocked_random_msg.assert_called_once()
    mock_sign_message.assert_called_with(encode_defunct(text="random_msg"), private_key=c.private_key)


@patch("web3.eth.Eth.contract")
@patch("web3.eth.Eth.account.sign_message", return_value={"signature": HexBytes(b"123")})
@patch("axie.claims.Claim.create_random_msg", return_value="random_msg")
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("web3.Web3.HTTPProvider", return_value="provider")
def test_jwq_fail_req_content(mocked_provider, mocked_checksum, mocked_random_msg, mock_sign_message, _):
        with requests_mock.Mocker() as req_mocker:
            req_mocker.post("https://graphql-gateway.axieinfinity.com/graphql", json={"data": {}})
            c = Claim("ronin:foo", "0xbar")
            with pytest.raises(Exception) as e:
                c.get_jwt()
                expected_payload = {
                    "operationName": "CreateAccessTokenWithSignature",
                    "variables": {
                        "input": {
                            "mainnet": "ronin",
                            "owner": "checksum",
                            "message": "random_msg",
                            "signature": f"{HexBytes(b'123').hex()}"
                        }
                    },
                    "query": "mutation CreateAccessTokenWithSignature($input: SignatureInput!)"
                    "{createAccessTokenWithSignature(input: $input) "
                    "{newAccount result accessToken __typename}}"
                }
                assert req_mocker.request_history[0].json() == expected_payload
        assert str(e.value) == ("Could not retreive JWT, probably your private key for this account is wrong. "
                                f"Account: {c.account}")
        mocked_provider.assert_called_with(RONIN_PROVIDER_FREE)
        mocked_checksum.assert_called_with(SLP_CONTRACT)
        mocked_random_msg.assert_called_once()
        mock_sign_message.assert_called_with(encode_defunct(text="random_msg"), private_key=c.private_key)


@patch("web3.eth.Eth.contract")
@patch("web3.eth.Eth.account.sign_message", return_value={"signature": HexBytes(b"123")})
@patch("axie.claims.Claim.create_random_msg", return_value="random_msg")
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("web3.Web3.HTTPProvider", return_value="provider")
def test_jwq_fail_req_content_2(mocked_provider, mocked_checksum, mocked_random_msg, mock_sign_message, _):
        with requests_mock.Mocker() as req_mocker:
            req_mocker.post("https://graphql-gateway.axieinfinity.com/graphql", 
                            json={"data": {"createAccessTokenWithSignature": {}}})
            c = Claim("ronin:foo", "0xbar")
            with pytest.raises(Exception) as e:
                c.get_jwt()
                expected_payload = {
                    "operationName": "CreateAccessTokenWithSignature",
                    "variables": {
                        "input": {
                            "mainnet": "ronin",
                            "owner": "checksum",
                            "message": "random_msg",
                            "signature": f"{HexBytes(b'123').hex()}"
                        }
                    },
                    "query": "mutation CreateAccessTokenWithSignature($input: SignatureInput!)"
                    "{createAccessTokenWithSignature(input: $input) "
                    "{newAccount result accessToken __typename}}"
                }
                assert req_mocker.request_history[0].json() == expected_payload
        assert str(e.value) == ("Could not retreive JWT, probably your private key for this account is wrong. "
                                f"Account: {c.account}")
        mocked_provider.assert_called_with(RONIN_PROVIDER_FREE)
        mocked_checksum.assert_called_with(SLP_CONTRACT)
        mocked_random_msg.assert_called_once()
        mock_sign_message.assert_called_with(encode_defunct(text="random_msg"), private_key=c.private_key)


@pytest.mark.asyncio
@patch("web3.Web3.toHex", return_value="transaction_hash")
@patch("web3.Web3.keccak", return_value='result_of_keccak')
@patch("web3.eth.Eth.get_transaction_receipt", return_value={'status': 1})
@patch("web3.eth.Eth.send_raw_transaction", return_value="raw_tx")
@patch("web3.eth.Eth.account.sign_transaction")
@patch("axie.claims.get_nonce", return_value=1)
@patch("axie.claims.Claim.get_jwt", return_value="token")
@patch("axie.claims.Claim.has_unclaimed_slp", return_value=456)
@patch("axie.claims.check_balance", return_value=123)
@patch("web3.eth.Eth.contract")
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("web3.Web3.HTTPProvider", return_value="provider")
async def test_execution(mocked_provider,
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
                         caplog):
    # Make sure file is clean to start
    await cleanup_log_file()
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
            c = Claim("ronin:foo", "0x00003A01C01173D676B64123")
            await c.execute()
    mocked_provider.assert_called_with(RONIN_PROVIDER_FREE)
    mocked_checksum.assert_has_calls([call(SLP_CONTRACT), call("0xfoo")])
    mocked_contract.assert_called_with(address="checksum", abi={"foo": "bar"})
    moocked_check_balance.assert_called_with("0xfoo")
    mocked_unclaimed_slp.assert_called_once()
    assert c.private_key == "0x00003A01C01173D676B64123"
    assert c.account == "0xfoo"
    mock_get_jwt.assert_called_once()
    mock_get_nonce.assert_called_with("0xfoo")
    mocked_sign_transaction.assert_called_once()
    mock_raw_send.assert_called_once()
    mock_receipt.assert_called_with("transaction_hash")
    mock_keccak.assert_called_once()
    mock_to_hex.assert_called_with("result_of_keccak")
    assert "Account ronin:foo has 456 unclaimed SLP" in caplog.text
    print(caplog.text)
    assert "SLP Claimed! New balance for account (ronin:foo) is: 123" in caplog.text
    with open(LOG_FILE_PATH) as f:
        log_file = f.readlines()
        assert len(log_file) == 1
    assert "Important: SLP Claimed! New balance for account (ronin:foo) is: 123" in log_file[0]
    await cleanup_log_file()


@pytest.mark.asyncio
@patch("web3.Web3.toHex", return_value="transaction_hash")
@patch("web3.Web3.keccak", return_value='result_of_keccak')
@patch("web3.eth.Eth.get_transaction_receipt", return_value={'status': 1})
@patch("web3.eth.Eth.send_raw_transaction", return_value="raw_tx")
@patch("web3.eth.Eth.account.sign_transaction")
@patch("axie.claims.get_nonce", return_value=1)
@patch("axie.claims.Claim.get_jwt", return_value="token")
@patch("axie.claims.Claim.has_unclaimed_slp", return_value=456)
@patch("axie.claims.check_balance", return_value=123)
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
                                               caplog):
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
            c = Claim("ronin:foo", "0x00003A01C01173D676B64123")
            with pytest.raises(Exception) as e:
                await c.execute()
            assert str(e.value) == "Account ronin:foo had no signature in blockchain_related"
    mocked_provider.assert_called_with(RONIN_PROVIDER_FREE)
    mocked_checksum.assert_called_with('0xa8754b9fa15fc18bb59458815510e40a12cd2014')
    mocked_contract.assert_called_with(address="checksum", abi={"foo": "bar"})
    moocked_check_balance.assert_not_called()
    mocked_unclaimed_slp.assert_called_once()
    assert c.private_key == "0x00003A01C01173D676B64123"
    assert c.account == "0xfoo"
    mock_get_jwt.assert_called_once()
    mock_get_nonce.assert_not_called()
    mocked_sign_transaction.assert_not_called()
    mock_raw_send.assert_not_called()
    mock_receipt.assert_not_called()
    mock_keccak.assert_not_called()
    mock_to_hex.assert_not_called()
    