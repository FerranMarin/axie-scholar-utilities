import os
import sys
import builtins
import json

from docopt import docopt, DocoptExit
from mock import patch, call
import pytest

import trezor_axie_scholar_cli as cli


@pytest.mark.parametrize("params, expected_result",
                         [
                            (["payout", "file1", "file2"],
                             {"--help": False,
                              "--force": False,
                              "--version": False,
                              "--yes": False,
                              "--safe-mode": False,
                              '<list_of_accounts>': None,
                              'axie_morphing': False,
                              "<payments_file>": "file1",
                              "<config_file>": "file2",
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              '<csv_file>': None,
                              '<breedings_file>': None,
                              'generate_breedings': False,
                              'axie_breeding': False,
                              "claim": False,
                              "generate_QR": False,
                              'generate_transfer_axies': False,
                              "config_trezor": False,
                              'generate_payments': False,
                              "payout": True}),
                            (["payout", "file1", "file2", "-y"],
                             {"--help": False,
                              "--force": False,
                              "--version": False,
                              "--yes": True,
                              "--safe-mode": False,
                              '<list_of_accounts>': None,
                              'axie_morphing': False,
                              "<payments_file>": "file1",
                              "<config_file>": "file2",
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              '<csv_file>': None,
                              '<breedings_file>': None,
                              'generate_breedings': False,
                              'axie_breeding': False,
                              "claim": False,
                              "generate_QR": False,
                              'generate_transfer_axies': False,
                              "config_trezor": False,
                              'generate_payments': False,
                              "payout": True}),
                            (["payout", "file1", "file2", "--yes"],
                             {"--help": False,
                              "--force": False,
                              "--version": False,
                              "--yes": True,
                              "--safe-mode": False,
                              '<list_of_accounts>': None,
                              'axie_morphing': False,
                              "<payments_file>": "file1",
                              "<config_file>": "file2",
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              '<csv_file>': None,
                              '<breedings_file>': None,
                              'axie_breeding': False,
                              'generate_breedings': False,
                              "claim": False,
                              "generate_QR": False,
                              'generate_transfer_axies': False,
                              "config_trezor": False,
                              'generate_payments': False,
                              "payout": True}),
                            (["claim", "file1", "file2"],
                             {"--help": False,
                              "--force": False,
                              "--version": False,
                              "--yes": False,
                              "--safe-mode": False,
                              '<list_of_accounts>': None,
                              'axie_morphing': False,
                              "<payments_file>": "file1",
                              "<config_file>": "file2",
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              '<csv_file>': None,
                              '<breedings_file>': None,
                              'axie_breeding': False,
                              'generate_breedings': False,
                              "claim": True,
                              "generate_QR": False,
                              'generate_transfer_axies': False,
                              "config_trezor": False,
                              'generate_payments': False,
                              "payout": False}),
                            (["claim", "file1", "file2", "--force"],
                             {"--help": False,
                              "--force": True,
                              "--version": False,
                              "--yes": False,
                              "--safe-mode": False,
                              '<list_of_accounts>': None,
                              'axie_morphing': False,
                              "<payments_file>": "file1",
                              "<config_file>": "file2",
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              '<csv_file>': None,
                              '<breedings_file>': None,
                              'axie_breeding': False,
                              'generate_breedings': False,
                              "claim": True,
                              "generate_QR": False,
                              'generate_transfer_axies': False,
                              "config_trezor": False,
                              'generate_payments': False,
                              "payout": False}),
                            (["config_trezor", "file1"],
                             {"--help": False,
                              "--force": False,
                              "--version": False,
                              "--yes": False,
                              "--safe-mode": False,
                              '<list_of_accounts>': None,
                              'axie_morphing': False,
                              "<payments_file>": "file1",
                              "<config_file>": None,
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              '<csv_file>': None,
                              '<breedings_file>': None,
                              'axie_breeding': False,
                              'generate_breedings': False,
                              "claim": False,
                              "generate_QR": False,
                              'generate_transfer_axies': False,
                              "config_trezor": True,
                              'generate_payments': False,
                              "payout": False}),
                            (["config_trezor", "file1", "file2"],
                             {"--help": False,
                              "--force": False,
                              "--version": False,
                              "--yes": False,
                              "--safe-mode": False,
                              '<list_of_accounts>': None,
                              'axie_morphing': False,
                              "<payments_file>": "file1",
                              "<config_file>": "file2",
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              '<csv_file>': None,
                              '<breedings_file>': None,
                              'axie_breeding': False,
                              'generate_breedings': False,
                              "claim": False,
                              "generate_QR": False,
                              'generate_transfer_axies': False,
                              "config_trezor": True,
                              'generate_payments': False,
                              "payout": False}),
                            (["transfer_axies", "file1", "file2"],
                             {"--help": False,
                              "--force": False,
                              "--version": False,
                              "--yes": False,
                              "--safe-mode": False,
                              '<list_of_accounts>': None,
                              'axie_morphing': False,
                              "<payments_file>": None,
                              "<config_file>": "file2",
                              '<transfers_file>': "file1",
                              'transfer_axies': True,
                              '<csv_file>': None,
                              '<breedings_file>': None,
                              'axie_breeding': False,
                              'generate_breedings': False,
                              'generate_transfer_axies': False,
                              "claim": False,
                              "generate_QR": False,
                              "config_trezor": False,
                              'generate_payments': False,
                              "payout": False}),
                            (["transfer_axies", "file1", "file2", "--safe-mode"],
                             {"--help": False,
                              "--force": False,
                              "--version": False,
                              "--yes": False,
                              "--safe-mode": True,
                              '<list_of_accounts>': None,
                              'axie_morphing': False,
                              "<payments_file>": None,
                              "<config_file>": "file2",
                              '<transfers_file>': "file1",
                              'transfer_axies': True,
                              '<csv_file>': None,
                              '<breedings_file>': None,
                              'axie_breeding': False,
                              'generate_breedings': False,
                              "claim": False,
                              "generate_QR": False,
                              'generate_transfer_axies': False,
                              "config_trezor": False,
                              'generate_payments': False,
                              "payout": False}),
                            (["generate_payments", "file1", "file2"],
                             {"--help": False,
                              "--force": False,
                              "--version": False,
                              "--yes": False,
                              "--safe-mode": False,
                              '<list_of_accounts>': None,
                              'axie_morphing': False,
                              "<payments_file>": "file2",
                              "<config_file>": None,
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              '<csv_file>': "file1",
                              '<breedings_file>': None,
                              'axie_breeding': False,
                              'generate_breedings': False,
                              "claim": False,
                              "generate_QR": False,
                              'generate_transfer_axies': False,
                              "config_trezor": False,
                              'generate_payments': True,
                              "payout": False}),
                            (["generate_payments", "file1"],
                             {"--help": False,
                              "--force": False,
                              "--version": False,
                              "--yes": False,
                              "--safe-mode": False,
                              '<list_of_accounts>': None,
                              'axie_morphing': False,
                              "<payments_file>": None,
                              "<config_file>": None,
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              '<csv_file>': "file1",
                              '<breedings_file>': None,
                              'axie_breeding': False,
                              'generate_breedings': False,
                              "claim": False,
                              "generate_QR": False,
                              'generate_transfer_axies': False,
                              "config_trezor": False,
                              'generate_payments': True,
                              "payout": False}),
                            (["axie_morphing", "file1", "a,b,c"],
                             {"--help": False,
                              "--force": False,
                              "--version": False,
                              "--yes": False,
                              "--safe-mode": False,
                              '<list_of_accounts>': "a,b,c",
                              'axie_morphing': True,
                              "<payments_file>": None,
                              "<config_file>": "file1",
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              '<csv_file>': None,
                              '<breedings_file>': None,
                              'axie_breeding': False,
                              'generate_breedings': False,
                              "claim": False,
                              "generate_QR": False,
                              'generate_transfer_axies': False,
                              "config_trezor": False,
                              'generate_payments': False,
                              "payout": False}),
                            (["axie_breeding", "file1", "file2"],
                             {"--help": False,
                              "--force": False,
                              "--version": False,
                              "--yes": False,
                              "--safe-mode": False,
                              '<list_of_accounts>': None,
                              'axie_morphing': False,
                              "<payments_file>": None,
                              "<config_file>": "file2",
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              '<csv_file>': None,
                              '<breedings_file>': "file1",
                              'axie_breeding': True,
                              'generate_breedings': False,
                              "claim": False,
                              "generate_QR": False,
                              'generate_transfer_axies': False,
                              "config_trezor": False,
                              'generate_payments': False,
                              "payout": False}),
                            (["generate_QR", "file1", "file2"],
                             {"--help": False,
                              "--force": False,
                              "--version": False,
                              "--yes": False,
                              "--safe-mode": False,
                              '<list_of_accounts>': None,
                              'axie_morphing': False,
                              "<payments_file>": "file1",
                              "<config_file>": "file2",
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              '<csv_file>': None,
                              '<breedings_file>': None,
                              'axie_breeding': False,
                              'generate_breedings': False,
                              "claim": False,
                              "generate_QR": True,
                              'generate_transfer_axies': False,
                              "config_trezor": False,
                              'generate_payments': False,
                              "payout": False}),
                            (["generate_breedings", "file1", "file2"],
                             {"--help": False,
                              "--force": False,
                              "--version": False,
                              "--yes": False,
                              "--safe-mode": False,
                              '<list_of_accounts>': None,
                              'axie_morphing': False,
                              "<payments_file>": None,
                              "<config_file>": None,
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              '<csv_file>': "file1",
                              '<breedings_file>': "file2",
                              'axie_breeding': False,
                              'generate_breedings': True,
                              "claim": False,
                              "generate_QR": False,
                              'generate_transfer_axies': False,
                              "config_trezor": False,
                              'generate_payments': False,
                              "payout": False}),
                            (["generate_breedings", "file1"],
                             {"--help": False,
                              "--force": False,
                              "--version": False,
                              "--yes": False,
                              "--safe-mode": False,
                              '<list_of_accounts>': None,
                              'axie_morphing': False,
                              "<payments_file>": None,
                              "<config_file>": None,
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              '<csv_file>': "file1",
                              '<breedings_file>': None,
                              'axie_breeding': False,
                              'generate_breedings': True,
                              "claim": False,
                              "generate_QR": False,
                              'generate_transfer_axies': False,
                              "config_trezor": False,
                              'generate_payments': False,
                              "payout": False}),
                            (["generate_transfer_axies", "file1", "file2"],
                             {"--help": False,
                              "--force": False,
                              "--version": False,
                              "--yes": False,
                              "--safe-mode": False,
                              '<list_of_accounts>': None,
                              'axie_morphing': False,
                              "<payments_file>": None,
                              "<config_file>": None,
                              '<transfers_file>': "file2",
                              'transfer_axies': False,
                              '<csv_file>': "file1",
                              '<breedings_file>': None,
                              'axie_breeding': False,
                              'generate_breedings': False,
                              "claim": False,
                              "generate_QR": False,
                              'generate_transfer_axies': True,
                              "config_trezor": False,
                              'generate_payments': False,
                              "payout": False}),
                            (["generate_transfer_axies", "file1"],
                             {"--help": False,
                              "--force": False,
                              "--version": False,
                              "--yes": False,
                              "--safe-mode": False,
                              '<list_of_accounts>': None,
                              'axie_morphing': False,
                              "<payments_file>": None,
                              "<config_file>": None,
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              '<csv_file>': "file1",
                              '<breedings_file>': None,
                              'axie_breeding': False,
                              'generate_breedings': False,
                              "claim": False,
                              "generate_QR": False,
                              'generate_transfer_axies': True,
                              "config_trezor": False,
                              'generate_payments': False,
                              "payout": False})
                         ])
