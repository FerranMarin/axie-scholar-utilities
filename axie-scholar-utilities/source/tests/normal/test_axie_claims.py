import sys

from mock import patch

from axie import AxieClaimsManager


@patch("axie.AxieClaimsManager.load_secrets_and_acc_name", return_value=("foo", "bar"))
def test_claims_manager_init(mocked_load_secrets_and_acc_name):
    secrets_file = "sample_secrets_file.json"
    payments_file = "sample_payments_file.json"
    a = AxieClaimsManager(payments_file, secrets_file)
    mocked_load_secrets_and_acc_name.assert_called_with(secrets_file, payments_file)


def test_claims_manager_verify_input_success():
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*4)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
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
    s_file = {scholar_acc: scholar_private_acc}
    axc = AxieClaimsManager(p_file, s_file)
    axc.verify_inputs()
    assert axc.secrets_file == {scholar_acc: scholar_private_acc}


def test_claims_manager_verify_only_accounts_in_payments_get_claimed():
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*4)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
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
    s_file = {
        scholar_acc: scholar_private_acc,
        "ronin:acc": "ronin:secret"
    }
    axc = AxieClaimsManager(p_file, s_file)
    axc.verify_inputs()
    assert axc.secrets_file == {scholar_acc: scholar_private_acc}


def test_claims_manager_verify_inputs_wrong_public_ronin(caplog):
    scholar_acc = '<account_s1_address>' + "".join([str(x) for x in range(10)]*4)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
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
    s_file = {scholar_acc: scholar_private_acc}
    with patch.object(sys, "exit") as mocked_sys:
        axc = AxieClaimsManager(p_file, s_file)
        axc.verify_inputs()

    mocked_sys.assert_called_once()
    assert f"Public address {scholar_acc} needs to start with ronin:" in caplog.text


def test_claims_manager_verify_input_wrong_private_ronin(caplog):
    scholar_acc = '<account_s1_address>' + "".join([str(x) for x in range(10)]*4)
    scholar_private_acc = 'ronin:<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
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
    s_file = {scholar_acc: scholar_private_acc}
    with patch.object(sys, "exit") as mocked_sys:
        axc = AxieClaimsManager(p_file, s_file)
        axc.verify_inputs()

    mocked_sys.assert_called_once()
    assert f"Private key for account {scholar_acc} is not valid, please review it!" in caplog.text


def test_claims_manager_verify_input_wrong_private_short(caplog):
    scholar_acc = '<account_s1_address>' + "".join([str(x) for x in range(10)]*4)
    scholar_private_acc = 'ronin:<account_s1_private_address>012345'
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
    s_file = {scholar_acc: scholar_private_acc}
    with patch.object(sys, "exit") as mocked_sys:
        axc = AxieClaimsManager(p_file, s_file)
        axc.verify_inputs()

    mocked_sys.assert_called_once()
    assert f"Private key for account {scholar_acc} is not valid, please review it!" in caplog.text


@patch("axie_utils.Claim.async_execute")
def test_claims_manager_prepare_claims(mocked_claim_execute):
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*4)
    scholar_private_acc = '0x<account_s1_private_address>012345' + "".join([str(x) for x in range(10)]*3)
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
    s_file = {scholar_acc: scholar_private_acc}
    axc = AxieClaimsManager(p_file, s_file)
    axc.prepare_claims()
    mocked_claim_execute.assert_called_once()
