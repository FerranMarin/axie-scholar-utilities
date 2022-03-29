import sys

from mock import patch

from trezor import TrezorAxieClaimsManager


@patch("trezor.TrezorAxieClaimsManager.load_trezor_config_and_acc_name", return_value=("foo", "bar"))
def test_claims_manager_init(mocked_load_secrets_and_acc_name):
    config_file = "config_file.json"
    payments_file = "payments_file.json"
    tacm = TrezorAxieClaimsManager(payments_file, config_file)
    mocked_load_secrets_and_acc_name.assert_called_with(config_file, payments_file)
    assert tacm.trezor_config == "foo"
    assert tacm.acc_names == "bar"


def test_claims_manager_verify_input_success():
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*4)
    p_file = {
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
    c_file = {scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    axc = TrezorAxieClaimsManager(p_file, c_file)
    axc.verify_inputs()
    assert axc.trezor_config == c_file
    assert axc.acc_names == {scholar_acc: "Scholar 1"}


def test_claims_manager_verify_only_accounts_in_payments_get_claimed():
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*4)
    p_file = {
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
    c_file = {
        scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"},
        "ronin:abc1": {"passphrase": "", "bip_path": "m/44'/60'/0'/0/1"}
    }
    axc = TrezorAxieClaimsManager(p_file, c_file)
    axc.verify_inputs()
    assert axc.trezor_config == {scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    assert axc.acc_names == {scholar_acc: "Scholar 1"}


def test_claims_manager_verify_inputs_wrong_public_ronin(caplog):
    scholar_acc = '<account_s1_address>' + "".join([str(x) for x in range(10)]*4)
    p_file = {
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
    c_file = {scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    with patch.object(sys, "exit") as mocked_sys:
        axc = TrezorAxieClaimsManager(p_file, c_file)
        axc.verify_inputs()

    mocked_sys.assert_called_once()
    assert f"Public address {scholar_acc} needs to start with ronin:" in caplog.text


@patch("trezor.trezor_claims.get_default_client", return_value="client")
@patch("trezor.trezor_claims.TrezorClaim.execute")
def test_claims_manager_prepare_claims(mocked_claim_execute, mock_client):
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*4)
    p_file = {
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
    c_file = {scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    axc = TrezorAxieClaimsManager(p_file, c_file)
    axc.prepare_claims()
    mocked_claim_execute.assert_called_once()
    mock_client.assert_called()