def test_parses_params(params, expected_result):
    args = docopt(cli.__doc__, params)
    assert args == expected_result


@pytest.mark.parametrize("params",
                         [
                            (["a", "b", "c"]),
                            (["generate_QR"]),
                            (["generate_QR", "file1"]),
                            (["config_trezor"]),
                            (["config_trezor", "file1", "file2", "file3"]),
                            (["payout", "file1"]),
                            (["transfer_axies"]),
                            (["transfer_axies", "file1"]),
                            (["transfer_axies", "file1", "file2", "file3"]),
                            (["claim"]),
                            (["claim", "file1"]),
                            (["payout"]),
                            (["payout", "file1"]),
                            (["payout", "file1", "file2", "file3"]),
                            (["generate_payments", "file1", "file2", "file3"]),
                            (["generate_payments"]),
                            (["axie_morphing"]),
                            (["generate_breedings"]),
                            (["generate_breedings", "file1", "file2", "file3"]),
                            (["generate_transfer_axies"]),
                            (["generate_transfer_axies", "file1", "file2", "file3"]),
                            (["axie_morphing", "file1"]),
                            (["axie_morphing", "file1", "foo", "bar"]),
                            (["axie_breeding"]),
                            (["axie_breeding", "file1"]),
                            (["axie_breeding", "file1", "foo", "bar"]),
                         ])
