import sys
import builtins
import logging

from mock import patch

from axie import AxiePaymentsManager
from axie.payments import CREATOR_FEE_ADDRESS


def test_payments_manager_init():
    payments_file = "sample_payments_file.json"
    secrets_file = "sample_secrets_file.json"
    axp = AxiePaymentsManager(payments_file, secrets_file)
    assert axp.auto is False
    axp2 = AxiePaymentsManager(payments_file, secrets_file, auto=True)
    assert axp2.auto is True


def test_payments_manager_verify_input_success():
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    p_file = {
        "scholars": [{
            "name": "Scholar 1",
            "ronin": scholar_acc,
            "splits": [
                {
                    "persona": "Manager",
                    "percentage": 44,
                    "ronin": manager_acc
                },
                {
                    "persona": "Scholar",
                    "percentage": 40,
                    "ronin": "ronin:<scholar_1_address>"
                },
                {
                    "persona": "Other Person",
                    "percentage": 6,
                    "ronin": "ronin:<other_person_address>"
                },
                {
                    "persona": "Trainer",
                    "percentage": 10,
                    "ronin": "ronin:<trainer_address>"
                }
        ]}],
        "donations": [{
            "name": "Entity 1",
            "ronin": dono_acc,
            "percentage": 1
        }]
    }
    s_file = {scholar_acc: scholar_private_acc}
    axp = AxiePaymentsManager(p_file, s_file)
    axp.verify_inputs()
    assert axp.manager_acc == None
    assert axp.type == "new"
    assert axp.scholar_accounts == p_file['scholars']
    assert axp.donations == p_file['donations']


def test_payments_manager_verify_input_success(caplog):
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    p_file = {
        "scholars": [{
            "name": "Scholar 1",
            "ronin": scholar_acc,
            "splits": [
                {
                    "persona": "foo",
                    "percentage": 44,
                    "ronin": manager_acc
                },
                {
                    "persona": "Scholar",
                    "percentage": 40,
                    "ronin": "ronin:<scholar_1_address>"
                },
                {
                    "persona": "Other Person",
                    "percentage": 6,
                    "ronin": "ronin:<other_person_address>"
                },
                {
                    "persona": "Trainer",
                    "percentage": 10,
                    "ronin": "ronin:<trainer_address>"
                }
        ]}],
        "donations": [{
            "name": "Entity 1",
            "ronin": dono_acc,
            "percentage": 1
        }]
    }
    s_file = {scholar_acc: scholar_private_acc}
    with patch.object(sys, "exit") as mocked_sys:
        axp = AxiePaymentsManager(p_file, s_file)
        axp.verify_inputs()
    mocked_sys.assert_called()
    assert "Account 'Scholar 1' has no manager in its splits. Please review it!" in caplog.text


def test_payments_manager_verify_input_success_percent():
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    p_file = {
        "Manager": manager_acc,
        "Scholars": [
            {
                "Name":"Scholar 1", 
                "AccountAddress": scholar_acc,
                "ScholarPayoutAddress": "ronin:<scholar_address>",
                "ScholarPercent": 50,
                "TrainerPayoutAddress": "ronin:<trainer_address>",
                "TrainerPercent": 1
            }],
        "Donations": [
            {
                "Name": "Entity 1",
                "AccountAddress": dono_acc,
                "Percent": 1
            }]
    }
    s_file = {scholar_acc: scholar_private_acc}
    axp = AxiePaymentsManager(p_file, s_file)
    axp.verify_inputs()
    assert axp.manager_acc == manager_acc
    assert axp.type == "legacy"
    assert axp.scholar_accounts == p_file['Scholars']
    assert axp.donations == p_file['Donations']


