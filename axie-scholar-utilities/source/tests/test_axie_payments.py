import sys
import builtins
import logging

import pytest
from mock import patch, call, mock_open

from axie import AxiePaymentsManager
from axie.payments import Payment, SLP_CONTRACT, PaymentsSummary
from tests.test_utils import LOG_FILE_PATH, cleanup_log_file


@patch("axie.payments.load_json")
def test_payments_manager_init(mocked_load_json):
    payments_file = "sample_payments_file.json"
    secrets_file = "sample_secrets_file.json"
    axp = AxiePaymentsManager(payments_file, secrets_file)
    mocked_load_json.assert_has_calls(
        calls=[call(payments_file), call(secrets_file)]
    )
    axp.auto = False
    axp2 = AxiePaymentsManager(payments_file, secrets_file, auto=True)
    axp2.auto = True


def test_payments_manager_verify_input_success(tmpdir):
    p_file = tmpdir.join("p.json")
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    p_file.write(('{"Manager":"'+manager_acc+'","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPayout":10,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPayout":1,'
                  '"ManagerPayout":9}],"Donations":[{"Name":"Entity 1",'
                  '"AccountAddress": "'+dono_acc+'","Percent":0.01}]}'))
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    axp = AxiePaymentsManager(p_file, s_file)
    axp.verify_inputs()
    assert axp.manager_acc == manager_acc
    assert axp.scholar_accounts == [
        {"Name": "Scholar 1",
         "AccountAddress": scholar_acc,
         "ScholarPayoutAddress": "ronin:<scholar_address>",
         "ScholarPayout": 10,
         "TrainerPayoutAddress": "ronin:<trainer_address>",
         "TrainerPayout": 1,
         "ManagerPayout": 9}]
    assert axp.donations == [
        {"Name": "Entity 1",
         "AccountAddress": dono_acc,
         "Percent": 0.01}]

def test_payments_manager_verify_input_manager_ronin_short(tmpdir, caplog):
    p_file = tmpdir.join("p.json")
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    dono_acc = 'ronin:<donations_address>'
    p_file.write(('{"Manager":"'+manager_acc+'","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPayout":10,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPayout":1,'
                  '"ManagerPayout":9}],"Donations":[{"Name":"Entity 1",'
                  '"AccountAddress": "'+dono_acc+'","Percent":0.01}]}'))
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    with patch.object(sys, "exit") as mocked_sys:
        axp = AxiePaymentsManager(p_file, s_file)
        axp.verify_inputs()
    mocked_sys.assert_called_once()
    assert f"Please review the ronins in your donations. One or more are wrong!" in caplog.text


def test_payments_manager_verify_input_donations_exceed_max(tmpdir, caplog):
    p_file = tmpdir.join("p.json")
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    p_file.write(('{"Manager":"'+manager_acc+'","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPayout":10,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPayout":1,'
                  '"ManagerPayout":9}],"Donations":[{"Name":"Entity 1",'
                  '"AccountAddress": "'+dono_acc+'","Percent":1}]}'))
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    with patch.object(sys, "exit") as mocked_sys:
        axp = AxiePaymentsManager(p_file, s_file)
        axp.verify_inputs()
    mocked_sys.assert_called_once()
    assert "Payments file donations exeeds 100%, please review it" in caplog.text

def test_payments_manager_verify_input_correct_dono_(tmpdir, caplog):
    p_file = tmpdir.join("p.json")
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    p_file.write(('{"Manager":"'+manager_acc+'","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPayout":10,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPayout":1,'
                  '"ManagerPayout":9}],"Donations":[{"Name":"Entity 0.01",'
                  '"AccountAddress": "'+dono_acc+'","Percent":1}]}'))
    s_file = tmpdir.join("s.json")
    s_file.write('{ }')
    with patch.object(sys, "exit") as mocked_sys:
        axp = AxiePaymentsManager(p_file, s_file)
        axp.verify_inputs()
    mocked_sys.assert_called_once()
    assert "Account 'Scholar 1' is not present in secret file, please add it." in caplog.text