def test_wrong_inputs(params):
    with pytest.raises(DocoptExit):
        docopt(cli.__doc__, params)


def test_payout_file_check_fail(caplog):
    with patch.object(sys, 'argv', ["", "payout", "p_file.json", "c_file.json"]):
        cli.run_cli()
    assert "Please provide a correct path to the file. Path provided: p_file.json" in caplog.text
    assert "Please review your file paths and re-try." in caplog.text


def test_generate_breedings_file_check_fail(caplog):
    with patch.object(sys, 'argv', ["", "generate_breedings", "b_file.csv", "b_file.json"]):
        cli.run_cli()
    assert "Please provide a correct path to the file. Path provided: b_file.json" in caplog.text
    assert "Please review your file paths and re-try." in caplog.text


def test_generate_transfers_file_check_fail(caplog):
    with patch.object(sys, 'argv', ["", "generate_transfer_axies", "t_file.csv", "t_file.json"]):
        cli.run_cli()
    assert "Please provide a correct path to the file. Path provided: t_file.json" in caplog.text
    assert "Please review your file paths and re-try." in caplog.text


def test_config_trezor_file_check_fail(caplog):
    with patch.object(sys, 'argv', ["", "config_trezor", "p_file.json", "c_file.json"]):
        cli.run_cli()
    assert "Please provide a correct path to the file. Path provided: c_file.json" in caplog.text
    assert "Please review your file paths and re-try." in caplog.text


