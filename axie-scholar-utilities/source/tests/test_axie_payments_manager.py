import os
import sys

import pytest
from mock import patch, call

from axie import AxiePaymentsManager
from axie.payments import Payment

@patch("axie.AxiePaymentsManager.load_json")
def test_payments_manager_init(mocked_load_json):
    payments_file = os.path.abspath("./test_data/sample_payments_file.json")
    secrets_file = os.path.abspath("./test_data/sample_secrets_file.json")
    AxiePaymentsManager(payments_file, secrets_file)
    mocked_load_json.assert_has_calls(
        calls=[call(payments_file), call(secrets_file)]
    )

def test_payments_manager_load_json_safeguard():
    with pytest.raises(Exception) as e:
        AxiePaymentsManager.load_json("non_existent.json")
    assert str(e.value) == ("File path non_existent.json does not exist. "
                            "Please provide a correct one")

def test_payments_manager_load_json(tmpdir):
    f = tmpdir.join("test.json")
    f.write('{"foo": "bar"}')
    loaded = AxiePaymentsManager.load_json(f)
    assert loaded == {"foo": "bar"}

def test_payments_manager_load_json_not_json(tmpdir):
    f = tmpdir.join("test.txt")
    f.write("foo bar")
    with pytest.raises(Exception) as e:
        AxiePaymentsManager.load_json(f)
    assert str(e.value) == f"File in path {f} is not a correctly encoded JSON."

def test_payments_manager_verify_input_success(tmpdir):
    p_file = tmpdir.join("p.json")
    scholar_acc = 'ronin:<account_s1_address>'+ "".join([str(x) for x in range(10)]*4)
    scholar_private_acc = '0x<account_s1_private_address>012345'+ "".join([str(x) for x in range(10)]*3)
    p_file.write(('{"Manager":"ronin:<Manager address here>","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPayout":10,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPayout":1,'
                  '"ManagerPayout":9}],"Donations":[{"Name":"Entity 1",'
                  '"AccountAddress": "ronin:<donation_entity_1_address>","Percent":0.01}]}'))
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    axp = AxiePaymentsManager(p_file, s_file)
    axp.verify_inputs()
    assert axp.manager_acc == "ronin:<Manager address here>"
    assert axp.scholar_accounts == [
        {"Name":"Scholar 1",
         "AccountAddress": scholar_acc,
         "ScholarPayoutAddress":"ronin:<scholar_address>",
         "ScholarPayout":10,
         "TrainerPayoutAddress":"ronin:<trainer_address>",
         "TrainerPayout":1,
         "ManagerPayout":9}]
    assert axp.donations == [
        {"Name":"Entity 1",
         "AccountAddress": "ronin:<donation_entity_1_address>",
         "Percent":0.01}]

def test_payments_manager_verify_input_donations_exceed_max(tmpdir, caplog):
    p_file = tmpdir.join("p.json")
    scholar_acc = 'ronin:<account_s1_address>'+ "".join([str(x) for x in range(10)]*4)
    scholar_private_acc = '0x<account_s1_private_address>012345'+ "".join([str(x) for x in range(10)]*3)
    p_file.write(('{"Manager":"ronin:<Manager address here>","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPayout":10,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPayout":1,'
                  '"ManagerPayout":9}],"Donations":[{"Name":"Entity 1",'
                  '"AccountAddress": "ronin:<donation_entity_1_address>","Percent":1}]}'))
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    with patch.object(sys, "exit") as mocked_sys:
        axp = AxiePaymentsManager(p_file, s_file)
        axp.verify_inputs()
    
    mocked_sys.assert_called_once()
    assert "Payments file donations exeeds 100%, please review it" in caplog.text

def test_payments_manager_verify_input_missing_private_key(tmpdir, caplog):
    p_file = tmpdir.join("p.json")
    scholar_acc = 'ronin:<account_s1_address>'+ "".join([str(x) for x in range(10)]*4)
    p_file.write(('{"Manager":"ronin:<Manager address here>","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPayout":10,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPayout":1,'
                  '"ManagerPayout":9}],"Donations":[{"Name":"Entity 0.01",'
                  '"AccountAddress": "ronin:<donation_entity_1_address>","Percent":1}]}'))
    s_file = tmpdir.join("s.json")
    s_file.write('{ }')
    with patch.object(sys, "exit") as mocked_sys:
        axp = AxiePaymentsManager(p_file, s_file)
        axp.verify_inputs()
    
    mocked_sys.assert_called_once()
    assert "Account 'Scholar 1' is not present in secret file, please add it." in caplog.text