def test_payments_manager_verify_input_missing_private_key(tmpdir, caplog):
    p_file = tmpdir.join("p.json")
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    p_file.write(('{"Manager":"'+manager_acc+'","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPayout":10,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPayout":1,'
                  '"ManagerPayout":9}],"Donations":[{"Name":"Entity 0.01",'
                  '"AccountAddress": "'+dono_acc+'","Percent":1}]}'))
    s_file = tmpdir.join("s.json")
    s_file.write('{ }')
    with patch.object(sys, "exit") as mocked_sys:
        axp = AxiePaymentsManager(p_file, s_file)
        axp.verify_inputs()
    mocked_sys.assert_called_once()
    assert "Account 'Scholar 1' is not present in secret file, please add it." in caplog.text


def test_payments_manager_verify_input_invalid_private_key(tmpdir, caplog):
    p_file = tmpdir.join("p.json")
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_private_acc = '0x<account_s1_private_address>012345'
    p_file.write(('{"Manager":"'+manager_acc+'","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPayout":10,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPayout":1,'
                  '"ManagerPayout":9}],"Donations":[{"Name":"Entity 0.01",'
                  '"AccountAddress": "'+dono_acc+'","Percent":1}]}'))
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    with patch.object(sys, "exit") as mocked_sys:
        axp = AxiePaymentsManager(p_file, s_file)
        axp.verify_inputs()
    mocked_sys.assert_called_once()
    assert f"Private key for account {scholar_acc} is not valid, please review it!" in caplog.text
    assert ("Please make sure your payments.json file looks like the one in the README.md\n"
           "Find it here: https://ferranmarin.github.io/axie-scholar-utilities/" in caplog.text)
    assert ("If your problem is with secrets.json, delete it and re-generate the file starting with "
            "an empty secrets file" in caplog.text)


@patch("axie.payments.get_nonce", return_value=1)
@patch("axie.AxiePaymentsManager.payout_account")
@patch("axie.AxiePaymentsManager.check_acc_has_enough_balance", return_value=True)
def test_payments_manager_prepare_payout_low_slp(mocked_check_balance, mocked_payout, mocked_get_nonce, tmpdir):
    p_file = tmpdir.join("p.json")
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    clean_scholar_acc = scholar_acc.replace("ronin:", "0x")
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    p_file.write(('{"Manager":"'+manager_acc+'","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPayout":10,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPayout":1,'
                  '"ManagerPayout":9}],"Donations":[{"Name":"Entity 1",'
                  '"AccountAddress": "'+dono_acc+'","Percent":0.01}]}'))
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    axp = AxiePaymentsManager(p_file, s_file)
    axp.verify_inputs()
    axp.prepare_payout()
    mocked_check_balance.assert_called_with(scholar_acc, 20)
    assert mocked_get_nonce.call_count == 4
    mocked_payout.assert_called_once()
    # 1st payment
    assert mocked_payout.call_args[0][0] == "Scholar 1"
    assert mocked_payout.call_args[0][1][0].name == "Payment to scholar of Scholar 1"
    assert mocked_payout.call_args[0][1][0].from_acc == clean_scholar_acc
    assert mocked_payout.call_args[0][1][0].from_private == scholar_private_acc
    assert mocked_payout.call_args[0][1][0].amount == 10
    assert mocked_payout.call_args[0][1][0].nonce == 1
    # 2nd payment
    assert mocked_payout.call_args[0][1][1].name == "Payment to trainer of Scholar 1"
    assert mocked_payout.call_args[0][1][1].from_acc == clean_scholar_acc
    assert mocked_payout.call_args[0][1][1].from_private == scholar_private_acc
    assert mocked_payout.call_args[0][1][1].amount == 1
    assert mocked_payout.call_args[0][1][1].nonce == 2
    # 3rd Payment
    assert mocked_payout.call_args[0][1][2].name == "Payment to manager of Scholar 1"
    assert mocked_payout.call_args[0][1][2].from_acc == clean_scholar_acc
    assert mocked_payout.call_args[0][1][2].from_private == scholar_private_acc
    assert mocked_payout.call_args[0][1][2].amount == 9
    assert mocked_payout.call_args[0][1][2].nonce == 3
    assert len(mocked_payout.call_args[0][1]) == 3