def test_config_trezor_file_check_fail_only_payment_file(caplog):
    with patch.object(sys, 'argv', ["", "config_trezor", "p_file.json"]):
        cli.run_cli()
    assert "Please provide a correct path to the file. Path provided: p_file.json" in caplog.text
    assert "Please review your file paths and re-try." in caplog.text


@patch('trezor.TrezorAccountsSetup.update_trezor_config')
@patch('trezor.TrezorAccountsSetup.__init__', return_value=None)
def test_config_trezor_no_config_file(mock_account_setup, mock_update_config, tmpdir):
    f1 = tmpdir.join("file1.json")
    f1.write('{"Scholars":[{"Name": "Acc1", "AccountAddress": "ronin:<account_s1_address>"},'
             '{"Name": "Acc2", "AccountAddress": "ronin:<account_s2_address>"}]}')
    with patch.object(sys, 'argv', ["", "config_trezor", f1.strpath]):
        cli.run_cli()
    mock_account_setup.assert_called_with(f1.strpath, None)
    mock_update_config.assert_called()


@patch('trezor.TrezorAccountsSetup.update_trezor_config')
@patch('trezor.TrezorAccountsSetup.__init__', return_value=None)
def test_config_trezor_config_file(mock_account_setup, mock_update_config, tmpdir):
    f1 = tmpdir.mkdir("other_folder").join("file1.json")
    f1.write('{"Scholars":[{"Name": "Acc1", "AccountAddress": "ronin:<account_s1_address>"},'
             '{"Name": "Acc2", "AccountAddress": "ronin:<account_s2_address>"}]}')
    f2 = tmpdir.join("trezor_config.json")
    f2.write('{}')
    with patch.object(sys, 'argv', ["", "config_trezor", f1.strpath, f2.strpath]):
        cli.run_cli()
    mock_account_setup.assert_called_with(f1.strpath, f2.strpath)
    mock_update_config.assert_called()