def test_payments_manager_verify_input_success_percent_with_payouts():
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    p_file = {
        "Manager": manager_acc,
        "Scholars": [
            {
                "Name":"Scholar 1", 
                "AccountAddress": scholar_acc,
                "ScholarPayoutAddress": "ronin:<scholar_address>",
                "ScholarPercent": 50,
                "ScholarPayout":10,
                "TrainerPayoutAddress": "ronin:<trainer_address>",
                "TrainerPercent": 1
            }],
        "Donations": [
            {
                "Name": "Entity 1",
                "AccountAddress": dono_acc,
                "Percent": 1
            }]
    }
    s_file = {scholar_acc: scholar_private_acc}
    axp = AxiePaymentsManager(p_file, s_file)
    axp.verify_inputs()
    assert axp.manager_acc == manager_acc
    assert axp.type == "legacy"
    assert axp.scholar_accounts == p_file['Scholars']
    assert axp.donations == p_file['Donations']


def test_payments_manager_verify_input_manager_ronin_short(caplog):
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    dono_acc = 'ronin:<donations_address>'
    p_file = {
        "Manager": manager_acc,
        "Scholars": [
            {
                "Name":"Scholar 1", 
                "AccountAddress": scholar_acc,
                "ScholarPayoutAddress": "ronin:<scholar_address>",
                "ScholarPercent": 50,
                "ScholarPayout":10,
                "TrainerPayoutAddress": "ronin:<trainer_address>",
                "TrainerPercent": 1
            }],
        "Donations": [
            {
                "Name": "Entity 1",
                "AccountAddress": dono_acc,
                "Percent": 1
            }]
    }
    s_file = {scholar_acc: scholar_private_acc}
    with patch.object(sys, "exit") as mocked_sys:
        axp = AxiePaymentsManager(p_file, s_file)
        axp.verify_inputs()
    mocked_sys.assert_called_once()
    assert "Please review the ronins in your donations. One or more are wrong!" in caplog.text


def test_payments_manager_verify_input_donations_exceed_max(caplog):
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    p_file = {
        "Manager": manager_acc,
        "Scholars": [
            {
                "Name":"Scholar 1", 
                "AccountAddress": scholar_acc,
                "ScholarPayoutAddress": "ronin:<scholar_address>",
                "ScholarPercent": 50,
                "ScholarPayout":10,
                "TrainerPayoutAddress": "ronin:<trainer_address>",
                "TrainerPercent": 1
            }],
        "Donations": [
            {
                "Name": "Entity 1",
                "AccountAddress": dono_acc,
                "Percent": 100
            }]
    }
    s_file = {scholar_acc: scholar_private_acc}
    with patch.object(sys, "exit") as mocked_sys:
        axp = AxiePaymentsManager(p_file, s_file)
        axp.verify_inputs()
    mocked_sys.assert_called()
    assert "Error given: 100 is greater than the maximum of 98\nFor attribute in: ['Donations', 0, 'Percent']" in caplog.text


def test_payments_manager_verify_input_missing_private_key(caplog):
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    p_file = {
        "Manager": manager_acc,
        "Scholars": [
            {
                "Name":"Scholar 1", 
                "AccountAddress": scholar_acc,
                "ScholarPayoutAddress": "ronin:<scholar_address>",
                "ScholarPercent": 50,
                "ScholarPayout":10,
                "TrainerPayoutAddress": "ronin:<trainer_address>",
                "TrainerPercent": 1
            }],
        "Donations": [
            {
                "Name": "Entity 1",
                "AccountAddress": dono_acc,
                "Percent": 1
            }]
    }
    s_file = {}
    with patch.object(sys, "exit") as mocked_sys:
        axp = AxiePaymentsManager(p_file, s_file)
        axp.verify_inputs()
    mocked_sys.assert_called_once()
    assert "Account 'Scholar 1' is not present in secret file, please add it." in caplog.text


def test_payments_manager_verify_input_invalid_private_key(caplog):
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_private_acc = '0x<account_s1_private_address>012345'
    p_file = {
        "Manager": manager_acc,
        "Scholars": [
            {
                "Name":"Scholar 1", 
                "AccountAddress": scholar_acc,
                "ScholarPayoutAddress": "ronin:<scholar_address>",
                "ScholarPercent": 50,
                "ScholarPayout":10,
                "TrainerPayoutAddress": "ronin:<trainer_address>",
                "TrainerPercent": 1
            }],
        "Donations": [
            {
                "Name": "Entity 1",
                "AccountAddress": dono_acc,
                "Percent": 1
            }]
    }
    s_file = {scholar_acc: scholar_private_acc}
    with patch.object(sys, "exit") as mocked_sys:
        axp = AxiePaymentsManager(p_file, s_file)
        axp.verify_inputs()
    mocked_sys.assert_called()
    assert f"Private key for account {scholar_acc} is not valid, please review it!" in caplog.text
    assert ("There is a problem with your secrets.json, delete it and re-generate the file starting with "
            "an empty secrets file.Or open it and see what is wrong with the keys of the accounts reported above." in caplog.text)