@patch("axie.payments.get_nonce", return_value=1)
@patch("axie.AxiePaymentsManager.payout_account")
@patch("axie.AxiePaymentsManager.check_acc_has_enough_balance", return_value=True)
def test_payments_manager_prepare_payout_high_slp_no_donos(mocked_check_balance,
                                                           mocked_payout,
                                                           mocked_get_nonce,
                                                           tmpdir):
    p_file = tmpdir.join("p.json")
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    clean_scholar_acc = scholar_acc.replace("ronin:", "0x")
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    p_file.write(('{"Manager":"'+manager_acc+'","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPayout":500,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPayout":100,'
                  '"ManagerPayout":400}]}'))
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    axp = AxiePaymentsManager(p_file, s_file)
    axp.verify_inputs()
    axp.prepare_payout()
    mocked_check_balance.assert_called_with(scholar_acc, 1000)
    assert mocked_get_nonce.call_count == 5
    mocked_payout.assert_called_once()
    # 1st payment
    assert mocked_payout.call_args[0][0] == "Scholar 1"
    assert mocked_payout.call_args[0][1][0].name == "Payment to scholar of Scholar 1"
    assert mocked_payout.call_args[0][1][0].from_acc == clean_scholar_acc
    assert mocked_payout.call_args[0][1][0].from_private == scholar_private_acc
    assert mocked_payout.call_args[0][1][0].amount == 500
    assert mocked_payout.call_args[0][1][0].nonce == 1
    # 2nd payment
    assert mocked_payout.call_args[0][1][1].name == "Payment to trainer of Scholar 1"
    assert mocked_payout.call_args[0][1][1].from_acc == clean_scholar_acc
    assert mocked_payout.call_args[0][1][1].from_private == scholar_private_acc
    assert mocked_payout.call_args[0][1][1].amount == 100
    assert mocked_payout.call_args[0][1][1].nonce == 2
    # 3rd Payment (fee)
    assert mocked_payout.call_args[0][1][2].name == "Donation to software creator for Scholar 1"
    assert mocked_payout.call_args[0][1][2].from_acc == clean_scholar_acc
    assert mocked_payout.call_args[0][1][2].from_private == scholar_private_acc
    assert mocked_payout.call_args[0][1][2].amount == round(1000*0.01)
    assert mocked_payout.call_args[0][1][2].nonce == 3
    # 4th Payment
    assert mocked_payout.call_args[0][1][3].name == "Payment to manager of Scholar 1"
    assert mocked_payout.call_args[0][1][3].from_acc == clean_scholar_acc
    assert mocked_payout.call_args[0][1][3].from_private == scholar_private_acc
    assert mocked_payout.call_args[0][1][3].amount == 400 - round(1000*0.01)
    assert mocked_payout.call_args[0][1][3].nonce == 4
    assert len(mocked_payout.call_args[0][1]) == 4


@patch("axie.payments.get_nonce", return_value=100)
@patch("axie.AxiePaymentsManager.payout_account")
@patch("axie.AxiePaymentsManager.check_acc_has_enough_balance", return_value=True)
def test_payments_manager_prepare_payout_high_slp_with_donos(mocked_check_balance,
                                                             mocked_payout,
                                                             mocked_get_nonce,
                                                             tmpdir):
    p_file = tmpdir.join("p.json")
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    clean_scholar_acc = scholar_acc.replace("ronin:", "0x")
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    p_file.write(('{"Manager":"'+manager_acc+'","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPayout":500,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPayout":100,'
                  '"ManagerPayout":400}], "Donations":[{"Name":"Entity 1",'
                  '"AccountAddress": "'+dono_acc+'","Percent":0.01}]}'))
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    axp = AxiePaymentsManager(p_file, s_file)
    axp.verify_inputs()
    axp.prepare_payout()
    mocked_check_balance.assert_called_with(scholar_acc, 1000)
    assert mocked_get_nonce.call_count == 6
    mocked_payout.assert_called_once()
    # 1st payment
    assert mocked_payout.call_args[0][0] == "Scholar 1"
    assert mocked_payout.call_args[0][1][0].name == "Payment to scholar of Scholar 1"
    assert mocked_payout.call_args[0][1][0].from_acc == clean_scholar_acc
    assert mocked_payout.call_args[0][1][0].from_private == scholar_private_acc
    assert mocked_payout.call_args[0][1][0].amount == 500
    assert mocked_payout.call_args[0][1][0].nonce == 100
    # 2nd payment
    assert mocked_payout.call_args[0][1][1].name == "Payment to trainer of Scholar 1"
    assert mocked_payout.call_args[0][1][1].from_acc == clean_scholar_acc
    assert mocked_payout.call_args[0][1][1].from_private == scholar_private_acc
    assert mocked_payout.call_args[0][1][1].amount == 100
    assert mocked_payout.call_args[0][1][1].nonce == 101
    # 3rd payment (dono)
    assert mocked_payout.call_args[0][1][2].name == "Donation to Entity 1 for Scholar 1"
    assert mocked_payout.call_args[0][1][2].from_acc == clean_scholar_acc
    assert mocked_payout.call_args[0][1][2].from_private == scholar_private_acc
    assert mocked_payout.call_args[0][1][2].amount == round(400*0.01)
    assert mocked_payout.call_args[0][1][2].nonce == 102
    # 4th Payment (fee)
    assert mocked_payout.call_args[0][1][3].name == "Donation to software creator for Scholar 1"
    assert mocked_payout.call_args[0][1][3].from_acc == clean_scholar_acc
    assert mocked_payout.call_args[0][1][3].from_private == scholar_private_acc
    assert mocked_payout.call_args[0][1][3].amount == round(1000*0.01)
    assert mocked_payout.call_args[0][1][3].nonce == 103
    # 5th Payment
    assert mocked_payout.call_args[0][1][4].name == "Payment to manager of Scholar 1"
    assert mocked_payout.call_args[0][1][4].from_acc == clean_scholar_acc
    assert mocked_payout.call_args[0][1][4].from_private == scholar_private_acc
    assert mocked_payout.call_args[0][1][4].amount == 400 - round(1000*0.01) - round(400*0.01)
    assert mocked_payout.call_args[0][1][4].nonce == 104
    assert len(mocked_payout.call_args[0][1]) == 5