def test_generate_payments_file(tmpdir):
    f1 = tmpdir.mkdir("other_folder").join("file1.csv")
    f1.write('Name,AccountAddress,ScholarPayoutAddress,ScholarPercent,ScholarPayout\n'
             'Test1,ronin:abc1,ronin:abc_scholar1,50,\n'
             'Test2,ronin:abc2,ronin:abc_scholar2,50,\n'
             'Test3,ronin:abc3,ronin:abc_scholar3,50,\n'
             'Test4,ronin:abc4,ronin:abc_scholar4,50,\n'
             'Test5,ronin:abc5,ronin:abc_scholar5,50,100\n')
    f2 = tmpdir.join("other_folder/payments.json")
    f2.write('{}')
    with patch.object(builtins, 'input', lambda _: 'ronin:9fa1bc784c665e683597d3f29375e45786617550'):
        cli.generate_payments_file(f1.strpath, f2.strpath)
    assert json.loads(f2.read()) == {
        'Manager': 'ronin:9fa1bc784c665e683597d3f29375e45786617550',
        'Scholars': [{
                'Name': 'Test1',
                'AccountAddress': 'ronin:abc1',
                'ScholarPayoutAddress': 'ronin:abc_scholar1',
                'ScholarPercent': 50
            },
            {
                'Name': 'Test2',
                'AccountAddress': 'ronin:abc2',
                'ScholarPayoutAddress': 'ronin:abc_scholar2',
                'ScholarPercent': 50
            },
            {
                'Name': 'Test3',
                'AccountAddress': 'ronin:abc3',
                'ScholarPayoutAddress': 'ronin:abc_scholar3',
                'ScholarPercent': 50
            },
            {
                'Name': 'Test4',
                'AccountAddress': 'ronin:abc4',
                'ScholarPayoutAddress': 'ronin:abc_scholar4',
                'ScholarPercent': 50
            },
            {
                'Name': 'Test5',
                'AccountAddress': 'ronin:abc5',
                'ScholarPayoutAddress': 'ronin:abc_scholar5',
                'ScholarPercent': 50,
                'ScholarPayout': 100
            }
        ]
    }


def test_generate_breedings_file(tmpdir):
    f1 = tmpdir.mkdir("other_folder").join("file1.csv")
    f1.write('Sire,Matron,AccountAddress\n'
             '123,234,ronin:abc1\n'
             '1232,2342,ronin:abc2\n'
             '1233,2343,ronin:abc3\n')
    f2 = tmpdir.join("other_folder/breedings.json")
    f2.write('{}')
    cli.generate_breedings_file(f1.strpath, f2.strpath)
    assert json.loads(f2.read()) == [
        {
            'Sire': 123,
            'Matron': 234,
            'AccountAddress': 'ronin:abc1',
        },
        {
            'Sire': 1232,
            'Matron': 2342,
            'AccountAddress': 'ronin:abc2',
        },
        {
            'Sire': 1233,
            'Matron': 2343,
            'AccountAddress': 'ronin:abc3',
        }
    ]


def test_generate_transfer_file(tmpdir):
    f1 = tmpdir.mkdir("other_folder").join("file1.csv")
    f1.write('AccountAddress,AxieId,ReceiverAddress\n'
             'ronin:<whohasanaxie1>,1231,ronin:<whowillgetanaxie>\n'
             'ronin:<whohasanaxie1>,1232,ronin:<whowillgetanaxie>\n'
             'ronin:<whohasanaxie1>,1233,ronin:<whowillgetanaxie>\n'
             'ronin:<whohasanaxie2>,1234,ronin:<whowillgetanaxie>\n'
             'ronin:<whohasanaxie2>,1235,ronin:<whowillgetanaxie>\n'
             'ronin:<whohasanaxie2>,1236,ronin:<whowillgetanaxie>\n')
    f2 = tmpdir.join("other_folder/breedings.json")
    f2.write('{}')
    cli.generate_transfers_file(f1.strpath, f2.strpath)
    assert json.loads(f2.read()) == [
        {
            "AccountAddress": "ronin:<whohasanaxie1>",
            "Transfers": [
                {
                    "AxieId": 1231,
                    "ReceiverAddress": "ronin:<whowillgetanaxie>"
                },
                {
                    "AxieId": 1232,
                    "ReceiverAddress": "ronin:<whowillgetanaxie>"
                },
                {
                    "AxieId": 1233,
                    "ReceiverAddress": "ronin:<whowillgetanaxie>"
                }
            ]
        },
        {
            "AccountAddress": "ronin:<whohasanaxie2>",
            "Transfers": [
                {
                    "AxieId": 1234,
                    "ReceiverAddress": "ronin:<whowillgetanaxie>"
                },
                {
                    "AxieId": 1235,
                    "ReceiverAddress": "ronin:<whowillgetanaxie>"
                },
                {
                    "AxieId": 1236,
                    "ReceiverAddress": "ronin:<whowillgetanaxie>"
                }
            ]
        }
    ]