def test_payments_manager_verify_input_invalid_private_key(tmpdir, caplog):
    p_file = tmpdir.join("p.json")
    scholar_acc = 'ronin:<account_s1_address>'+ "".join([str(x) for x in range(10)]*4)
    scholar_private_acc = '0x<account_s1_private_address>012345'
    p_file.write(('{"Manager":"ronin:<Manager address here>","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPayout":10,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPayout":1,'
                  '"ManagerPayout":9}],"Donations":[{"Name":"Entity 0.01",'
                  '"AccountAddress": "ronin:<donation_entity_1_address>","Percent":1}]}'))
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    with patch.object(sys, "exit") as mocked_sys:
        axp = AxiePaymentsManager(p_file, s_file)
        axp.verify_inputs()
    
    mocked_sys.assert_called_once()
    assert f"Private key for account {scholar_acc} is not valid, please review it!" in caplog.text

@patch("axie.payments.Payment.get_nonce", return_value=1)
@patch("axie.payments.Payment.validate_account")
@patch("axie.AxiePaymentsManager.payout_account")
def test_payments_manager_prepare_payout_low_slp(mocked_payout, mocked_validate_acc, mocked_get_nonce, tmpdir):
    p_file = tmpdir.join("p.json")
    scholar_acc = 'ronin:<account_s1_address>'+ "".join([str(x) for x in range(10)]*4)
    scholar_private_acc = '0x<account_s1_private_address>012345'+ "".join([str(x) for x in range(10)]*3)
    p_file.write(('{"Manager":"ronin:<Manager address here>","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPayout":10,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPayout":1,'
                  '"ManagerPayout":9}],"Donations":[{"Name":"Entity 1",'
                  '"AccountAddress": "ronin:<donation_entity_1_address>","Percent":0.01}]}'))
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    axp = AxiePaymentsManager(p_file, s_file)
    axp.verify_inputs()
    axp.prepare_payout()
    mocked_validate_acc.assert_called_with('ronin:<Manager address here>')
    assert mocked_get_nonce.call_count == 4
    mocked_payout.assert_called_once()
    # 1st payment
    assert mocked_payout.call_args[0][0] == "Scholar 1"
    assert mocked_payout.call_args[0][1][0].name == "Payment to scholar"
    assert mocked_payout.call_args[0][1][0].from_acc == scholar_acc
    assert mocked_payout.call_args[0][1][0].from_private == scholar_private_acc
    assert mocked_payout.call_args[0][1][0].amount == 10
    assert mocked_payout.call_args[0][1][0].nonce == 1
    # 2nd payment
    assert mocked_payout.call_args[0][1][1].name == "Payment to trainer"
    assert mocked_payout.call_args[0][1][1].from_acc == scholar_acc
    assert mocked_payout.call_args[0][1][1].from_private == scholar_private_acc
    assert mocked_payout.call_args[0][1][1].amount == 1
    assert mocked_payout.call_args[0][1][1].nonce == 2
    # 3rd Payment
    assert mocked_payout.call_args[0][1][2].name == "Payment to manager"
    assert mocked_payout.call_args[0][1][2].from_acc == scholar_acc
    assert mocked_payout.call_args[0][1][2].from_private == scholar_private_acc
    assert mocked_payout.call_args[0][1][2].amount == 9
    assert mocked_payout.call_args[0][1][2].nonce == 3
    assert len(mocked_payout.call_args[0][1]) == 3

@patch("axie.payments.Payment.get_nonce", return_value=1)
@patch("axie.payments.Payment.validate_account")
@patch("axie.AxiePaymentsManager.payout_account")
def test_payments_manager_prepare_payout_high_slp_no_donos(mocked_payout, mocked_validate_acc, mocked_get_nonce, tmpdir):
    p_file = tmpdir.join("p.json")
    scholar_acc = 'ronin:<account_s1_address>'+ "".join([str(x) for x in range(10)]*4)
    scholar_private_acc = '0x<account_s1_private_address>012345'+ "".join([str(x) for x in range(10)]*3)
    p_file.write(('{"Manager":"ronin:<Manager address here>","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPayout":500,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPayout":100,'
                  '"ManagerPayout":400}]}'))
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    axp = AxiePaymentsManager(p_file, s_file)
    axp.verify_inputs()
    axp.prepare_payout()
    mocked_validate_acc.assert_called_with('ronin:<Manager address here>')
    assert mocked_get_nonce.call_count == 5
    mocked_payout.assert_called_once()
    # 1st payment
    assert mocked_payout.call_args[0][0] == "Scholar 1"
    assert mocked_payout.call_args[0][1][0].name == "Payment to scholar"
    assert mocked_payout.call_args[0][1][0].from_acc == scholar_acc
    assert mocked_payout.call_args[0][1][0].from_private == scholar_private_acc
    assert mocked_payout.call_args[0][1][0].amount == 500
    assert mocked_payout.call_args[0][1][0].nonce == 1
    # 2nd payment
    assert mocked_payout.call_args[0][1][1].name == "Payment to trainer"
    assert mocked_payout.call_args[0][1][1].from_acc == scholar_acc
    assert mocked_payout.call_args[0][1][1].from_private == scholar_private_acc
    assert mocked_payout.call_args[0][1][1].amount == 100
    assert mocked_payout.call_args[0][1][1].nonce == 2
    # 3rd Payment (fee)
    assert mocked_payout.call_args[0][1][2].name == "Donation to software creator"
    assert mocked_payout.call_args[0][1][2].from_acc == scholar_acc
    assert mocked_payout.call_args[0][1][2].from_private == scholar_private_acc
    assert mocked_payout.call_args[0][1][2].amount == round(1000*0.01)
    assert mocked_payout.call_args[0][1][2].nonce == 3
    # 4th Payment
    assert mocked_payout.call_args[0][1][3].name == "Payment to manager"
    assert mocked_payout.call_args[0][1][3].from_acc == scholar_acc
    assert mocked_payout.call_args[0][1][3].from_private == scholar_private_acc
    assert mocked_payout.call_args[0][1][3].amount == 400 - round(1000*0.01)
    assert mocked_payout.call_args[0][1][3].nonce == 4
    assert len(mocked_payout.call_args[0][1]) == 4

