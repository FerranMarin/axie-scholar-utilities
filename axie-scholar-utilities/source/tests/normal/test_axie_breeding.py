import sys
import json
import builtins

from mock import patch, mock_open, call

from axie import AxieBreedManager
from axie.breeding import Breed, AXIE_CONTRACT
from axie.payments import PaymentsSummary, CREATOR_FEE_ADDRESS
from axie.utils import RONIN_PROVIDER_FREE, USER_AGENT


@patch("axie.breeding.load_json", return_value={"foo": "bar"})
def test_breed_manager_init(mock_load):
    s_file = "_secrets_file.json"
    b_file = "breeds_file.json"
    acc = "ronin:abc1"
    abm = AxieBreedManager(b_file, s_file, acc)
    mock_load.assert_has_calls(calls=[
        call(s_file),
        call(b_file)
    ])
    assert abm.secrets == {"foo": "bar"}
    assert abm.breeding_file == {"foo": "bar"}
    assert abm.payment_account == acc
    assert abm.breeding_costs == 0


def test_breed_manager_verify_inputs_succcess(tmpdir):
    acc = 'ronin:<accountfoo_address>' + "".join([str(x) for x in range(10)]*4)
    private_acc = '0x<accountfoo_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+acc+'":"'+private_acc+'"}')
    b_file = tmpdir.join("b.json")
    data = [{
        "Sire": 1234,
        "Matron": 5678,
        "AccountAddress": acc
    }]
    b_file.write(json.dumps(data))
    abm = AxieBreedManager(b_file, s_file, acc)
    abm.verify_inputs()
    assert abm.secrets == {acc: private_acc}


def test_breed_manager_verify_inputs_fail_validation(tmpdir, caplog):
    acc = '0x<accountfoo_address>' + "".join([str(x) for x in range(10)]*4)
    private_acc = '0x<accountfoo_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+acc+'":"'+private_acc+'"}')
    b_file = tmpdir.join("b.json")
    data = [{
        "Sire": 1234,
        "Matron": 5678,
        "AccountAddress": acc
    }]
    b_file.write(json.dumps(data))
    with patch.object(sys, "exit") as mocked_sys:
        abm = AxieBreedManager(b_file, s_file, acc)
        abm.verify_inputs()
    mocked_sys.assert_called_once()
    assert f"Validation of breeding file failed. Error given: '{acc}' does not match '^ronin:'" in caplog.text


def test_breed_manager_verify_inputs_missing_account_in_secrets(tmpdir, caplog):
    acc = '0x<accountfoo_address>' + "".join([str(x) for x in range(10)]*4)
    s_file = tmpdir.join("s.json")
    s_file.write('{"foo":"bar"}')
    b_file = tmpdir.join("b.json")
    data = [{
        "Sire": 1234,
        "Matron": 5678,
        "AccountAddress": acc
    }]
    b_file.write(json.dumps(data))
    with patch.object(sys, "exit") as mocked_sys:
        abm = AxieBreedManager(b_file, s_file, acc)
        abm.verify_inputs()
    mocked_sys.assert_called_once()
    assert f"Account '{acc}' is not present in secret file, please add it." in caplog.text


def test_breed_manager_verify_inputs_missing_payments_account_in_secrets(tmpdir, caplog):
    acc = '0x<accountfoo_address>' + "".join([str(x) for x in range(10)]*4)
    private_acc = '0x<accountfoo_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+acc+'":"'+private_acc+'"}')
    b_file = tmpdir.join("b.json")
    data = [{
        "Sire": 1234,
        "Matron": 5678,
        "AccountAddress": acc
    }]
    b_file.write(json.dumps(data))
    with patch.object(sys, "exit") as mocked_sys:
        abm = AxieBreedManager(b_file, s_file, "ronin:abc1")
        abm.verify_inputs()
    mocked_sys.assert_called_once()
    assert "Payment account 'ronin:abc1' is not present in secret file, please add it." in caplog.text