@patch("trezor.TrezorAxiePaymentsManager.__init__", return_value=None)
@patch("trezor.TrezorAxiePaymentsManager.verify_inputs")
@patch("trezor.TrezorAxiePaymentsManager.prepare_payout")
def test_payout_takes_auto_parameter(mock_prepare_payout, mock_verify_input, mocked_paymentsmanager, tmpdir):
    f1 = tmpdir.join("file1.json")
    f1.write('{"Scholars":[{"Name": "Acc1", "AccountAddress": "ronin:<account_s1_address>"}]}')
    f2 = tmpdir.join("file2.json")
    config_data = {"ronin:<account_s1_address>": {"passphrase": "", "bip_path": "m/44'/60'/0'/0/48"}}
    f2.write(json.dumps(config_data))
    with patch.object(sys, 'argv', ["", "payout", str(f1), str(f2)]):
        cli.run_cli()
    mock_prepare_payout.assert_called_with()
    mock_verify_input.assert_called_with()
    mocked_paymentsmanager.assert_called_with(str(f1), str(f2), auto=False)


@patch("trezor.TrezorAxiePaymentsManager.__init__", return_value=None)
@patch("trezor.TrezorAxiePaymentsManager.verify_inputs")
@patch("trezor.TrezorAxiePaymentsManager.prepare_payout")
def test_payout_takes_auto_parameter_yes(mock_prepare_payout, mock_verify_inputs, mocked_paymentsmanager, tmpdir):
    f1 = tmpdir.join("file1.json")
    f1.write('{"Scholars":[{"Name": "Acc1", "AccountAddress": "ronin:<account_s1_address>"}]}')
    f2 = tmpdir.join("file2.json")
    config_data = {"ronin:<account_s1_address>": {"passphrase": "", "bip_path": "m/44'/60'/0'/0/48"}}
    f2.write(json.dumps(config_data))
    with patch.object(sys, 'argv', ["", "payout", str(f1), str(f2), "-y"]):
        cli.run_cli()
    mock_prepare_payout.assert_called_with()
    mock_verify_inputs.assert_called_with()
    mocked_paymentsmanager.assert_called_with(str(f1), str(f2), auto=True)


@patch("trezor.TrezorAxieClaimsManager.__init__", return_value=None)
@patch("trezor.TrezorAxieClaimsManager.prepare_claims")
@patch("trezor.TrezorAxieClaimsManager.verify_inputs")
def test_claim(mock_verify_inputs, mock_prepare_claims, mock_claimsmanager, tmpdir):
    f1 = tmpdir.join("file1.json")
    f1.write('{"ronin:<account_s1_address>": "hello"}')
    f2 = tmpdir.join("file2.json")
    config_data = {"ronin:<account_s1_address>": {"passphrase": "", "bip_path": "m/44'/60'/0'/0/48"}}
    f2.write(json.dumps(config_data))
    with patch.object(sys, 'argv', ["", "claim", str(f1), str(f2)]):
        cli.run_cli()
    mock_verify_inputs.assert_called_with()
    mock_prepare_claims.assert_called_with()
    mock_claimsmanager.assert_called_with(str(f1), str(f2), False)


@patch("trezor.TrezorAxieClaimsManager.__init__", return_value=None)
@patch("trezor.TrezorAxieClaimsManager.prepare_claims")
@patch("trezor.TrezorAxieClaimsManager.verify_inputs")
def test_claim(mock_verify_inputs, mock_prepare_claims, mock_claimsmanager, tmpdir):
    f1 = tmpdir.join("file1.json")
    f1.write('{"ronin:<account_s1_address>": "hello"}')
    f2 = tmpdir.join("file2.json")
    config_data = {"ronin:<account_s1_address>": {"passphrase": "", "bip_path": "m/44'/60'/0'/0/48"}}
    f2.write(json.dumps(config_data))
    with patch.object(sys, 'argv', ["", "claim", str(f1), str(f2), '--force']):
        cli.run_cli()
    mock_verify_inputs.assert_called_with()
    mock_prepare_claims.assert_called_with()
    mock_claimsmanager.assert_called_with(str(f1), str(f2), True)