@patch("axie.AxiePaymentsManager.prepare_new_payout")
@patch("axie.AxiePaymentsManager.prepare_old_payout")
def test_payments_manager_prepare_payout_check_correct_calcs_legacy(mocked_prepare_old_payout, mocked_prepare_new_payout):
    axp = AxiePaymentsManager({}, {})
    axp.type = 'legacy'
    axp.prepare_payout()
    mocked_prepare_new_payout.assert_not_called()
    mocked_prepare_old_payout.assert_called_once()


@patch("axie.AxiePaymentsManager.prepare_new_payout")
@patch("axie.AxiePaymentsManager.prepare_old_payout")
def test_payments_manager_prepare_payout_check_correct_calcs_new(mocked_prepare_old_payout, mocked_prepare_new_payout):
    axp = AxiePaymentsManager({}, {})
    axp.type = 'new'
    axp.prepare_payout()
    mocked_prepare_old_payout.assert_not_called()
    mocked_prepare_new_payout.assert_called_once()


@patch("axie.payments.check_balance", return_value=1000)
@patch("axie_utils.Scatter.execute")
@patch("axie_utils.Scatter.__init__", return_value=None)
@patch("axie.AxiePaymentsManager.check_acc_has_enough_balance", return_value=True)
def test_payments_manager_prepare_payout_check_correct_payments_legacy(mocked_enough_balance,
                                                                       mocked_scatter_init,
                                                                       mocked_scatter_execute,
                                                                       mocked_check_balance):
    scholar_acc = 'ronin:12345678900987654321' + "".join([str(x) for x in range(10)]*2)
    manager_acc = 'ronin:12345678900987000321' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    p_file = {
        "Manager": manager_acc,
        "Scholars": [
            {
                "Name":"Scholar 1", 
                "AccountAddress": scholar_acc,
                "ScholarPayoutAddress": "ronin:<scholar_address>",
                "ScholarPercent": 45,
                "TrainerPayoutAddress": "ronin:<trainer_address>",
                "TrainerPercent": 10
            }],
        "Donations": [
            {
                "Name": "Entity 1",
                "AccountAddress": dono_acc,
                "Percent": 1
            }]
    }
    s_file = {scholar_acc: scholar_private_acc}
    axp = AxiePaymentsManager(p_file, s_file)
    axp.verify_inputs()
    with patch.object(builtins, 'input', lambda _: 'y'):
        axp.prepare_payout()
    mocked_check_balance.assert_called()
    mocked_enough_balance.assert_called_with(scholar_acc, 1000)
    mocked_scatter_init.assert_called_with(
        'slp',
        scholar_acc,
        s_file[scholar_acc],
        {
           "ronin:<scholar_address>": 450,
           "ronin:<trainer_address>": 100,
            dono_acc: 10,
            CREATOR_FEE_ADDRESS: 10,
            manager_acc: 430
        }
    )
    mocked_scatter_execute.assert_called()


