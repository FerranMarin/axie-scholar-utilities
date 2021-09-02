import sys

from mock import patch
import pytest

from axie import AxieClaimsManager


@patch("axie.claims.load_json")
def test_claims_manager_init(mocked_load_json):
    secrets_file = "sample_secrets_file.json"
    AxieClaimsManager(secrets_file)
    mocked_load_json.assert_called_with(secrets_file)


def test_claims_manager_verify_input_success(tmpdir):
    scholar_acc = 'ronin:<account_s1_address>'+ "".join([str(x) for x in range(10)]*4)
    scholar_private_acc = '0x<account_s1_private_address>012345'+ "".join([str(x) for x in range(10)]*3)
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    axc = AxieClaimsManager(s_file)
    axc.verify_input()
    axc.secrets_file = {scholar_acc:scholar_private_acc}


def test_claims_manager_verify_input_wrong_public_ronin(tmpdir, caplog):
    scholar_acc = '<account_s1_address>'+ "".join([str(x) for x in range(10)]*4)
    scholar_private_acc = '0x<account_s1_private_address>012345'+ "".join([str(x) for x in range(10)]*3)
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    with patch.object(sys, "exit") as mocked_sys:
        axc = AxieClaimsManager(s_file)
        axc.verify_input()
    
    mocked_sys.assert_called_once()
    assert f"Public address {scholar_acc} needs to start with ronin:" in caplog.text


def test_claims_manager_verify_input_wrong_public_private_ronin(tmpdir, caplog):
    scholar_acc = '<account_s1_address>'+ "".join([str(x) for x in range(10)]*4)
    scholar_private_acc = 'ronin:<account_s1_private_address>012345'+ "".join([str(x) for x in range(10)]*3)
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    with patch.object(sys, "exit") as mocked_sys:
        axc = AxieClaimsManager(s_file)
        axc.verify_input()
    
    mocked_sys.assert_called_once()
    assert f"Private key for account {scholar_acc} is not valid, please review it!" in caplog.text


def test_claims_manager_verify_input_wrong_public_private_short(tmpdir, caplog):
    scholar_acc = '<account_s1_address>'+ "".join([str(x) for x in range(10)]*4)
    scholar_private_acc = 'ronin:<account_s1_private_address>012345'
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    with patch.object(sys, "exit") as mocked_sys:
        axc = AxieClaimsManager(s_file)
        axc.verify_input()
    
    mocked_sys.assert_called_once()
    assert f"Private key for account {scholar_acc} is not valid, please review it!" in caplog.text


@patch("axie.claims.Claim.has_unclaimed_slp")
@patch("axie.claims.check_balance")
@patch("axie.claims.Claim.execute")
def test_claims_manager_prepare_claims(mocked_claim_execute, mocked_check_balance, mocked_has_unclaimed_slp, tmpdir):
    scholar_acc = 'ronin:<account_s1_address>'+ "".join([str(x) for x in range(10)]*4)
    scholar_private_acc = '0x<account_s1_private_address>012345'+ "".join([str(x) for x in range(10)]*3)
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    axc = AxieClaimsManager(s_file)
    axc.prepare_claims()
    mocked_check_balance.assert_called_with(scholar_acc)
    mocked_has_unclaimed_slp.assert_called_once()
    mocked_claim_execute.assert_called_once()


def test_claim_init():
    pass


def test_has_unclaimed_slp():
    pass


def test_create_random_msg():
    pass


def test_get_jwt():
    pass


def test_execution():
    pass