def test_claim_file_check_fail(caplog):
    with patch.object(sys, 'argv', ["", "claim", "p_file.json", "s_file.json"]):
        cli.run_cli()
    assert "Please provide a correct path to the file. Path provided: p_file.json" in caplog.text
    assert "Please review your file paths and re-try." in caplog.text


def test_transfer_file_check_fail(caplog):
    with patch.object(sys, 'argv', ["", "transfer_axies", "t_file.json", "s_file.json"]):
        cli.run_cli()
    assert "Please provide a correct path to the file. Path provided: t_file.json" in caplog.text
    assert "Please review your file paths and re-try." in caplog.text


@patch("trezor.TrezorAxieTransferManager.__init__", return_value=None)
@patch("trezor.TrezorAxieTransferManager.prepare_transfers")
@patch("trezor.TrezorAxieTransferManager.verify_inputs")
def test_transfer(mock_verify_inputs, mock_prepare_transfers, mock_transfersmanager, tmpdir):
    f1 = tmpdir.join("file1.json")
    f1.write('{"ronin:<account_s1_address>": "hello"}')
    f2 = tmpdir.join("file2.json")
    config_data = {"ronin:<account_s1_address>": {"passphrase": "", "bip_path": "m/44'/60'/0'/0/48"}}
    f2.write(json.dumps(config_data))
    with patch.object(sys, 'argv', ["", "transfer_axies", str(f1), str(f2)]):
        cli.run_cli()
    mock_verify_inputs.assert_called_with()
    mock_prepare_transfers.assert_called_with()
    mock_transfersmanager.assert_called_with(str(f1), str(f2), secure=False)


@patch("trezor.TrezorAxieTransferManager.__init__", return_value=None)
@patch("trezor.TrezorAxieTransferManager.prepare_transfers")
@patch("trezor.TrezorAxieTransferManager.verify_inputs")
def test_transfer_secure(mock_verify_inputs, mock_prepare_transfers, mock_transfersmanager, tmpdir):
    f1 = tmpdir.join("file1.json")
    f1.write('{"ronin:<account_s1_address>": "hello"}')
    f2 = tmpdir.join("file2.json")
    config_data = {"ronin:<account_s1_address>": {"passphrase": "", "bip_path": "m/44'/60'/0'/0/48"}}
    f2.write(json.dumps(config_data))
    with patch.object(sys, 'argv', ["", "transfer_axies", str(f1), str(f2), "--safe-mode"]):
        cli.run_cli()
    mock_verify_inputs.assert_called_with()
    mock_prepare_transfers.assert_called_with()
    mock_transfersmanager.assert_called_with(str(f1), str(f2), secure=True)


def test_axie_morphing_file_check_fail(caplog):
    with patch.object(sys, 'argv', ["", "axie_morphing", "s_file.json", "foo,bar"]):
        cli.run_cli()
    assert "Please provide a correct path to the file. Path provided: s_file.json" in caplog.text
    assert "Please review your file paths and re-try." in caplog.text


@patch("trezor.TrezorAxieMorphingManager.__init__", return_value=None)
@patch("axie.Axies.__init__", return_value=None)
@patch("axie.Axies.find_axies_to_morph", return_value=[1, 2, 3])
@patch("trezor.TrezorAxieMorphingManager.execute")
@patch("trezor.TrezorAxieMorphingManager.verify_inputs")
def test_axie_morphing(mock_veritfy_inputs, mock_morphing_execute, mock_find_axies, mock_axies_init, mock_morphingmanager, tmpdir): # noqa
    f = tmpdir.join("file2.json")
    config_data = {"ronin:<account_s1_address>": {"passphrase": "", "bip_path": "m/44'/60'/0'/0/48"}}
    f.write(json.dumps(config_data))
    with patch.object(sys, 'argv', ["", "axie_morphing", str(f), "foo,bar"]):
        cli.run_cli()
    mock_axies_init.assert_has_calls([call('foo'), call('bar')])
    mock_morphingmanager.assert_has_calls([call([1, 2, 3], "foo", str(f)), call([1, 2, 3], "bar", str(f))])
    assert mock_veritfy_inputs.call_count == 2
    assert mock_find_axies.call_count == 2
    assert mock_morphing_execute.call_count == 2


