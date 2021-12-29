import os
import sys
import json
import builtins

from mock import patch, call, mock_open
from glob import glob
import pytest

from trezor import TrezorAxiePaymentsManager
from trezor.trezor_payments import TrezorPayment
from axie.payments import PaymentsSummary
from axie.utils import SLP_CONTRACT
from tests.test_utils import LOG_FILE_PATH, cleanup_log_file


@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    """Cleanup a testing directory once we are finished."""
    def remove_log_files():
        files = glob(LOG_FILE_PATH+'logs/*.log')
        for f in files:
            os.remove(f)
    request.addfinalizer(remove_log_files)


@patch("trezor.trezor_payments.load_json")
def test_payments_manager_init(mocked_load_json):
    payments_file = "sample_payments_file.json"
    config_file = "sample_config_file.json"
    axp = TrezorAxiePaymentsManager(payments_file, config_file)
    mocked_load_json.assert_has_calls(
        calls=[call(payments_file), call(config_file)]
    )
    assert axp.auto is False
    axp2 = TrezorAxiePaymentsManager(payments_file, config_file, auto=True)
    assert axp2.auto is True


def test_payments_manager_verify_input_success(tmpdir):
    p_file = tmpdir.join("p.json")
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    p_file.write(('{"Manager":"'+manager_acc+'","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPercent":50,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPercent":1}],'
                  '"Donations":[{"Name":"Entity 1", "AccountAddress": "'+dono_acc+'","Percent":1}]}'))
    c_file = tmpdir.join("c.json")
    config_data = {scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    c_file.write(json.dumps(config_data))
    taxp = TrezorAxiePaymentsManager(p_file, c_file)
    taxp.verify_inputs()
    assert taxp.manager_acc == manager_acc
    assert taxp.scholar_accounts == [
        {"Name": "Scholar 1",
         "AccountAddress": scholar_acc,
         "ScholarPayoutAddress": "ronin:<scholar_address>",
         "ScholarPercent": 50,
         "TrainerPayoutAddress": "ronin:<trainer_address>",
         "TrainerPercent": 1}]
    assert taxp.donations == [
        {"Name": "Entity 1",
         "AccountAddress": dono_acc,
         "Percent": 1}]


def test_payments_manager_verify_input_success_percent_with_payouts(tmpdir):
    p_file = tmpdir.join("p.json")
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    p_file.write(('{"Manager":"'+manager_acc+'","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPercent":50,"ScholarPayout":10,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPercent":1}],'
                  '"Donations":[{"Name":"Entity 1", "AccountAddress": "'+dono_acc+'","Percent":1}]}'))
    c_file = tmpdir.join("s.json")
    config_data = {scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    c_file.write(json.dumps(config_data))
    axp = TrezorAxiePaymentsManager(p_file, c_file)
    axp.verify_inputs()
    assert axp.manager_acc == manager_acc
    assert axp.scholar_accounts == [
        {"Name": "Scholar 1",
         "AccountAddress": scholar_acc,
         "ScholarPayoutAddress": "ronin:<scholar_address>",
         "ScholarPercent": 50,
         "ScholarPayout": 10,
         "TrainerPayoutAddress": "ronin:<trainer_address>",
         "TrainerPercent": 1}]
    assert axp.donations == [
        {"Name": "Entity 1",
         "AccountAddress": dono_acc,
         "Percent": 1}]


def test_payments_manager_verify_input_manager_ronin_short(tmpdir, caplog):
    p_file = tmpdir.join("p.json")
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>'
    p_file.write(('{"Manager":"'+manager_acc+'","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPercent":50,"ScholarPayout":10,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPercent":1}],'
                  '"Donations":[{"Name":"Entity 1", "AccountAddress": "'+dono_acc+'","Percent":1}]}'))
    c_file = tmpdir.join("s.json")
    config_data = {scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    c_file.write(json.dumps(config_data))
    with patch.object(sys, "exit") as mocked_sys:
        axp = TrezorAxiePaymentsManager(p_file, c_file)
        axp.verify_inputs()
    mocked_sys.assert_called_once()
    assert "Please review the ronins in your donations. One or more are wrong!" in caplog.text


def test_payments_manager_verify_input_correct_dono(tmpdir, caplog):
    p_file = tmpdir.join("p.json")
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    p_file.write(('{"Manager":"'+manager_acc+'","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPercent":50,"ScholarPayout":10,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPercent":1}],'
                  '"Donations":[{"Name":"Entity 1", "AccountAddress": "'+dono_acc+'","Percent":1}]}'))
    c_file = tmpdir.join("c.json")
    c_file.write('{ }')
    with patch.object(sys, "exit") as mocked_sys:
        axp = TrezorAxiePaymentsManager(p_file, c_file)
        axp.verify_inputs()
    mocked_sys.assert_called_once()
    assert "Account 'Scholar 1' is not present in trezor config file, please re-run setup." in caplog.text


@patch("trezor.TrezorAxiePaymentsManager.prepare_payout")
def test_payments_manager_prepare_payout(mocked_prepare_payout, tmpdir):
    p_file = tmpdir.join("p.json")
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    p_file.write(('{"Manager":"'+manager_acc+'","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPercent":45,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPercent":10}],'
                  '"Donations":[{"Name":"Entity 1",'
                  '"AccountAddress": "'+dono_acc+'","Percent":1}]}'))
    c_file = tmpdir.join("c.json")
    config_data = {scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    c_file.write(json.dumps(config_data))
    axp = TrezorAxiePaymentsManager(p_file, c_file)
    axp.verify_inputs()
    axp.prepare_payout()
    mocked_prepare_payout.assert_called_once()


@patch("trezor.trezor_payments.parse_path", return_value="m/44'/60'/0'/0/0")
@patch("trezor.trezor_payments.get_default_client", return_value="client")
@patch("trezor.trezor_payments.check_balance", return_value=1000)
@patch("trezor.TrezorAxiePaymentsManager.payout_account")
@patch("trezor.TrezorAxiePaymentsManager.check_acc_has_enough_balance", return_value=True)
def test_payments_manager_prepare_payout_check_correct_payments(mocked_enough_balance,
                                                                mocked_payout,
                                                                mocked_check_balance,
                                                                mocked_client,
                                                                mocked_parse,
                                                                tmpdir):
    p_file = tmpdir.join("p.json")
    scholar_acc = 'ronin:12345678900987654321' + "".join([str(x) for x in range(10)]*2)
    manager_acc = 'ronin:12345678900987000321' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    clean_scholar_acc = scholar_acc.replace("ronin:", "0x")
    p_file.write(('{"Manager":"'+manager_acc+'","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPercent":45,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPercent":10}],'
                  '"Donations":[{"Name":"Entity 1",'
                  '"AccountAddress": "'+dono_acc+'","Percent":1}]}'))
    c_file = tmpdir.join("c.json")
    config_data = {scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    c_file.write(json.dumps(config_data))
    axp = TrezorAxiePaymentsManager(p_file, c_file)
    axp.verify_inputs()
    axp.prepare_payout()
    mocked_client.assert_called()
    mocked_parse.assert_called()
    mocked_check_balance.assert_called()
    mocked_enough_balance.assert_called_with(scholar_acc, 1000)
    mocked_payout.assert_called_once()
    # 1st payment
    assert mocked_payout.call_args[0][0] == "Scholar 1"
    assert mocked_payout.call_args[0][1][0].name == "Payment to scholar of Scholar 1"
    assert mocked_payout.call_args[0][1][0].from_acc == clean_scholar_acc
    assert mocked_payout.call_args[0][1][0].bip_path == "m/44'/60'/0'/0/0"
    assert mocked_payout.call_args[0][1][0].amount == 450
    # 2nd payment
    assert mocked_payout.call_args[0][1][1].name == "Payment to trainer of Scholar 1"
    assert mocked_payout.call_args[0][1][1].from_acc == clean_scholar_acc
    assert mocked_payout.call_args[0][1][1].bip_path == "m/44'/60'/0'/0/0"
    assert mocked_payout.call_args[0][1][1].amount == 100
    # 3rd payment (dono)
    assert mocked_payout.call_args[0][1][2].name == "Donation to Entity 1 for Scholar 1"
    assert mocked_payout.call_args[0][1][2].from_acc == clean_scholar_acc
    assert mocked_payout.call_args[0][1][2].bip_path == "m/44'/60'/0'/0/0"
    assert mocked_payout.call_args[0][1][2].amount == round(450*0.01)
    # 4th Payment (fee)
    assert mocked_payout.call_args[0][1][3].name == "Donation to software creator for Scholar 1"
    assert mocked_payout.call_args[0][1][3].from_acc == clean_scholar_acc
    assert mocked_payout.call_args[0][1][3].bip_path == "m/44'/60'/0'/0/0"
    assert mocked_payout.call_args[0][1][3].amount == round(1000*0.01)
    # 5th Payment
    assert mocked_payout.call_args[0][1][4].name == "Payment to manager of Scholar 1"
    assert mocked_payout.call_args[0][1][4].from_acc == clean_scholar_acc
    assert mocked_payout.call_args[0][1][4].bip_path == "m/44'/60'/0'/0/0"
    assert mocked_payout.call_args[0][1][4].amount == 1000 - 550 - round(1000*0.01) - round(450*0.01)
    assert len(mocked_payout.call_args[0][1]) == 5


@patch("trezor.trezor_payments.get_default_client", return_value="client")
@patch("trezor.trezor_payments.check_balance", return_value=0)
@patch("trezor.TrezorAxiePaymentsManager.payout_account")
@patch("trezor.TrezorAxiePaymentsManager.check_acc_has_enough_balance", return_value=True)
def test_payments_manager_prepare_payout_check_correct_payments_no_balance(mocked_enough_balance,
                                                                           mocked_payout,
                                                                           mocked_check_balance,
                                                                           mocked_client,
                                                                           tmpdir):
    p_file = tmpdir.join("p.json")
    scholar_acc = 'ronin:12345678900987654321' + "".join([str(x) for x in range(10)]*2)
    manager_acc = 'ronin:12345678900987000321' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    p_file.write(('{"Manager":"'+manager_acc+'","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPercent":45,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPercent":10}],'
                  '"Donations":[{"Name":"Entity 1",'
                  '"AccountAddress": "'+dono_acc+'","Percent":1}]}'))
    c_file = tmpdir.join("c.json")
    config_data = {scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    c_file.write(json.dumps(config_data))
    axp = TrezorAxiePaymentsManager(p_file, c_file)
    axp.verify_inputs()
    axp.prepare_payout()
    mocked_client.assert_called()
    mocked_check_balance.assert_called()
    mocked_enough_balance.assert_called_with(scholar_acc, 0)
    mocked_payout.assert_not_called()


@patch("trezor.trezor_transfers.rlp.encode")
@patch("web3.Web3.toBytes")
@patch("web3.eth.Eth.get_transaction_count", return_value=123)
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch('trezor.trezor_transfers.ethereum.sign_tx', return_value=(1, b'2xf', b'3fg'))
@patch("web3.eth.Eth.send_raw_transaction")
@patch("web3.Web3.toHex", return_value="transaction_hash")
@patch("web3.Web3.keccak", return_value='result_of_keccak')
@patch("web3.eth.Eth.contract")
@patch("web3.eth.Eth.get_transaction_receipt", return_value={'status': 1})
def test_execute_calls_web3_functions(mock_transaction_receipt,
                                      mock_contract,
                                      mock_keccak,
                                      mock_to_hex,
                                      mock_send,
                                      mock_sign,
                                      mock_checksum,
                                      _,
                                      mocked_to_bytes,
                                      mock_rlp,
                                      caplog):
    # Make sure file is clean to start
    log_file = glob(LOG_FILE_PATH+'logs/results_*.log')[0][9:]
    cleanup_log_file(log_file)
    PaymentsSummary().clear()
    s = PaymentsSummary()
    with patch.object(builtins,
                      "open",
                      mock_open(read_data='{"foo": "bar"}')) as mock_file:
        p = TrezorPayment(
            "random_account",
            "manager",
            "client",
            "m/44'/60'/0'/0/0",
            "ronin:from_ronin",
            "ronin:to_ronin",
            10,
            s)
        p.execute()
    mock_file.assert_called_with("trezor/slp_abi.json", encoding='utf-8')
    mock_contract.assert_called_with(address="checksum", abi={"foo": "bar"})
    mock_keccak.assert_called_once()
    mock_to_hex.assert_called_with("result_of_keccak")
    mock_send.assert_called_once()
    mock_sign.assert_called_once()
    mocked_to_bytes.assert_called()
    mock_rlp.assert_called()
    mock_checksum.assert_has_calls(calls=[
        call(SLP_CONTRACT),
        call('0xfrom_ronin'),
        call('0xto_ronin')])
    mock_transaction_receipt.assert_called_with("transaction_hash")
    assert ('Transaction random_account(ronin:to_ronin) for the amount of 10 SLP completed! Hash: transaction_hash - '
            'Explorer: https://explorer.roninchain.com/tx/transaction_hash' in caplog.text)
    assert str(s) == "Paid 1 managers, 10 SLP.\n"
    with open(log_file) as f:
        lf = f.readlines()
        assert len(lf) == 2
    assert "Important: Debugging information" in lf[0]
    assert ("Important: Transaction random_account(ronin:to_ronin) for the amount of 10 SLP completed! "
            "Hash: transaction_hash - Explorer: https://explorer.roninchain.com/tx/transaction_hash") in lf[1]
    cleanup_log_file(log_file)


@patch("trezor.trezor_transfers.rlp.encode")
@patch("web3.Web3.toBytes")
@patch("web3.eth.Eth.get_transaction_count", return_value=123)
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch('trezor.trezor_transfers.ethereum.sign_tx', return_value=(1, b'2xf', b'3fg'))
@patch("web3.eth.Eth.send_raw_transaction")
@patch("web3.Web3.toHex", return_value="transaction_hash")
@patch("web3.Web3.keccak", return_value='result_of_keccak')
@patch("web3.eth.Eth.contract")
@patch("web3.eth.Eth.get_transaction_receipt", return_value={'status': 0})
@patch("trezor.trezor_payments.TrezorPayment.send_replacement_tx")
def test_execute_calls_web3_functions_retry(mock_replacement_tx,
                                            mock_transaction_receipt,
                                            mock_contract,
                                            mock_keccak,
                                            mock_to_hex,
                                            mock_send,
                                            mock_sign,
                                            mock_checksum,
                                            _,
                                            mocked_to_bytes,
                                            mock_rlp,
                                            caplog):
    # Make sure file is clean to start
    log_file = glob(LOG_FILE_PATH+'logs/results_*.log')[0][9:]
    cleanup_log_file(log_file)
    PaymentsSummary().clear()
    s = PaymentsSummary()
    with patch.object(builtins,
                      "open",
                      mock_open(read_data='{"foo": "bar"}')) as mock_file:
        p = TrezorPayment(
            "random_account",
            "manager",
            "client",
            "m/44'/60'/0'/0/0",
            "ronin:from_ronin",
            "ronin:to_ronin",
            10,
            s)
        p.execute()
    mock_file.assert_called_with("trezor/slp_abi.json", encoding='utf-8')
    mock_contract.assert_called_with(address="checksum", abi={"foo": "bar"})
    mock_keccak.assert_called_once()
    mock_to_hex.assert_called_with("result_of_keccak")
    mock_send.assert_called_once()
    mock_sign.assert_called_once()
    mocked_to_bytes.assert_called()
    mock_rlp.assert_called()
    mock_checksum.assert_has_calls(calls=[
        call(SLP_CONTRACT),
        call('0xfrom_ronin'),
        call('0xto_ronin')])
    mock_transaction_receipt.assert_called_with("transaction_hash")
    mock_replacement_tx.assert_called_with(123)
    assert ("Important: Transaction random_account(ronin:to_ronin) for the amount of 10 SLP failed. "
            "Trying to replace it with a 0 value tx and re-try." in caplog.text)
    with open(log_file) as f:
        lf = f.readlines()
        assert len(lf) == 2
    assert "Important: Debugging information" in lf[0]
    assert ("Important: Transaction random_account(ronin:to_ronin) for the amount of 10 SLP failed. "
            "Trying to replace it with a 0 value tx and re-try.") in lf[1]
    assert str(s) == "No payments made!"
    cleanup_log_file(log_file)
