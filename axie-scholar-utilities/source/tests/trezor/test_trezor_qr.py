import os
import sys
import json
from datetime import datetime

from mock import patch, call
from trezorlib.tools import parse_path 

from trezor import TrezorQRCodeManager
from trezor.trezor_qr_code import TrezorQRCode
from trezor.trezor_utils import CustomUI


@patch("trezor.TrezorQRCodeManager.load_trezor_config_and_acc_name", return_value=("foo", "bar"))
def test_qrcode_manager_init(mocked_load):
    config_file = "trezor_config.json"
    payments_file = "payments.json"
    tr_qr_m = TrezorQRCodeManager(payments_file, config_file)
    mocked_load.assert_called_with(config_file, payments_file)
    assert tr_qr_m.trezor_config == "foo"
    assert tr_qr_m.acc_names == "bar"


def test_qrcode_manager_verify_input_success(tmpdir):
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*4)
    p_file = tmpdir.join("p.json")
    data = {
        "Manager": "ronin:<Manager address here>",
        "Scholars": [
            {
                "Name": "Scholar 1",
                "AccountAddress": f"{scholar_acc}",
                "ScholarPayoutAddress": "ronin:<scholar_address>",
                "ScholarPercent": 60
            }]
    }
    p_file.write(json.dumps(data))
    c_file = tmpdir.join("s.json")
    config_data = {scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    c_file.write(json.dumps(config_data))
    qr = TrezorQRCodeManager(p_file, c_file)
    qr.verify_inputs()
    assert qr.trezor_config == config_data
    assert qr.acc_names == {scholar_acc: "Scholar 1"}
    assert qr.path == os.path.dirname(c_file)


def test_qrcode_manager_verify_inputs_wrong_public_ronin(tmpdir, caplog):
    scholar_acc = '<account_s1_address>' + "".join([str(x) for x in range(10)]*4)
    p_file = tmpdir.join("p.json")
    data = {
        "Manager": "ronin:<Manager address here>",
        "Scholars": [
            {
                "Name": "Scholar 1",
                "AccountAddress": f"{scholar_acc}",
                "ScholarPayoutAddress": "ronin:<scholar_address>",
                "ScholarPercent": 60
            }]
    }
    p_file.write(json.dumps(data))
    c_file = tmpdir.join("s.json")
    config_data = {scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    c_file.write(json.dumps(config_data))
    with patch.object(sys, "exit") as mocked_sys:
        qr = TrezorQRCodeManager(p_file, c_file)
        qr.verify_inputs()

    mocked_sys.assert_called_once()
    assert f"Public address {scholar_acc} needs to start with ronin:" in caplog.text


@patch("trezor.trezor_qr_code.get_default_client", return_value="client")
@patch("trezor.trezor_qr_code.TrezorQRCode.generate_qr")
@patch("trezor.trezor_qr_code.TrezorQRCode.__init__", return_value=None)
def test_qrcode_manager_execute(mocked_qrcode_init, mocked_qrcode_generate_qr, mocked_client, tmpdir):
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*4)
    scholar_acc_other = 'ronin:<account_s2_address>' + "".join([str(x) for x in range(10)]*4)
    p_file = tmpdir.join("p.json")
    data = {
        "Manager": "ronin:<Manager address here>",
        "Scholars": [
            {
                "Name": "Scholar 1",
                "AccountAddress": f"{scholar_acc}",
                "ScholarPayoutAddress": "ronin:<scholar_address>",
                "ScholarPercent": 60
            },
            {
                "Name": "Scholar 2",
                "AccountAddress": f"{scholar_acc_other}",
                "ScholarPayoutAddress": "ronin:<scholar_address>",
                "ScholarPercebt": 60
            }]
    }
    p_file.write(json.dumps(data))
    c_file = tmpdir.join("s.json")
    config_data = {
        scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}, 
        scholar_acc_other: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/1"}
    }
    c_file.write(json.dumps(config_data))
    qr = TrezorQRCodeManager(p_file, c_file)
    qr.execute()
    mocked_qrcode_init.assert_has_calls(calls=[
        call(account=scholar_acc, bip_path="m/44'/60'/0'/0/0", client="client", acc_name="Scholar 1", path=os.path.dirname(c_file)),
        call(account=scholar_acc_other,bip_path="m/44'/60'/0'/0/1", client="client", acc_name="Scholar 2", path=os.path.dirname(c_file))
    ])
    mocked_client.assert_called()
    assert mocked_qrcode_generate_qr.call_count == 2


def test_qrcode_init():
    q = TrezorQRCode(
        acc_name="test_acc",
        account="ronin:foo",
        client="client",
        bip_path="m/44'/60'/0'/0/0",
        path="/")
    assert q.acc_name == "test_acc"
    assert q.account == "0xfoo"
    assert q.client == "client"
    assert q.bip_path == parse_path("m/44'/60'/0'/0/0")
    assert q.path == f'/test_acc-{int(datetime.timestamp(datetime.now()))}.png'


@patch("qrcode.make")
@patch("trezor.trezor_qr_code.TrezorQRCode.get_jwt", return_value="token")
def test_qr_code_generate(mock_get_jwt, mock_qrmake, tmpdir, caplog):
    q = TrezorQRCode(
        acc_name="test_acc",
        account="ronin:foo",
        client="client",
        bip_path="m/44'/60'/0'/0/0",
        path=tmpdir)
    q.generate_qr()
    mock_get_jwt.assert_called()
    mock_qrmake.assert_called_with("token")
    assert f"Saving QR Code for account test_acc at {q.path}" in caplog.text