@patch("axie.payments.get_nonce", return_value=100)
@patch("axie.AxiePaymentsManager.payout_account")
@patch("axie.AxiePaymentsManager.check_acc_has_enough_balance", return_value=False)
def test_payments_manager_prepare_no_payout_not_enough_balance(mocked_check_balance,
                                                               mocked_payout,
                                                               mocked_get_nonce,
                                                               tmpdir):
    p_file = tmpdir.join("p.json")
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    p_file.write(('{"Manager":"'+manager_acc+'","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPayout":500,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPayout":100,'
                  '"ManagerPayout":400}], "Donations":[{"Name":"Entity 1",'
                  '"AccountAddress": "'+dono_acc+'","Percent":0.01}]}'))
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    axp = AxiePaymentsManager(p_file, s_file)
    axp.verify_inputs()
    axp.prepare_payout()
    assert mocked_get_nonce.call_count == 6
    mocked_check_balance.assert_called_with(scholar_acc, 1000)
    mocked_payout.assert_not_called()

@patch("axie.payments.get_nonce", return_value=100)
@patch("axie.AxiePaymentsManager.payout_account")
@patch("axie.AxiePaymentsManager.check_acc_has_enough_balance", return_value=True)
def test_payments_manager_prepare_no_payout_not_manager_payout(mocked_check_balance,
                                                               mocked_payout,
                                                               mocked_get_nonce,
                                                               tmpdir,
                                                               caplog):
    p_file = tmpdir.join("p.json")
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    p_file.write(('{"Manager":"'+manager_acc+'","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPayout":500,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPayout":100,'
                  '"ManagerPayout":1}], "Donations":[{"Name":"Entity 1",'
                  '"AccountAddress": "'+dono_acc+'","Percent":0.01}]}'))
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    axp = AxiePaymentsManager(p_file, s_file)
    axp.verify_inputs()
    axp.prepare_payout()
    assert mocked_get_nonce.call_count == 5
    mocked_check_balance.assert_called_with(scholar_acc, 601)
    mocked_payout.assert_not_called()
    assert ('Fix your payments, currently after fees and donations manager is receiving a '
            'negative payment of -5' in caplog.text)



