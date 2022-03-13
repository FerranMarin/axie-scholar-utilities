import builtins
from glob import glob

from mock import patch, call, mock_open

from trezor import TrezorAxieTransferManager
from trezor.trezor_transfers import TrezorTransfer, AXIE_CONTRACT
from tests.test_utils import LOG_FILE_PATH, cleanup_log_file


@patch("trezor.trezor_transfers.load_json")
def test_transfer_manager_init(mocked_load_json):
    transfers_file = "sample_transfers_file.json"
    config_file = "sample_config_file.json"
    atm = TrezorAxieTransferManager(transfers_file, config_file)
    mocked_load_json.assert_has_calls(
        calls=[call(transfers_file), call(config_file)]
    )
    assert atm.secure is None
    atm = TrezorAxieTransferManager(transfers_file, config_file, True)
    assert atm.secure is True


@patch("trezor.trezor_transfers.parse_path", return_value="m/44'/60'/0'/0/0")
@patch("trezor.trezor_transfers.get_default_client", return_value="client")
@patch("trezor.trezor_transfers.Axies.get_axies", return_value=[123, 123123, 234])
@patch("trezor.trezor_transfers.load_json")
@patch("trezor.trezor_transfers.TrezorAxieTransferManager.execute_transfers")
def test_transfer_manager_prepare_transfers(mocked_execute_transfers,
                                            mocked_load_json,
                                            mock_axies,
                                            mock_client,
                                            mock_parse):
    transfers_file = "sample_transfers_file.json"
    config_file = "sample_config_file.json"
    atm = TrezorAxieTransferManager(transfers_file, config_file)
    mocked_load_json.assert_has_calls(
        calls=[call(transfers_file), call(config_file)]
    )
    atm.transfers_file = [{"AccountAddress": "ronin:1", "Transfers": [
        {"AxieId": 123, "ReceiverAddress": "ronin:2"},
        {"AxieId": 123123, "ReceiverAddress": "ronin:2"},
        {"AxieId": 234, "ReceiverAddress": "ronin:3"}
    ]}]
    atm.trezor_config = {"ronin:1": {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    atm.prepare_transfers()
    mock_axies.assert_called_once()
    mock_client.assert_called()
    mock_parse.assert_has_calls(calls=[
        call("m/44'/60'/0'/0/0"),
        call("m/44'/60'/0'/0/0"),
        call("m/44'/60'/0'/0/0")
    ])
    assert mocked_execute_transfers.call_count == 1
    transactions_list = mocked_execute_transfers.call_args_list[0][0][0]
    assert len(transactions_list) == 3
    # Check transaction 1
    assert transactions_list[0].from_acc == "0x1"
    assert transactions_list[0].bip_path == "m/44'/60'/0'/0/0"
    assert transactions_list[0].client == "client"
    assert transactions_list[0].to_acc == "0x2"
    assert transactions_list[0].axie_id == 123
    # Check transaction 2
    assert transactions_list[1].from_acc == "0x1"
    assert transactions_list[1].bip_path == "m/44'/60'/0'/0/0"
    assert transactions_list[1].client == "client"
    assert transactions_list[1].to_acc == "0x2"
    assert transactions_list[1].axie_id == 123123
    # Check transaction 3
    assert transactions_list[2].from_acc == "0x1"
    assert transactions_list[2].bip_path == "m/44'/60'/0'/0/0"
    assert transactions_list[2].client == "client"
    assert transactions_list[2].to_acc == "0x3"
    assert transactions_list[2].axie_id == 234


@patch("trezor.trezor_transfers.parse_path", return_value="m/44'/60'/0'/0/0")
@patch("trezor.trezor_transfers.get_default_client", return_value="client")
@patch("trezor.trezor_transfers.Axies.get_axies", return_value=[123])
@patch("trezor.trezor_transfers.load_json")
@patch("trezor.trezor_transfers.TrezorAxieTransferManager.execute_transfers")
def test_transfer_manager_prepare_transfers_only_available(mocked_execute_transfers,
                                                           mocked_load_json,
                                                           mock_axies,
                                                           mock_client,
                                                           mock_parse):
    transfers_file = "sample_transfers_file.json"
    config_file = "sample_config_file.json"
    atm = TrezorAxieTransferManager(transfers_file, config_file)
    mocked_load_json.assert_has_calls(
        calls=[call(transfers_file), call(config_file)]
    )
    atm.transfers_file = [{"AccountAddress": "ronin:1", "Transfers": [
        {"AxieId": 123, "ReceiverAddress": "ronin:2"},
        {"AxieId": 123123, "ReceiverAddress": "ronin:2"},
        {"AxieId": 234, "ReceiverAddress": "ronin:3"}
    ]}]
    atm.trezor_config = {"ronin:1": {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    atm.prepare_transfers()
    mock_axies.assert_called_once()
    mock_client.assert_called()
    mock_parse.assert_called_with("m/44'/60'/0'/0/0")
    assert mocked_execute_transfers.call_count == 1
    transactions_list = mocked_execute_transfers.call_args_list[0][0][0]
    assert len(transactions_list) == 1
    # Check transaction 1
    assert transactions_list[0].from_acc == "0x1"
    assert transactions_list[0].bip_path == "m/44'/60'/0'/0/0"
    assert transactions_list[0].client == "client"
    assert transactions_list[0].to_acc == "0x2"
    assert transactions_list[0].axie_id == 123


@patch("trezor.trezor_transfers.parse_path", return_value="m/44'/60'/0'/0/0")
@patch("trezor.trezor_transfers.get_default_client", return_value="client")
@patch("trezor.trezor_transfers.Axies.get_axies", return_value=[123, 123123, 234])
@patch("trezor.trezor_transfers.load_json")
@patch("trezor.trezor_transfers.TrezorAxieTransferManager.execute_transfers")
def test_transfer_manager_prepare_transfers_secure(mocked_execute_transfers,
                                                   mocked_load_json,
                                                   mock_axies,
                                                   mock_client,
                                                   mock_parse):
    transfers_file = "sample_transfers_file.json"
    config_file = "sample_config_file.json"
    atm = TrezorAxieTransferManager(transfers_file, config_file, True)
    mocked_load_json.assert_has_calls(
        calls=[call(transfers_file), call(config_file)]
    )
    atm.transfers_file = [{"AccountAddress": "ronin:1", "Transfers": [
        {"AxieId": 123, "ReceiverAddress": "ronin:2"},
        {"AxieId": 123123, "ReceiverAddress": "ronin:2"},
        {"AxieId": 234, "ReceiverAddress": "ronin:3"}
    ]}]
    atm.trezor_config = {
         "ronin:1": {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"},
         "ronin:3": {"passphrase": "", "bip_path": "m/44'/60'/0'/0/1"},
    }
    atm.prepare_transfers()
    mock_axies.assert_called_once()
    mock_client.assert_called()
    mock_parse.assert_called_with("m/44'/60'/0'/0/0")
    assert mocked_execute_transfers.call_count == 1
    transactions_list = mocked_execute_transfers.call_args_list[0][0][0]
    assert len(transactions_list) == 1
    assert transactions_list[0].from_acc == "0x1"
    assert transactions_list[0].bip_path == "m/44'/60'/0'/0/0"
    assert transactions_list[0].client == "client"
    assert transactions_list[0].to_acc == "0x3"
    assert transactions_list[0].axie_id == 234


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
                                      mocked_get_transaction_count,
                                      mocked_to_bytes,
                                      mocked_rlp,
                                      caplog):
    # Make sure file is clean to start
    log_file = glob(LOG_FILE_PATH+'logs/results_*.log')[0][9:]
    cleanup_log_file(log_file)
    t = TrezorTransfer(
        to_acc="ronin:to_ronin",
        client="client",
        bip_path="m/44'/60'/0'/0/0",
        from_acc="ronin:from_ronin",
        axie_id=123
    )
    with patch.object(builtins,
                      "open",
                      mock_open(read_data='{"foo": "bar"}')) as mock_file:
        t.execute()
    mock_file.assert_called_with("trezor/axie_abi.json", encoding='utf-8')
    mock_contract.assert_called_with(address='checksum', abi={'foo': 'bar'})
    mock_keccak.assert_called_once()
    mock_to_hex.assert_called_with("result_of_keccak")
    mock_send.assert_called_once()
    mock_sign.assert_called_once()
    mocked_to_bytes.assert_called()
    mocked_rlp.assert_called()
    mock_checksum.assert_has_calls(calls=[
        call(AXIE_CONTRACT),
        call('0xfrom_ronin'),
        call('0xfrom_ronin'),
        call('0xto_ronin')])
    mock_transaction_receipt.assert_called_with("transaction_hash")
    mocked_get_transaction_count.assert_called()
    assert ("Axie Transfer of axie (123) from account (ronin:from_ronin) to account "
            "(ronin:to_ronin) completed! Hash: transaction_hash - "
            "Explorer: https://explorer.roninchain.com/tx/transaction_hash" in caplog.text)
    print(log_file)
    with open(log_file) as f:
        lf = f.readlines()
        assert len(lf) == 1
    cleanup_log_file(log_file)
