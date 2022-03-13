import builtins
import json

from mock import patch

from trezor import TrezorAccountsSetup


def test_trezor_setup_init():
    inp =  {"ronin:<account_s1_address>": "hello"}
    tas = TrezorAccountsSetup(inp)
    assert tas.trezor_config == {}
    assert tas.payments == inp
    assert tas.path == None


def test_trezor_setup_init_existing_config():
    f1 = {"ronin:<account_s1_address>": "hello"}
    config_data = {"ronin:<account_s1_address>": {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    tas = TrezorAccountsSetup(f1, config_data)
    assert tas.trezor_config == config_data
    assert tas.payments == f1

def test_trezor_setup_update_already_existing(caplog):
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    p_file = {
        "Manager": manager_acc,
        "Scholars": [
            {
                "Name": "Scholar 1",
                "AccountAddress": scholar_acc,
                "ScholarPayoutAddress": "ronin:<scholar_address>",
                "ScholarPercent": 55
            }
        ],
        "Donations": [
            {
                "Name": "Entity 1",
                "AccountAddress": dono_acc,
                "Percent": 1
            }
        ]
    }
    config_data = {scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    tas = TrezorAccountsSetup(p_file, config_data)
    tas.update_trezor_config()
    assert 'Gathered all accounts config, saving trezor_config file' in caplog.text
    assert 'Trezor_config file saved!' in caplog.text


@patch('trezor.trezor_setup.ethereum.get_address', return_value='ronin:<account_s1_address>01234567890123456789')
@patch('trezor.trezor_setup.get_default_client')
def test_trezor_setup_update(mock_client, mock_get_address, caplog):
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    p_file = {
        "Manager": manager_acc,
        "Scholars": [
            {
                "Name": "Scholar 1",
                "AccountAddress": scholar_acc,
                "ScholarPayoutAddress": "ronin:<scholar_address>",
                "ScholarPercent": 55
            }
        ],
        "Donations": [
            {
                "Name": "Entity 1",
                "AccountAddress": dono_acc,
                "Percent": 1
            }
        ]
    }
    tas = TrezorAccountsSetup(p_file)
    with patch.object(builtins, 'input', lambda _: 1):
        tas.update_trezor_config()
        mock_client.assert_called()
        mock_get_address.assert_called()
    assert 'Gathered all accounts config, saving trezor_config file' in caplog.text
    assert 'Trezor_config file saved!' in caplog.text