@patch("axie.payments.get_nonce", return_value=100)
@patch("axie.AxiePaymentsManager.payout_account")
@patch("axie.payments.check_balance", return_value=90000)
def test_payments_manager_enough_balance_with_leftovers(mocked_check_balance,
                                                        mocked_payout,
                                                        mocked_get_nonce,
                                                        tmpdir,
                                                        caplog):
    p_file = tmpdir.join("p.json")
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    p_file.write(('{"Manager":"'+manager_acc+'","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPayout":500,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPayout":100,'
                  '"ManagerPayout":400}], "Donations":[{"Name":"Entity 1",'
                  '"AccountAddress": "'+dono_acc+'","Percent":0.01}]}'))
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    axp = AxiePaymentsManager(p_file, s_file)
    axp.verify_inputs()
    axp.prepare_payout()
    assert mocked_get_nonce.call_count == 6
    mocked_check_balance.assert_called_with(scholar_acc)
    mocked_payout.assert_called()
    assert ("These payments will leave 89000 SLP in your wallet."
            "Cancel payments and adjust payments if you want to leave 0 SLP in it." in caplog.text)


@patch("axie.payments.Payment.execute", return_value=("abc123", True))
@patch("axie.AxiePaymentsManager.check_acc_has_enough_balance", return_value=True)
@patch("axie.payments.get_nonce", return_value=1)
def test_payments_manager_payout_account_accept(_, mocked_check_balance, mocked_execute, tmpdir, caplog):
    p_file = tmpdir.join("p.json")
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    p_file.write(('{"Manager":"'+manager_acc+'","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPayout":500,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPayout":100,'
                  '"ManagerPayout":400}], "Donations":[{"Name":"Entity 1",'
                  '"AccountAddress": "'+dono_acc+'","Percent":0.01}]}'))
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    axp = AxiePaymentsManager(p_file, s_file)
    axp.verify_inputs()
    with caplog.at_level(logging.DEBUG):
        with patch.object(builtins, 'input', lambda _: 'y'):
            axp.prepare_payout()
        mocked_check_balance.assert_called_with(scholar_acc, 1000)
        assert mocked_execute.call_count == 5
        assert "Payment to scholar of Scholar 1(ronin:<scholar_address>) for the amount of 500 SLP" in caplog.text
        assert "Payment to trainer of Scholar 1(ronin:<trainer_address>) for the amount of 100 SLP" in caplog.text
        assert (f"Donation to Entity 1 for Scholar 1({dono_acc}) for the amount of 4 SLP" in caplog.text)
        assert ("Donation to software creator for Scholar 1(ronin:9fa1bc784c665e683597d3f29375e45786617550) "
                "for the amount of 10 SLP" in caplog.text)
        assert f"Payment to manager of Scholar 1({manager_acc}) for the amount of 386 SLP" in caplog.text
        assert "Transactions completed for account: 'Scholar 1'" in caplog.text


@patch("axie.payments.Payment.execute", return_value=("abc123", True))
@patch("axie.AxiePaymentsManager.check_acc_has_enough_balance", return_value=True)
@patch("axie.payments.get_nonce", return_value=1)
def test_payments_manager_payout_auto_yes(_, mocked_check_balance, mocked_execute, tmpdir, caplog):
    p_file = tmpdir.join("p.json")
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    p_file.write(('{"Manager":"'+manager_acc+'","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPayout":500,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPayout":100,'
                  '"ManagerPayout":400}], "Donations":[{"Name":"Entity 1",'
                  '"AccountAddress": "'+dono_acc+'","Percent":0.01}]}'))
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    axp = AxiePaymentsManager(p_file, s_file, auto=True)
    axp.verify_inputs()
    with caplog.at_level(logging.INFO):
        axp.prepare_payout()
        mocked_check_balance.assert_called_with(scholar_acc, 1000)
        assert mocked_execute.call_count == 5
        assert "Payment to scholar of Scholar 1(ronin:<scholar_address>) for the amount of 500 SLP" in caplog.text
        assert "Payment to trainer of Scholar 1(ronin:<trainer_address>) for the amount of 100 SLP" in caplog.text
        assert (f"Donation to Entity 1 for Scholar 1({dono_acc}) for the amount "
                "of 4 SLP" in caplog.text)
        assert ("Donation to software creator for Scholar 1(ronin:9fa1bc784c665e683597d3f29375e45786617550) "
                "for the amount of 10 SLP" in caplog.text)
        assert f"Payment to manager of Scholar 1({manager_acc}) for the amount of 386 SLP" in caplog.text
        assert "Transactions completed for account: 'Scholar 1'" in caplog.text
        assert "Transactions Summary:" in caplog.text