@patch("axie.payments.check_balance", return_value=1000)
@patch("axie_utils.Scatter.execute")
@patch("axie_utils.Scatter.__init__", return_value=None)
@patch("axie.AxiePaymentsManager.check_acc_has_enough_balance", return_value=True)
def test_payments_manager_prepare_payout_check_correct_payments_new(mocked_enough_balance,
                                                                    mocked_scatter_init,
                                                                    mocked_scatter_execute,
                                                                    mocked_check_balance):
    scholar_acc = 'ronin:12345678900987654321' + "".join([str(x) for x in range(10)]*2)
    manager_acc = 'ronin:12345678900987000321' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    p_file = {
        "scholars": [{
            "name": "Scholar 1",
            "ronin": scholar_acc,
            "splits": [
                {
                    "persona": "Manager",
                    "percentage": 43,
                    "ronin": manager_acc
                },
                {
                    "persona": "Scholar",
                    "percentage": 40,
                    "ronin": "ronin:<scholar_1_address>"
                },
                {
                    "persona": "Other Person",
                    "percentage": 6,
                    "ronin": "ronin:<other_person_address>"
                },
                {
                    "persona": "Trainer",
                    "percentage": 10,
                    "ronin": "ronin:<trainer_address>"
                }
        ]}],
        "donations": [{
            "name": "Entity 1",
            "ronin": dono_acc,
            "percentage": 1
        }]
    }
    s_file = {scholar_acc: scholar_private_acc}
    axp = AxiePaymentsManager(p_file, s_file)
    axp.verify_inputs()
    with patch.object(builtins, 'input', lambda _: 'y'):
        axp.prepare_payout()
    mocked_check_balance.assert_called()
    mocked_enough_balance.assert_called_with(scholar_acc, 990)
    mocked_scatter_init.assert_called_with(
        'slp',
        scholar_acc,
        s_file[scholar_acc],
        {
           "ronin:<scholar_1_address>": 400,
           "ronin:<other_person_address>": 60,
           "ronin:<trainer_address>": 100,
            dono_acc: 10,
            CREATOR_FEE_ADDRESS: 10,
            manager_acc: 410
        }
    )
    mocked_scatter_execute.assert_called()



@patch("axie.payments.check_balance", return_value=0)
@patch("axie_utils.Scatter.execute")
@patch("axie.AxiePaymentsManager.check_acc_has_enough_balance", return_value=True)
def test_payments_manager_prepare_payout_check_correct_payments_percent_no_balance(mocked_enough_balance,
                                                                                   mocked_payout,
                                                                                   mocked_check_balance):
    scholar_acc = 'ronin:12345678900987654321' + "".join([str(x) for x in range(10)]*2)
    manager_acc = 'ronin:12345678900987000321' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    p_file = {
        "Manager": manager_acc,
        "Scholars": [
            {
                "Name":"Scholar 1", 
                "AccountAddress": scholar_acc,
                "ScholarPayoutAddress": "ronin:<scholar_address>",
                "ScholarPercent": 45,
                "TrainerPayoutAddress": "ronin:<trainer_address>",
                "TrainerPercent": 10
            }],
        "Donations": [
            {
                "Name": "Entity 1",
                "AccountAddress": dono_acc,
                "Percent": 1
            }]
    }
    s_file = {scholar_acc: scholar_private_acc}
    axp = AxiePaymentsManager(p_file, s_file)
    axp.verify_inputs()
    axp.prepare_payout()
    mocked_check_balance.assert_called()
    mocked_enough_balance.assert_called_with(scholar_acc, 0)
    mocked_payout.assert_not_called()


@patch("axie.payments.check_balance", return_value=100)
@patch("axie_utils.Scatter.execute")
@patch("axie.AxiePaymentsManager.check_acc_has_enough_balance", return_value=False)
def test_payments_manager_prepare_no_payout_not_enough_balance(mocked_check_balance,
                                                               mocked_payout,
                                                               _):
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    p_file = {
        "Manager": manager_acc,
        "Scholars": [
            {
                "Name":"Scholar 1", 
                "AccountAddress": scholar_acc,
                "ScholarPayoutAddress": "ronin:<scholar_address>",
                "ScholarPercent": 90,
                "TrainerPayoutAddress": "ronin:<trainer_address>",
                "TrainerPercent": 10
            }],
        "Donations": [
            {
                "Name": "Entity 1",
                "AccountAddress": dono_acc,
                "Percent": 1
            }]
    }
    s_file = {scholar_acc: scholar_private_acc}
    axp = AxiePaymentsManager(p_file, s_file)
    axp.verify_inputs()
    axp.prepare_payout()
    mocked_check_balance.assert_called_with(scholar_acc, 101)
    mocked_payout.assert_not_called()


