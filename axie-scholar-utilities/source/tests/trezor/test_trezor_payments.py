import sys

from mock import patch

from trezor import TrezorAxiePaymentsManager
from trezor.trezor_payments import CREATOR_FEE_ADDRESS


def test_payments_manager_init():
    payments_file = "foo"
    config_file = "bar"
    axp = TrezorAxiePaymentsManager(payments_file, config_file)
    assert axp.payments_file == payments_file
    assert axp.trezor_config == config_file
    assert axp.auto is False
    axp2 = TrezorAxiePaymentsManager(payments_file, config_file, auto=True)
    assert axp2.payments_file == payments_file
    assert axp2.trezor_config == config_file
    assert axp2.auto is True


def test_payments_manager_verify_input_success():
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
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
    config_data = {scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    taxp = TrezorAxiePaymentsManager(p_file, config_data)
    taxp.verify_inputs()
    assert taxp.type == "new"
    assert taxp.manager_acc == None
    assert taxp.scholar_accounts == p_file['scholars']
    assert taxp.donations == p_file['donations']


def test_payments_manager_verify_input_success(caplog):
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
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
    config_data = {scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    with patch.object(sys, "exit") as mocked_sys:
        axp = TrezorAxiePaymentsManager(p_file, config_data)
        axp.verify_inputs()
    mocked_sys.assert_called()
    assert "Account 'Scholar 1' has no manager in its splits. Please review it!" in caplog.text

def test_payments_manager_verify_input_success_legacy():
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
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
    config_data = {scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    axp = TrezorAxiePaymentsManager(p_file, config_data)
    axp.verify_inputs()
    assert axp.manager_acc == manager_acc
    assert axp.type == "legacy"
    assert axp.scholar_accounts == p_file['Scholars']
    assert axp.donations == p_file['Donations']

def test_payments_manager_verify_input_manager_ronin_short(caplog):
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>'
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
    config_data = {scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    with patch.object(sys, "exit") as mocked_sys:
        axp = TrezorAxiePaymentsManager(p_file, config_data)
        axp.verify_inputs()
    mocked_sys.assert_called_once()
    assert "Please review the ronins in your donations. One or more are wrong!" in caplog.text


def test_payments_manager_verify_input_correct_dono(caplog):
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
    with patch.object(sys, "exit") as mocked_sys:
        axp = TrezorAxiePaymentsManager(p_file, {})
        axp.verify_inputs()
    mocked_sys.assert_called_once()
    assert "Account 'Scholar 1' is not present in trezor_config file, please add it." in caplog.text


@patch("trezor.TrezorAxiePaymentsManager.prepare_payout")
def test_payments_manager_prepare_payout(mocked_prepare_payout):
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
    config_data = {scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    axp = TrezorAxiePaymentsManager(p_file, config_data)
    axp.verify_inputs()
    axp.prepare_payout()
    mocked_prepare_payout.assert_called_once()


@patch("trezor.trezor_payments.parse_path", return_value="m/44'/60'/0'/0/0")
@patch("trezor.trezor_payments.get_default_client", return_value="client")
@patch("trezor.trezor_payments.check_balance", return_value=1000)
@patch("axie_utils.TrezorScatter.execute")
@patch("axie_utils.TrezorScatter.__init__", return_value=None)
@patch("trezor.TrezorAxiePaymentsManager.check_acc_has_enough_balance", return_value=True)
def test_payments_manager_prepare_payout_check_correct_payments(mocked_enough_balance,
                                                                mocked_scatter_init,
                                                                mocked_scatter_execute,
                                                                mocked_check_balance,
                                                                mocked_client,
                                                                mocked_parse):
    scholar_acc = 'ronin:12345678900987654321' + "".join([str(x) for x in range(10)]*2)
    manager_acc = 'ronin:12345678900987000321' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
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
    config_data = {scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    axp = TrezorAxiePaymentsManager(p_file, config_data, auto=True)
    axp.verify_inputs()
    axp.prepare_payout()
    mocked_client.assert_called()
    mocked_parse.assert_called()
    mocked_check_balance.assert_called()
    mocked_enough_balance.assert_called_with(scholar_acc, 1000)
    mocked_scatter_init.assert_called_with(
        'slp',
        scholar_acc,
        'client',
        config_data[scholar_acc]['bip_path'],
        {
           "ronin:<scholar_address>": 500,
           'ronin:<trainer_address>': 100,
           dono_acc: 10,
           CREATOR_FEE_ADDRESS : 10,
           manager_acc: 380 
        }
    )
    mocked_scatter_execute.assert_called()

@patch("trezor.trezor_payments.get_default_client", return_value="client")
@patch("trezor.trezor_payments.check_balance", return_value=0)
@patch("axie_utils.TrezorScatter.execute")
@patch("axie_utils.TrezorScatter.__init__", return_value=None)
@patch("trezor.TrezorAxiePaymentsManager.check_acc_has_enough_balance", return_value=True)
def test_payments_manager_prepare_payout_check_correct_payments_no_balance(mocked_enough_balance,
                                                                           mocked_scatter_init,
                                                                           mocked_scatter_execute,
                                                                           mocked_check_balance,
                                                                           mocked_client):
    scholar_acc = 'ronin:12345678900987654321' + "".join([str(x) for x in range(10)]*2)
    manager_acc = 'ronin:12345678900987000321' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
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
    config_data = {scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    axp = TrezorAxiePaymentsManager(p_file, config_data)
    axp.verify_inputs()
    axp.prepare_payout()
    mocked_client.assert_called()
    mocked_check_balance.assert_called()
    mocked_enough_balance.assert_called_with(scholar_acc, 0)
    mocked_scatter_init.assert_not_called()
    mocked_scatter_execute.assert_not_called()