@patch("axie.AxieBreedManager.calculate_fee_cost")
@patch("axie.AxieBreedManager.calculate_breeding_cost")
def test_breed_manager_calculate_cost(mock_breed_cost, mock_fee_cost, tmpdir):
    acc = 'ronin:<accountfoo_address>' + "".join([str(x) for x in range(10)]*4)
    private_acc = '0x<accountfoo_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+acc+'":"'+private_acc+'"}')
    b_file = tmpdir.join("b.json")
    data = [{
        "Sire": 1234,
        "Matron": 5678,
        "AccountAddress": acc
    }]
    b_file.write(json.dumps(data))
    abm = AxieBreedManager(b_file, s_file, acc)
    abm.calculate_cost()
    mock_breed_cost.assert_not_called()
    mock_fee_cost.assert_called_once()


def test_breed_manager_calculate_fee_cost(tmpdir):
    acc = 'ronin:<accountfoo_address>' + "".join([str(x) for x in range(10)]*4)
    private_acc = '0x<accountfoo_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+acc+'":"'+private_acc+'"}')
    b_file = tmpdir.join("b.json")
    data = [{
        "Sire": 1234,
        "Matron": 5678,
        "AccountAddress": acc
    }]
    b_file.write(json.dumps(data))
    abm = AxieBreedManager(b_file, s_file, acc)
    assert abm.calculate_fee_cost() == 30
    abm.breeding_file = [1, 2, 3]
    assert abm.calculate_fee_cost() == 30*3
    abm.breeding_file = list(range(17))
    assert abm.calculate_fee_cost() == (15 * 30) + ((17 - 15) * 25)
    abm.breeding_file = list(range(35))
    assert abm.calculate_fee_cost() == (15 * 30) + (15 * 25) + ((35 - 30) * 20)
    abm.breeding_file = list(range(75))
    assert abm.calculate_fee_cost() == (15 * 30) + (15 * 25) + (20 * 20) + ((75 - 50) * 15)


def test_breed_manager_calculate_breeding_cost(tmpdir):
    acc = 'ronin:<accountfoo_address>' + "".join([str(x) for x in range(10)]*4)
    private_acc = '0x<accountfoo_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+acc+'":"'+private_acc+'"}')
    b_file = tmpdir.join("b.json")
    data = [{
        "Sire": 1234,
        "Matron": 5678,
        "AccountAddress": acc
    }]
    b_file.write(json.dumps(data))
    abm = AxieBreedManager(b_file, s_file, acc)
    assert abm.calculate_breeding_cost() == 0
    abm.breeding_file = list(range(75))
    assert abm.calculate_breeding_cost() == 0


@patch("axie.breeding.check_balance", return_value=1000)
@patch("axie.breeding.Breed.execute")
@patch("axie.breeding.Breed.__init__", return_value=None)
@patch("axie.payments.Payment.execute")
@patch("axie.payments.Payment.__init__", return_value=None)
def test_breed_manager_execute(mock_payments_init,
                               mock_payments_execute,
                               mock_breed_init,
                               mock_bree_execute,
                               mock_check_balance,
                               tmpdir):
    acc = 'ronin:<accountfoo_address>' + "".join([str(x) for x in range(10)]*4)
    private_acc = '0x<accountfoo_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+acc+'":"'+private_acc+'"}')
    b_file = tmpdir.join("b.json")
    data = [{
        "Sire": 1234,
        "Matron": 5678,
        "AccountAddress": acc
    }, {
        "Sire": 123,
        "Matron": 456,
        "AccountAddress": acc
    }]
    b_file.write(json.dumps(data))
    abm = AxieBreedManager(b_file, s_file, acc)
    abm.execute()
    mock_check_balance.assert_called_once()
    mock_breed_init.assert_has_calls(calls=[
        call(sire_axie=1234, matron_axie=5678, address=acc, private_key=private_acc),
        call(sire_axie=123, matron_axie=456, address=acc, private_key=private_acc)
    ])
    assert mock_bree_execute.call_count == 2
    mock_payments_init.assert_called_with(
        "Breeding Fee",
        "donation",
        acc,
        private_acc,
        CREATOR_FEE_ADDRESS,
        60,
        PaymentsSummary())
    assert mock_payments_execute.call_count == 1