@patch("web3.eth.Eth.contract")
@patch("web3.Web3.toChecksumAddress")
@patch("axie.payments.check_balance", return_value=1000)
@patch("axie_utils.Scatter.execute")
@patch("axie.AxiePaymentsManager.check_acc_has_enough_balance", return_value=True)
def test_payments_manager_payout_account_accept(_, mocked_execute, mocked_check_balance, __, ___, caplog):
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    p_file = {
        "Manager": manager_acc,
        "Scholars": [
            {
                "Name":"Scholar 1", 
                "AccountAddress": scholar_acc,
                "ScholarPayoutAddress": "ronin:<scholar_address>",
                "ScholarPercent": 50,
                "TrainerPayoutAddress": "ronin:<trainer_address>",
                "TrainerPercent": 10
            }],
        "Donations": [
            {
                "Name": "Entity 1",
                "AccountAddress": dono_acc,
                "Percent": 1
            }]
    }
    s_file = {scholar_acc: scholar_private_acc}
    axp = AxiePaymentsManager(p_file, s_file)
    axp.verify_inputs()
    with caplog.at_level(logging.DEBUG):
        with patch.object(builtins, 'input', lambda _: 'y'):
            axp.prepare_payout()
        mocked_check_balance.assert_called_with(scholar_acc)
        mocked_execute.assert_called()
        assert "SLP scatter completed for account: 'Scholar 1'" in caplog.text


@patch("web3.eth.Eth.contract")
@patch("web3.Web3.toChecksumAddress")
@patch("axie.payments.check_balance", return_value=1000)
@patch("axie_utils.Scatter.execute")
@patch("axie.AxiePaymentsManager.check_acc_has_enough_balance", return_value=True)
def test_payments_manager_payout_auto_yes(_, mocked_execute, mocked_check_balance, __, ___, caplog):
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    p_file = {
        "Manager": manager_acc,
        "Scholars": [
            {
                "Name":"Scholar 1", 
                "AccountAddress": scholar_acc,
                "ScholarPayoutAddress": "ronin:<scholar_address>",
                "ScholarPercent": 50,
                "TrainerPayoutAddress": "ronin:<trainer_address>",
                "TrainerPercent": 10
            }],
        "Donations": [
            {
                "Name": "Entity 1",
                "AccountAddress": dono_acc,
                "Percent": 1
            }]
    }
    s_file = {scholar_acc: scholar_private_acc}
    axp = AxiePaymentsManager(p_file, s_file, auto=True)
    axp.verify_inputs()
    with caplog.at_level(logging.INFO):
        axp.prepare_payout()
        mocked_check_balance.assert_called_with(scholar_acc)
        mocked_execute.assert_called_once()
        assert "SLP scatter completed for account: 'Scholar 1'" in caplog.text
        assert "Transactions Summary:" in caplog.text


@patch("axie.payments.check_balance", return_value=1000)
@patch("axie_utils.Scatter.execute")
@patch("axie.AxiePaymentsManager.check_acc_has_enough_balance", return_value=True)
def test_payments_manager_payout_account_deny(_, mocked_execute, mocked_check_balance, caplog):
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    p_file = {
        "Manager": manager_acc,
        "Scholars": [
            {
                "Name":"Scholar 1", 
                "AccountAddress": scholar_acc,
                "ScholarPayoutAddress": "ronin:<scholar_address>",
                "ScholarPercent": 50,
                "TrainerPayoutAddress": "ronin:<trainer_address>",
                "TrainerPercent": 10
            }],
        "Donations": [
            {
                "Name": "Entity 1",
                "AccountAddress": dono_acc,
                "Percent": 1
            }]
    }
    s_file = {scholar_acc: scholar_private_acc}
    axp = AxiePaymentsManager(p_file, s_file)
    axp.verify_inputs()
    with patch.object(builtins, 'input', lambda _: 'n'):
        axp.prepare_payout()
    mocked_check_balance.assert_called_with(scholar_acc)
    mocked_execute.assert_not_called()
    assert "SLP scatter canceled for account: 'Scholar 1'" in caplog.text