@patch("trezor.TrezorAxieMorphingManager.__init__", return_value=None)
@patch("axie.Axies.__init__", return_value=None)
@patch("axie.Axies.find_axies_to_morph", return_value=[])
@patch("trezor.TrezorAxieMorphingManager.execute")
@patch("trezor.TrezorAxieMorphingManager.verify_inputs")
def test_axie_morphing_none(mock_veritfy_inputs, mock_morphing_execute, mock_find_axies, mock_axies_init, mock_morphingmanager, tmpdir): # noqa
    f = tmpdir.join("file2.json")
    config_data = {"ronin:<account_s1_address>": {"passphrase": "", "bip_path": "m/44'/60'/0'/0/48"}}
    f.write(json.dumps(config_data))
    with patch.object(sys, 'argv', ["", "axie_morphing", str(f), "foo,bar,1"]):
        cli.run_cli()
    mock_axies_init.assert_has_calls([call('foo'), call('bar'), call("1")])
    assert mock_find_axies.call_count == 3
    mock_morphingmanager.assert_not_called()
    mock_veritfy_inputs.assert_not_called()
    mock_morphing_execute.assert_not_called()


def test_axiebreeding_file_check_fail(caplog):
    with patch.object(sys, 'argv', ["", "axie_breeding", "s_file.json", "b_file.json"]):
        cli.run_cli()
    assert "Please provide a correct path to the file. Path provided: s_file.json" in caplog.text
    assert "Please review your file paths and re-try." in caplog.text


@patch("trezor.TrezorAxieBreedManager.__init__", return_value=None)
@patch("trezor.TrezorAxieBreedManager.execute")
@patch("trezor.TrezorAxieBreedManager.verify_inputs")
def test_breeding(mock_verify_inputs, mock_execute_breeding, mock_breedingmanager, tmpdir):
    acc = "ronin:45a1bc784c665e123597d3f29375e45786611234"
    f1 = tmpdir.join("file1.json")
    f1.write('{"ronin:<account_s1_address>": "hello"}')
    f2 = tmpdir.join("file2.json")
    config_data = {"ronin:<account_s1_address>": {"passphrase": "", "bip_path": "m/44'/60'/0'/0/48"}}
    f2.write(json.dumps(config_data))
    with patch.object(sys, 'argv', ["", "axie_breeding", str(f1), str(f2)]):
        with patch.object(builtins, 'input', lambda _: acc):
            cli.run_cli()
    mock_verify_inputs.assert_called_with()
    mock_execute_breeding.assert_called_with()
    mock_breedingmanager.assert_called_with(str(f1), str(f2), acc)


def test_qrcode_file_check_fail(caplog):
    with patch.object(sys, 'argv', ["", "generate_QR", "s_file.json", "p_file.json"]):
        cli.run_cli()
    assert "Please provide a correct path to the file. Path provided: s_file.json" in caplog.text
    assert "Please review your file paths and re-try." in caplog.text


@patch("trezor.TrezorQRCodeManager.__init__", return_value=None)
@patch("trezor.TrezorQRCodeManager.execute")
def test_qrcode(mock_execute, mock_qrcodemanager, tmpdir):
    f1 = tmpdir.join("file1.json")
    f1.write('{"ronin:<account_s1_address>": "hello"}')
    f2 = tmpdir.join("file2.json")
    config_data = {"ronin:<account_s1_address>": {"passphrase": "", "bip_path": "m/44'/60'/0'/0/48"}}
    f2.write(json.dumps(config_data))
    with patch.object(sys, 'argv', ["", "generate_QR", str(f1), str(f2)]):
        cli.run_cli()
    mock_execute.assert_called_with()
    mock_qrcodemanager.assert_called_with(str(f1), str(f2), os.path.dirname(f2))
