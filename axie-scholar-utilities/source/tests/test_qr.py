import os
import sys
import json
from datetime import datetime

import pytest
from mock import patch, call
import requests_mock

from axie import QRCodeManager
from axie.qr_code import QRCode


@patch("axie.QRCodeManager.load_secrets_and_acc_name", return_value=("foo", "bar"))
def test_qrcode_manager_init(mocked_load):
    secrets_file = "secrets.json"
    payments_file = "payments.json"
    QRCodeManager(payments_file, secrets_file)
    mocked_load.assert_called_with(secrets_file, payments_file)


def test_qrcode_manager_verify_input_success(tmpdir):
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
                "ScholarPercent": 60
            }]
    }
    p_file.write(json.dumps(data))
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    qr = QRCodeManager(p_file, s_file)
    qr.verify_inputs()
    assert qr.secrets_file == {scholar_acc: scholar_private_acc}
    assert qr.path == os.path.dirname(s_file)


def test_qrcode_manager_verify_inputs_wrong_public_ronin(tmpdir, caplog):
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
                "ScholarPercent": 60
            }]
    }
    p_file.write(json.dumps(data))
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    with patch.object(sys, "exit") as mocked_sys:
        qr = QRCodeManager(p_file, s_file)
        qr.verify_inputs()

    mocked_sys.assert_called_once()
    assert f"Public address {scholar_acc} needs to start with ronin:" in caplog.text

def test_qrcode_manager_verify_input_wrong_private_ronin(tmpdir, caplog):
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
                "ScholarPercent": 60
            }]
    }
    p_file.write(json.dumps(data))
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    with patch.object(sys, "exit") as mocked_sys:
        qr = QRCodeManager(p_file, s_file)
        qr.verify_inputs()

    mocked_sys.assert_called_once()
    assert f"Private key for account {scholar_acc} is not valid, please review it!" in caplog.text


def test_qrcode_manager_verify_input_wrong_private_short(tmpdir, caplog):
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
                "ScholarPercent": 60
            }]
    }
    p_file.write(json.dumps(data))
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    with patch.object(sys, "exit") as mocked_sys:
        qr = QRCodeManager(p_file, s_file)
        qr.verify_inputs()

    mocked_sys.assert_called_once()
    assert f"Private key for account {scholar_acc} is not valid, please review it!" in caplog.text


@patch("axie.qr_code.QRCode.generate_qr")
@patch("axie.qr_code.QRCode.__init__", return_value=None)
def test_qrcode_manager_execute(mocked_qrcode_init, mocked_qrcode_generate_qr, tmpdir):
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*4)
    scholar_acc_other = 'ronin:<account_s2_address>' + "".join([str(x) for x in range(10)]*4)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    scholar_private_acc_other = '0x<account_s2_private_address>012345' + "".join([str(x) for x in range(10)]*3)
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
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'", "'+scholar_acc_other+'":"'+scholar_private_acc_other+'"}')
    qr = QRCodeManager(p_file, s_file)
    qr.execute()
    mocked_qrcode_init.assert_has_calls(calls=[
        call(account=scholar_acc, private_key=scholar_private_acc, acc_name="Scholar 1", path=os.path.dirname(s_file)),
        call(account=scholar_acc_other, private_key=scholar_private_acc_other, acc_name="Scholar 2", path=os.path.dirname(s_file))
    ])
    assert mocked_qrcode_generate_qr.call_count == 2


def test_qrcode_init():
    q = QRCode(account="ronin:foo", private_key="0xbar", acc_name="test_acc", path="/")
    assert q.private_key == "0xbar"
    assert q.account == "0xfoo"
    assert q.acc_name == "test_acc"
    assert q.path == f'/test_acc-{int(datetime.timestamp(datetime.now()))}.png'


@patch("qrcode.make")
@patch("axie.qr_code.QRCode.get_jwt", return_value="token")
def test_qr_code_generate(mock_get_jwt, mock_qrmake, tmpdir, caplog):
    q = QRCode(account="ronin:foo", private_key="0xbar", acc_name="test_acc", path=tmpdir)
    q.generate_qr()
    mock_get_jwt.assert_called()
    mock_qrmake.assert_called_with("token")
    assert f"Saving QR Code for account test_acc at {q.path}" in caplog.text
