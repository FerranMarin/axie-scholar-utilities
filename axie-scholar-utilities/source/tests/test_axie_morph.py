import sys
import builtins

import pytest
from mock import patch, call, mock_open
import requests_mock
from hexbytes import HexBytes
from eth_account.messages import encode_defunct

from axie import AxieMorphingManager
from axie.morphing import Morph


@patch("axie.morphing.load_json", return_value={"foo": "bar"})
def test_morph_manager_init(mock_load_json):
    secrets_file = "s_file.json"
    mm = AxieMorphingManager([1, 2, 3], "ronin:abc1", secrets_file)
    mock_load_json.assert_called_with(secrets_file)
    assert mm.axie_list == [1,2,3]
    assert mm.account == "ronin:abc1"
    assert mm.secrets == {"foo": "bar"}


def test_morph_manager_verify_input_success(tmpdir):
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    mm = AxieMorphingManager([1,2,3], scholar_acc, s_file)
    mm.verify_inputs()
    assert mm.axie_list == [1,2,3]
    assert mm.account == scholar_acc
    assert mm.secrets == {scholar_acc: scholar_private_acc}


def test_morph_manager_verify_input_fail(tmpdir, caplog):
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    s_file = tmpdir.join("s.json")
    s_file.write('{"foo": "bar"}')
    with patch.object(sys, "exit") as mocked_sys:
        mm = AxieMorphingManager([1,2,3], scholar_acc, s_file)
        mm.verify_inputs()
    mocked_sys.assert_called_once()
    assert f"Account '{scholar_acc}' is not present in secret file, please add it." in caplog.text


@patch("axie.morphing.Morph.execute", return_value=None)
@patch("axie.morphing.Morph.__init__", return_value=None)
def test_morph_manager_execute(mock_morph_init, mock_morph_execute, tmpdir):
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    mm = AxieMorphingManager([1,2,3], scholar_acc, s_file)
    mm.execute()
    mock_morph_init.assert_has_calls(calls=[
        call(axie=1, account=scholar_acc, private_key=scholar_private_acc),
        call(axie=2, account=scholar_acc, private_key=scholar_private_acc),
        call(axie=3, account=scholar_acc, private_key=scholar_private_acc)
    ])
    assert mock_morph_execute.call_count == 3


def test_morph_init():
    m = Morph(axie=1, account="ronin:abcd1", private_key="0xabc1")
    assert m.axie == 1
    assert m.account == "0xabcd1"
    assert m.private_key == "0xabc1"


@patch("web3.eth.Eth.account.sign_message", return_value={"signature": HexBytes(b"123")})
@patch("axie.morphing.Morph.get_jwt", return_value="token")
def test_morph_execute(mock_get_jwt, mock_sign_msg, caplog):
    with requests_mock.Mocker() as req_mocker:
        req_mocker.post(
            'https://graphql-gateway.axieinfinity.com/graphql',
            json={
                "data": {"morphAxie": True}
            }
        )
        m = Morph(axie=1, account="ronin:abc1", private_key="0xabc1")
        m.execute()
    mock_get_jwt.assert_called()
    mock_sign_msg.assert_called_with(encode_defunct(text=f"axie_id={m.axie}&owner={m.account}"),
                                                    private_key=m.private_key)
    assert f"Axie {m.axie} in {m.account} correctly morphed!" in caplog.text


@patch("web3.eth.Eth.account.sign_message", return_value={"signature": HexBytes(b"123")})
@patch("axie.morphing.Morph.get_jwt", return_value="token")
def test_morph_execute_bad_json_response(mock_get_jwt, mock_sign_msg, caplog):
    with requests_mock.Mocker() as req_mocker:
        req_mocker.post(
            'https://graphql-gateway.axieinfinity.com/graphql',
            json={
                "foo": "bar"
            }
        )
        m = Morph(axie=1, account="ronin:abc1", private_key="0xabc1")
        m.execute()
    mock_get_jwt.assert_called()
    mock_sign_msg.assert_called_with(encode_defunct(text=f"axie_id={m.axie}&owner={m.account}"),
                                                    private_key=m.private_key)
    assert f"Somethin went wrong morphing axie {m.axie} in {m.account}" in caplog.text