@patch("axie.payments.Payment.get_nonce", return_value=100)
@patch("axie.payments.Payment.validate_account")
@patch("axie.AxiePaymentsManager.payout_account")
def test_payments_manager_prepare_payout_high_slp_no_donos(mocked_payout, mocked_validate_acc, mocked_get_nonce, tmpdir):
    p_file = tmpdir.join("p.json")
    scholar_acc = 'ronin:<account_s1_address>'+ "".join([str(x) for x in range(10)]*4)
    scholar_private_acc = '0x<account_s1_private_address>012345'+ "".join([str(x) for x in range(10)]*3)
    p_file.write(('{"Manager":"ronin:<Manager address here>","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPayout":500,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPayout":100,'
                  '"ManagerPayout":400}], "Donations":[{"Name":"Entity 1",'
                  '"AccountAddress": "ronin:<donation_entity_1_address>","Percent":0.01}]}'))
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    axp = AxiePaymentsManager(p_file, s_file)
    axp.verify_inputs()
    axp.prepare_payout()
    mocked_validate_acc.assert_called_with('ronin:<Manager address here>')
    assert mocked_get_nonce.call_count == 6
    mocked_payout.assert_called_once()
    # 1st payment
    assert mocked_payout.call_args[0][0] == "Scholar 1"
    assert mocked_payout.call_args[0][1][0].name == "Payment to scholar"
    assert mocked_payout.call_args[0][1][0].from_acc == scholar_acc
    assert mocked_payout.call_args[0][1][0].from_private == scholar_private_acc
    assert mocked_payout.call_args[0][1][0].amount == 500
    assert mocked_payout.call_args[0][1][0].nonce == 100
    # 2nd payment
    assert mocked_payout.call_args[0][1][1].name == "Payment to trainer"
    assert mocked_payout.call_args[0][1][1].from_acc == scholar_acc
    assert mocked_payout.call_args[0][1][1].from_private == scholar_private_acc
    assert mocked_payout.call_args[0][1][1].amount == 100
    assert mocked_payout.call_args[0][1][1].nonce == 101
    # 3rd payment (dono)
    assert mocked_payout.call_args[0][1][2].name == "Donation to Entity 1"
    assert mocked_payout.call_args[0][1][2].from_acc == scholar_acc
    assert mocked_payout.call_args[0][1][2].from_private == scholar_private_acc
    assert mocked_payout.call_args[0][1][2].amount == round(400*0.01)
    assert mocked_payout.call_args[0][1][2].nonce == 102
    # 4th Payment (fee)
    assert mocked_payout.call_args[0][1][3].name == "Donation to software creator"
    assert mocked_payout.call_args[0][1][3].from_acc == scholar_acc
    assert mocked_payout.call_args[0][1][3].from_private == scholar_private_acc
    assert mocked_payout.call_args[0][1][3].amount == round(1000*0.01)
    assert mocked_payout.call_args[0][1][3].nonce == 103
    # 5th Payment
    assert mocked_payout.call_args[0][1][4].name == "Payment to manager"
    assert mocked_payout.call_args[0][1][4].from_acc == scholar_acc
    assert mocked_payout.call_args[0][1][4].from_private == scholar_private_acc
    assert mocked_payout.call_args[0][1][4].amount == 400 - round(1000*0.01) - round(400*0.01)
    assert mocked_payout.call_args[0][1][4].nonce == 104
    assert len(mocked_payout.call_args[0][1]) == 5