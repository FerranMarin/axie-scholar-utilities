import sys
import json

from mock import patch, call

from trezor import TrezorAxieMorphingManager


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
