import builtins
import json

from mock import patch

from trezor import TrezorAccountsSetup

def test_trezor_setup_init(tmpdir):
    f1 = tmpdir.join("file1.json")
    f1.write('{"ronin:<account_s1_address>": "hello"}')
    tas = TrezorAccountsSetup(f1.strpath)
    assert tas.trezor_config_file == None
    assert tas.trezor_config == {}
    assert tas.payments == {"ronin:<account_s1_address>": "hello"}


def test_trezor_setup_init_existing_config(tmpdir):
    f1 = tmpdir.join("file1.json")
    f1.write('{"ronin:<account_s1_address>": "hello"}')
    f2 = tmpdir.join('file2.json')
    config_data = {"ronin:<account_s1_address>": {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    f2.write(json.dumps(config_data))
    tas = TrezorAccountsSetup(f1.strpath, f2.strpath)
    assert tas.trezor_config_file == f2.strpath
    assert tas.trezor_config == config_data
    assert tas.payments == {"ronin:<account_s1_address>": "hello"}


def test_trezor_setup_update_already_existing(tmpdir, caplog):
    p_file = tmpdir.join("p.json")
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    p_file.write(('{"Manager":"'+manager_acc+'","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPayout":10,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPayout":1,'
                  '"ManagerPayout":9}],"Donations":[{"Name":"Entity 1",'
                  '"AccountAddress": "'+dono_acc+'","Percent":0.01}]}'))
    f2 = tmpdir.join('file2.json')
    config_data = {scholar_acc: {"passphrase": "", "bip_path": "m/44'/60'/0'/0/0"}}
    f2.write(json.dumps(config_data))
    tas = TrezorAccountsSetup(p_file.strpath, f2.strpath)
    tas.update_trezor_config()
    assert 'Gathered all accounts config, saving trezor_config file' in caplog.text
    assert 'Trezor_config file saved!' in caplog.text

@patch('trezor.trezor_setup.ethereum.get_address', return_value='ronin:<account_s1_address>01234567890123456789')
@patch('trezor.trezor_setup.get_default_client')
def test_trezor_setup_update(mock_client, mock_get_address, tmpdir, caplog):
    p_file = tmpdir.join("p.json")
    manager_acc = 'ronin:<manager_address>000' + "".join([str(x) for x in range(10)]*2)
    dono_acc = 'ronin:<donations_address>0' + "".join([str(x) for x in range(10)]*2)
    scholar_acc = 'ronin:<account_s1_address>' + "".join([str(x) for x in range(10)]*2)
    p_file.write(('{"Manager":"'+manager_acc+'","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPayout":10,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPayout":1,'
                  '"ManagerPayout":9}],"Donations":[{"Name":"Entity 1",'
                  '"AccountAddress": "'+dono_acc+'","Percent":0.01}]}'))
    tas = TrezorAccountsSetup(p_file.strpath)
    with patch.object(builtins, 'input', lambda _: 1):
        tas.update_trezor_config()
        mock_client.assert_called()
        mock_get_address.assert_called()
    assert 'Gathered all accounts config, saving trezor_config file' in caplog.text
    assert 'Trezor_config file saved!' in caplog.text
