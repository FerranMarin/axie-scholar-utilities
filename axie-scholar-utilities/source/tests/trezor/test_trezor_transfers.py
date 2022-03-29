from mock import patch, call

from trezor import TrezorAxieTransferManager


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


@patch("trezor.trezor_transfers.get_default_client", return_value="client")
@patch("axie_utils.Axies.get_axies", return_value=[123, 123123, 234])
@patch("trezor.trezor_transfers.load_json")
@patch("trezor.trezor_transfers.TrezorAxieTransferManager.execute_transfers")
def test_transfer_manager_prepare_transfers(mocked_execute_transfers,
                                            mocked_load_json,
                                            mock_axies,
                                            mock_client):
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
    assert mocked_execute_transfers.call_count == 1
    transactions_list = mocked_execute_transfers.call_args_list[0][0][0]
    assert len(transactions_list) == 3
    # Check transaction 1
    assert transactions_list[0].from_acc == "0x1"
    assert transactions_list[0].client == "client"
    assert transactions_list[0].to_acc == "0x2"
    assert transactions_list[0].axie_id == 123
    # Check transaction 2
    assert transactions_list[1].from_acc == "0x1"
    assert transactions_list[1].client == "client"
    assert transactions_list[1].to_acc == "0x2"
    assert transactions_list[1].axie_id == 123123
    # Check transaction 3
    assert transactions_list[2].from_acc == "0x1"
    assert transactions_list[2].client == "client"
    assert transactions_list[2].to_acc == "0x3"
    assert transactions_list[2].axie_id == 234


@patch("trezor.trezor_transfers.get_default_client", return_value="client")
@patch("axie_utils.Axies.get_axies", return_value=[123])
@patch("trezor.trezor_transfers.load_json")
@patch("trezor.trezor_transfers.TrezorAxieTransferManager.execute_transfers")
def test_transfer_manager_prepare_transfers_only_available(mocked_execute_transfers,
                                                           mocked_load_json,
                                                           mock_axies,
                                                           mock_client):
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
    assert mocked_execute_transfers.call_count == 1
    transactions_list = mocked_execute_transfers.call_args_list[0][0][0]
    assert len(transactions_list) == 1
    # Check transaction 1
    assert transactions_list[0].from_acc == "0x1"
    assert transactions_list[0].client == "client"
    assert transactions_list[0].to_acc == "0x2"
    assert transactions_list[0].axie_id == 123


@patch("trezor.trezor_transfers.get_default_client", return_value="client")
@patch("axie_utils.Axies.get_axies", return_value=[123, 123123, 234])
@patch("trezor.trezor_transfers.load_json")
@patch("trezor.trezor_transfers.TrezorAxieTransferManager.execute_transfers")
def test_transfer_manager_prepare_transfers_secure(mocked_execute_transfers,
                                                   mocked_load_json,
                                                   mock_axies,
                                                   mock_client):
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
    assert mocked_execute_transfers.call_count == 1
    transactions_list = mocked_execute_transfers.call_args_list[0][0][0]
    assert len(transactions_list) == 1
    assert transactions_list[0].from_acc == "0x1"
    assert transactions_list[0].client == "client"
    assert transactions_list[0].to_acc == "0x3"
    assert transactions_list[0].axie_id == 234