@patch("axie.payments.Payment.execute")
@patch("axie.AxiePaymentsManager.check_acc_has_enough_balance", return_value=True)
@patch("axie.payments.get_nonce", return_value=1)
def test_payments_manager_payout_account_deny(_, mocked_check_balance, mocked_execute, tmpdir, caplog):
    p_file = tmpdir.join("p.json")
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    p_file.write(('{"Manager":"'+manager_acc+'","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPayout":500,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPayout":100,'
                  '"ManagerPayout":400}], "Donations":[{"Name":"Entity 1",'
                  '"AccountAddress": "'+dono_acc+'","Percent":0.01}]}'))
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    axp = AxiePaymentsManager(p_file, s_file)
    axp.verify_inputs()
    with patch.object(builtins, 'input', lambda _: 'n'):
        axp.prepare_payout()
    mocked_check_balance.assert_called_with(scholar_acc, 1000)
    mocked_execute.assert_not_called()
    assert "Transactions canceled for account: 'Scholar 1'" in caplog.text


@patch("web3.Web3.toChecksumAddress")
@patch("web3.eth.Eth.get_transaction_count", return_value=123)
def test_payment_get_nonce_calls_w3_low_nonce(_, mocked_transaction_count):
    p = Payment(
        "random_account",
        "manager",
        "ronin:from_ronin",
        "ronin:from_private_ronin",
        "ronin:to_ronin",
        10,
        PaymentsSummary(),
        1)
    mocked_transaction_count.assert_called_once()
    assert p.nonce == 123


@patch("web3.Web3.toChecksumAddress")
@patch("web3.eth.Eth.get_transaction_count", return_value=123)
def test_payment_get_nonce_calls_w3_high_nonce(_, mocked_transaction_count):
    p = Payment(
        "random_account",
        "manager",
        "ronin:from_ronin",
        "ronin:from_private_ronin",
        "ronin:to_ronin",
        10,
        PaymentsSummary(),
        125)
    mocked_transaction_count.assert_called_once()
    assert p.nonce == 125


@pytest.mark.asyncio
@patch("web3.eth.Eth.get_transaction_count", return_value=123)
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("web3.eth.Eth.account.sign_transaction")
@patch("web3.eth.Eth.send_raw_transaction")
@patch("web3.Web3.toHex", return_value="transaction_hash")
@patch("web3.Web3.keccak", return_value='result_of_keccak')
@patch("web3.eth.Eth.contract")
@patch("web3.eth.Eth.get_transaction_receipt", return_value={'status': 1})
async def test_execute_calls_web3_functions(mock_transaction_receipt,
                                            mock_contract,
                                            mock_keccak,
                                            mock_to_hex,
                                            mock_send,
                                            mock_sign,
                                            mock_checksum,
                                            _,
                                            caplog):
    # Make sure file is clean to start
    await cleanup_log_file()
    PaymentsSummary().clear()
    s = PaymentsSummary()
    p = Payment(
        "random_account",
        "manager",
        "ronin:from_ronin",
        "ronin:from_private_ronin",
        "ronin:to_ronin",
        10,
        s
    )
    with patch.object(builtins,
                      "open",
                      mock_open(read_data='{"foo": "bar"}')) as mock_file:
        await p.execute()
    mock_file.assert_called_with("axie/slp_abi.json")
    mock_contract.assert_called_with(address="checksum", abi={"foo": "bar"})
    mock_keccak.assert_called_once()
    mock_to_hex.assert_called_with("result_of_keccak")
    mock_send.assert_called_once()
    mock_sign.assert_called_once()
    assert mock_sign.call_args[1]['private_key'] == "ronin:from_private_ronin"
    mock_checksum.assert_has_calls(calls=[
        call('0xfrom_ronin'),
        call(SLP_CONTRACT),
        call('0xto_ronin')])
    mock_transaction_receipt.assert_called_with("transaction_hash")
    assert ('Transaction random_account(ronin:to_ronin) for the amount of 10 SLP completed! Hash: transaction_hash - '
            'Explorer: https://explorer.roninchain.com/tx/transaction_hash' in caplog.text)
    assert str(s) == "Paid 1 managers, 10 SLP.\n"
    with open(LOG_FILE_PATH) as f:
        log_file = f.readlines()
        assert len(log_file) == 1
    assert ("Important: Transaction random_account(ronin:to_ronin) for the amount of 10 SLP completed! "
            "Hash: transaction_hash - Explorer: https://explorer.roninchain.com/tx/transaction_hash") in log_file[0]
    await cleanup_log_file()
