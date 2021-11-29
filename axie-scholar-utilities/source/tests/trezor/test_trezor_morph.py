import sys
import json

from mock import patch, call
import requests_mock
from hexbytes import HexBytes

from trezor import TrezorAxieMorphingManager
from trezor.trezor_morphing import TrezorMorph


class MockedSignedMsg:
    
    def __init__(self):
        self.signature = HexBytes(b'123')


@patch("trezor.trezor_morphing.load_json", return_value={"foo": "bar"})
def test_morph_manager_init(mock_load_json):
    config_file = "c_file.json"
    mm = TrezorAxieMorphingManager([1, 2, 3], "ronin:abc1", config_file)
    mock_load_json.assert_called_with(config_file)
    assert mm.axie_list == [1, 2, 3]
    assert mm.account == "ronin:abc1"
    assert mm.trezor_config == {"foo": "bar"}


def test_morph_manager_verify_input_success(tmpdir):
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    c_file = tmpdir.join("c.json")
    config_data = {scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    c_file.write(json.dumps(config_data))
    mm = TrezorAxieMorphingManager([1, 2, 3], scholar_acc, c_file)
    mm.verify_inputs()
    assert mm.axie_list == [1, 2, 3]
    assert mm.account == scholar_acc
    assert mm.trezor_config == config_data


def test_morph_manager_verify_input_fail(tmpdir, caplog):
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    c_file = tmpdir.join("c.json")
    config_data = {"ronin:abc123": {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    c_file.write(json.dumps(config_data))
    with patch.object(sys, "exit") as mocked_sys:
        mm = TrezorAxieMorphingManager([1, 2, 3], scholar_acc, c_file)
        mm.verify_inputs()
    mocked_sys.assert_called_once()
    assert f"Account '{scholar_acc}' is not present in trezor config, please re-run trezor setup." in caplog.text


@patch("trezor.trezor_morphing.get_default_client", return_value='client')
@patch("trezor.trezor_morphing.TrezorMorph.execute", return_value=None)
@patch("trezor.trezor_morphing.TrezorMorph.__init__", return_value=None)
def test_morph_manager_execute(mock_morph_init, mock_morph_execute, mock_client, tmpdir):
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    c_file = tmpdir.join("c.json")
    config_data = {scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    c_file.write(json.dumps(config_data))
    mm = TrezorAxieMorphingManager([1, 2, 3], scholar_acc, c_file)
    mm.execute()
    mock_client.assert_called()
    mock_morph_init.assert_has_calls(calls=[
        call(axie=1, account=scholar_acc, client='client', bip_path="m/44'/60'/0'/0/0"),
        call(axie=2, account=scholar_acc, client='client', bip_path="m/44'/60'/0'/0/0"),
        call(axie=3, account=scholar_acc, client='client', bip_path="m/44'/60'/0'/0/0")
    ])
    assert mock_morph_execute.call_count == 3


@patch("trezor.trezor_utils.parse_path", return_value="m/44'/60'/0'/0/0")
def test_morph_init(mock_parse):
    m = TrezorMorph(axie=1, account="ronin:abcd1", client='client', bip_path="m/44'/60'/0'/0/0")
    mock_parse.assert_called()
    assert m.axie == 1
    assert m.account == "0xabcd1"
    assert m.client == "client"
    assert m.bip_path == "m/44'/60'/0'/0/0"


@patch("trezor.trezor_utils.parse_path", return_value="m/44'/60'/0'/0/0")
@patch("trezor.trezor_morphing.ethereum.sign_message", return_value=MockedSignedMsg())
@patch("trezor.trezor_morphing.TrezorMorph.get_jwt", return_value="token")
def test_morph_execute(mock_get_jwt, mock_sign_msg, mock_parse, caplog):
    with requests_mock.Mocker() as req_mocker:
        req_mocker.post(
            'https://graphql-gateway.axieinfinity.com/graphql',
            json={
                "data": {"morphAxie": True}
            }
        )
        m = TrezorMorph(axie=1, account="ronin:abcd1", client='client', bip_path="m/44'/60'/0'/0/0")
        m.execute()
    mock_parse.assert_called()
    mock_get_jwt.assert_called()
    mock_sign_msg.assert_called()
    assert f"Axie {m.axie} in {m.account} correctly morphed!" in caplog.text



@patch("trezor.trezor_utils.parse_path", return_value="m/44'/60'/0'/0/0")
@patch("trezor.trezor_morphing.ethereum.sign_message", return_value=MockedSignedMsg())
@patch("trezor.trezor_morphing.TrezorMorph.get_jwt", return_value="token")
def test_morph_execute(mock_get_jwt, mock_sign_msg, mock_parse, caplog):
    with requests_mock.Mocker() as req_mocker:
        req_mocker.post(
            'https://graphql-gateway.axieinfinity.com/graphql',
            json={
                "foo": "bar"
            }
        )
        m = TrezorMorph(axie=1, account="ronin:abcd1", client='client', bip_path="m/44'/60'/0'/0/0")
        m.execute()
    mock_parse.assert_called()
    mock_get_jwt.assert_called()
    mock_sign_msg.assert_called()
    assert f"Somethin went wrong morphing axie {m.axie} in {m.account}" in caplog.text