@patch("axie.payments.Payment.execute")
@patch("axie.breeding.Breed.execute")
@patch("axie.payments.Payment.__init__", return_value=None)
@patch("axie.breeding.Breed.__init__", return_value=None)
@patch("axie.breeding.check_balance", return_value=0)
def test_breed_manager_execute_not_enough_slp(mock_check_balance, _, __, ___, ____, tmpdir, caplog):
    acc = 'ronin:<accountfoo_address>' + "".join([str(x) for x in range(10)]*4)
    private_acc = '0x<accountfoo_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+acc+'":"'+private_acc+'"}')
    b_file = tmpdir.join("b.json")
    data = [{
        "Sire": 1234,
        "Matron": 5678,
        "AccountAddress": acc
    }, {
        "Sire": 123,
        "Matron": 456,
        "AccountAddress": acc
    }]
    b_file.write(json.dumps(data))
    abm = AxieBreedManager(b_file, s_file, acc)
    with patch.object(sys, "exit") as mocked_sys:
        abm.execute()
    mocked_sys.assert_called_once()
    mock_check_balance.assert_called_once()
    assert "Not enough SLP funds to pay for breeding and the fee" in caplog.text


def test_breed_init():
    acc = 'ronin:<accountfoo_address>' + "".join([str(x) for x in range(10)]*4)
    private_acc = '0x<accountfoo_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    b = Breed(sire_axie=123, matron_axie=456, address=acc, private_key=private_acc)
    assert b.sire_axie == 123
    assert b.matron_axie == 456
    assert b.private_key == private_acc
    assert b.address == acc.replace("ronin:", "0x")


@patch("web3.Web3.toHex", return_value="transaction_hash")
@patch("web3.Web3.keccak", return_value='result_of_keccak')
@patch("web3.eth.Eth.get_transaction_receipt", return_value={'status': 1})
@patch("web3.eth.Eth.send_raw_transaction", return_value="raw_tx")
@patch("web3.eth.Eth.account.sign_transaction")
@patch("axie.breeding.get_nonce", return_value=1)
@patch("web3.eth.Eth.contract")
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("web3.Web3.HTTPProvider", return_value="provider")
def test_breed_execute(mocked_provider,
                       mocked_checksum,
                       mocked_contract,
                       mock_get_nonce,
                       mocked_sign_transaction,
                       mock_raw_send,
                       mock_receipt,
                       mock_keccak,
                       mock_to_hex):
    acc = 'ronin:<accountfoo_address>' + "".join([str(x) for x in range(10)]*4)
    private_acc = '0x<accountfoo_private_address>012345' + "".join([str(x) for x in range(10)]*3)
    with patch.object(builtins,
                      "open",
                      mock_open(read_data='{"foo": "bar"}')):
        b = Breed(sire_axie=123, matron_axie=456, address=acc, private_key=private_acc)
        b.execute()
    mock_get_nonce.assert_called_once()
    mocked_provider.assert_called_with(
        RONIN_PROVIDER_FREE,
        request_kwargs={"headers": {"content-type": "application/json", "user-agent": USER_AGENT}}
    )
    mocked_checksum.assert_called_with(AXIE_CONTRACT)
    mocked_contract.assert_called_with(address="checksum", abi={"foo": "bar"})
    mocked_sign_transaction.assert_called_once()
    mock_raw_send.assert_called_once()
    mock_keccak.assert_called_once()
    mock_to_hex.assert_called_with("result_of_keccak")
    mock_receipt.assert_called_with("transaction_hash")
