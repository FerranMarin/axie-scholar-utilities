import sys
import builtins
import json

from docopt import docopt, DocoptExit
from mock import patch, call
import pytest

import axie_scholar_cli as cli


@pytest.mark.parametrize("params, expected_result",
                         [
                            (["payout", "file1", "file2"],
                             {"--help": False,
                              "--version": False,
                              "--yes": False,
                              '<list_of_accounts>': None, 
                              'axie_morphing': False,
                              "<payments_file>": "file1",
                              "<secrets_file>": "file2",
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              '<csv_file>': None,
                              'mass_update_secrets': False,
                              '<breedings_file>': None,
                              'axie_breeding': False,
                              "claim": False,
                              "generate_QR": False,
                              "generate_secrets": False,
                              'generate_payments': False,
                              "payout": True}),
                            (["payout", "file1", "file2", "-y"],
                             {"--help": False,
                              "--version": False,
                              "--yes": True,
                              '<list_of_accounts>': None, 
                              'axie_morphing': False,
                              "<payments_file>": "file1",
                              "<secrets_file>": "file2",
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              '<csv_file>': None,
                              'mass_update_secrets': False,
                              '<breedings_file>': None,
                              'axie_breeding': False,
                              "claim": False,
                              "generate_QR": False,
                              "generate_secrets": False,
                              'generate_payments': False,
                              "payout": True}),
                            (["payout", "file1", "file2", "--yes"],
                             {"--help": False,
                              "--version": False,
                              "--yes": True,
                              '<list_of_accounts>': None, 
                              'axie_morphing': False,
                              "<payments_file>": "file1",
                              "<secrets_file>": "file2",
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              '<csv_file>': None,
                              'mass_update_secrets': False,
                              '<breedings_file>': None,
                              'axie_breeding': False,
                              "claim": False,
                              "generate_QR": False,
                              "generate_secrets": False,
                              'generate_payments': False,
                              "payout": True}),
                            (["claim", "file1", "file2"],
                             {"--help": False,
                              "--version": False,
                              "--yes": False,
                              '<list_of_accounts>': None, 
                              'axie_morphing': False,
                              "<payments_file>": "file1",
                              "<secrets_file>": "file2",
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              '<csv_file>': None,
                              'mass_update_secrets': False,
                              '<breedings_file>': None,
                              'axie_breeding': False,
                              "claim": True,
                              "generate_QR": False,
                              "generate_secrets": False,
                              'generate_payments': False,
                              "payout": False}),
                            (["generate_secrets", "file1"],
                             {"--help": False,
                              "--version": False,
                              "--yes": False,
                              '<list_of_accounts>': None, 
                              'axie_morphing': False,
                              "<payments_file>": "file1",
                              "<secrets_file>": None,
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              '<csv_file>': None,
                              'mass_update_secrets': False,
                              '<breedings_file>': None,
                              'axie_breeding': False,
                              "claim": False,
                              "generate_QR": False,
                              "generate_secrets": True,
                              'generate_payments': False,
                              "payout": False}),
                            (["generate_secrets", "file1", "file2"],
                             {"--help": False,
                              "--version": False,
                              "--yes": False,
                              '<list_of_accounts>': None, 
                              'axie_morphing': False,
                              "<payments_file>": "file1",
                              "<secrets_file>": "file2",
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              '<csv_file>': None,
                              'mass_update_secrets': False,
                              '<breedings_file>': None,
                              'axie_breeding': False,
                              "claim": False,
                              "generate_QR": False,
                              "generate_secrets": True,
                              'generate_payments': False,
                              "payout": False}),
                            (["transfer_axies", "file1", "file2"],
                             {"--help": False,
                              "--version": False,
                              "--yes": False,
                              '<list_of_accounts>': None, 
                              'axie_morphing': False,
                              "<payments_file>": None,
                              "<secrets_file>": "file2",
                              '<transfers_file>': "file1",
                              'transfer_axies': True,
                              '<csv_file>': None,
                              'mass_update_secrets': False,
                              '<breedings_file>': None,
                              'axie_breeding': False,
                              "claim": False,
                              "generate_QR": False,
                              "generate_secrets": False,
                              'generate_payments': False,
                              "payout": False}),
                            (["mass_update_secrets", "file1", "file2"],
                             {"--help": False,
                              "--version": False,
                              "--yes": False,
                              '<list_of_accounts>': None, 
                              'axie_morphing': False,
                              "<payments_file>": None,
                              "<secrets_file>": "file2",
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              '<csv_file>': "file1",
                              'mass_update_secrets': True,
                              '<breedings_file>': None,
                              'axie_breeding': False,
                              "claim": False,
                              "generate_QR": False,
                              "generate_secrets": False,
                              'generate_payments': False,
                              "payout": False}),
                            (["generate_payments", "file1", "file2"],
                             {"--help": False,
                              "--version": False,
                              "--yes": False,
                              '<list_of_accounts>': None, 
                              'axie_morphing': False,
                              "<payments_file>": "file2",
                              "<secrets_file>": None,
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              '<csv_file>': "file1",
                              'mass_update_secrets': False,
                              '<breedings_file>': None,
                              'axie_breeding': False,
                              "claim": False,
                              "generate_QR": False,
                              "generate_secrets": False,
                              'generate_payments': True,
                              "payout": False}),
                            (["generate_payments", "file1"],
                             {"--help": False,
                              "--version": False,
                              "--yes": False,
                              '<list_of_accounts>': None, 
                              'axie_morphing': False,
                              "<payments_file>": None,
                              "<secrets_file>": None,
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              '<csv_file>': "file1",
                              'mass_update_secrets': False,
                              '<breedings_file>': None,
                              'axie_breeding': False,
                              "claim": False,
                              "generate_QR": False,
                              "generate_secrets": False,
                              'generate_payments': True,
                              "payout": False}),
                            (["axie_morphing", "file1", "a,b,c"],
                             {"--help": False,
                              "--version": False,
                              "--yes": False,
                              '<list_of_accounts>': "a,b,c", 
                              'axie_morphing': True,
                              "<payments_file>": None,
                              "<secrets_file>": "file1",
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              '<csv_file>': None,
                              'mass_update_secrets': False,
                              '<breedings_file>': None,
                              'axie_breeding': False,
                              "claim": False,
                              "generate_QR": False,
                              "generate_secrets": False,
                              'generate_payments': False,
                              "payout": False}),
                            (["axie_breeding", "file1", "file2"],
                             {"--help": False,
                              "--version": False,
                              "--yes": False,
                              '<list_of_accounts>': None, 
                              'axie_morphing': False,
                              "<payments_file>": None,
                              "<secrets_file>": "file2",
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              '<csv_file>': None,
                              'mass_update_secrets': False,
                              '<breedings_file>': "file1",
                              'axie_breeding': True,
                              "claim": False,
                              "generate_QR": False,
                              "generate_secrets": False,
                              'generate_payments': False,
                              "payout": False}),
                            (["generate_QR", "file1", "file2"],
                             {"--help": False,
                              "--version": False,
                              "--yes": False,
                              '<list_of_accounts>': None, 
                              'axie_morphing': False,
                              "<payments_file>": "file1",
                              "<secrets_file>": "file2",
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              '<csv_file>': None,
                              'mass_update_secrets': False,
                              '<breedings_file>': None,
                              'axie_breeding': False,
                              "claim": False,
                              "generate_QR": True,
                              "generate_secrets": False,
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
                            (["mass_update_secrets"]),
                            (["mass_update_secrets", "file1"]),
                            (["mass_update_secrets", "file1", "file2", "file3"]),
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
    with patch.object(sys, 'argv', ["", "payout", "p_file.json", "s_file.json"]):
        cli.run_cli()
    assert "Please provide a correct path to the file. Path provided: p_file.json" in caplog.text
    assert "Please review your file paths and re-try." in caplog.text


def test_secret_gen_file_check_fail(caplog):
    with patch.object(sys, 'argv', ["", "generate_secrets", "p_file.json", "s_file.json"]):
        cli.run_cli()
    assert "Please provide a correct path to the file. Path provided: s_file.json" in caplog.text
    assert "Please review your file paths and re-try." in caplog.text


def test_secret_gen_file_check_fail_only_payment_file(caplog):
    with patch.object(sys, 'argv', ["", "generate_secrets", "p_file.json"]):
        cli.run_cli()
    assert "Please provide a correct path to the file. Path provided: p_file.json" in caplog.text
    assert "Please review your file paths and re-try." in caplog.text


def test_generate_secrets_no_secrets_file(tmpdir):
    f1 = tmpdir.join("file1.json")
    f1.write('{"Scholars":[{"Name": "Acc1", "AccountAddress": "ronin:<account_s1_address>"},'
             '{"Name": "Acc2", "AccountAddress": "ronin:<account_s2_address>"}]}')
    f2 = tmpdir.join("secrets.json")
    with patch.object(builtins, 'input', lambda _: 'some_input'):
        cli.generate_secrets_file(f1.strpath)
    assert f2.read() == ('{\n    "ronin:<account_s1_address>": "some_input",\n'
                         '    "ronin:<account_s2_address>": "some_input"\n}')


def test_generate_secrets_no_secrets_file_other_folder(tmpdir):
    f1 = tmpdir.mkdir("other_folder").join("file1.json")
    f1.write('{"Scholars":[{"Name": "Acc1", "AccountAddress": "ronin:<account_s1_address>"},'
             '{"Name": "Acc2", "AccountAddress": "ronin:<account_s2_address>"}]}')
    f2 = tmpdir.join("other_folder/secrets.json")
    with patch.object(builtins, 'input', lambda _: 'some_input'):
        cli.generate_secrets_file(f1.strpath)
    assert f2.read() == ('{\n    "ronin:<account_s1_address>": "some_input",\n'
                         '    "ronin:<account_s2_address>": "some_input"\n}')


def test_generate_secrets_already_there(tmpdir):
    f1 = tmpdir.join("file1.json")
    f1.write('{"Scholars":[{"Name": "Acc1", "AccountAddress": "ronin:<account_s1_address>"},'
             '{"Name": "Acc2", "AccountAddress": "ronin:<account_s2_address>"}]}')
    f2 = tmpdir.join("file2.json")
    f2.write('{"ronin:<account_s1_address>": "hello", "ronin:<account_s2_address>": "test"}')
    expected_out = f2.read()
    with patch.object(builtins, 'input', lambda _: 'some_input'):
        cli.generate_secrets_file(f1.strpath, f2.strpath)
    assert f2.read() == expected_out


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
    print(json.loads(f2.read()))
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


def test_generate_secrets_partially_there(tmpdir):
    f1 = tmpdir.join("file1.json")
    f1.write('{"Scholars":[{"Name": "Acc1", "AccountAddress": "ronin:<account_s1_address>"},'
             '{"Name": "Acc2", "AccountAddress": "ronin:<account_s2_address>"}]}')
    f2 = tmpdir.join("file2.json")
    f2.write('{"ronin:<account_s1_address>": "hello"}')
    with patch.object(builtins, 'input', lambda _: 'some_input'):
        cli.generate_secrets_file(f1.strpath, f2.strpath)
    assert f2.read() == ('{\n    "ronin:<account_s1_address>": "hello",\n'
                         '    "ronin:<account_s2_address>": "some_input"\n}')


@patch("axie.AxiePaymentsManager.__init__", return_value=None)
@patch("axie.AxiePaymentsManager.verify_inputs")
@patch("axie.AxiePaymentsManager.prepare_payout")
def test_payout_takes_auto_parameter(mock_prepare_payout, mock_verify_input, mocked_paymentsmanager, tmpdir):
    f1 = tmpdir.join("file1.json")
    f1.write('{"Scholars":[{"Name": "Acc1", "AccountAddress": "ronin:<account_s1_address>"}]}')
    f2 = tmpdir.join("file2.json")
    f2.write('{"ronin:<account_s1_address>": "hello"}')
    with patch.object(sys, 'argv', ["", "payout", str(f1), str(f2)]):
        cli.run_cli()
    mock_prepare_payout.assert_called_with()
    mock_verify_input.assert_called_with()
    mocked_paymentsmanager.assert_called_with(str(f1), str(f2), auto=False)


@patch("axie.AxiePaymentsManager.__init__", return_value=None)
@patch("axie.AxiePaymentsManager.verify_inputs")
@patch("axie.AxiePaymentsManager.prepare_payout")
def test_payout_takes_auto_parameter_yes(mock_prepare_payout, mock_verify_inputs, mocked_paymentsmanager, tmpdir):
    f1 = tmpdir.join("file1.json")
    f1.write('{"Scholars":[{"Name": "Acc1", "AccountAddress": "ronin:<account_s1_address>"}]}')
    f2 = tmpdir.join("file2.json")
    f2.write('{"ronin:<account_s1_address>": "hello"}')
    with patch.object(sys, 'argv', ["", "payout", str(f1), str(f2), "-y"]):
        cli.run_cli()
    mock_prepare_payout.assert_called_with()
    mock_verify_inputs.assert_called_with()
    mocked_paymentsmanager.assert_called_with(str(f1), str(f2), auto=True)


@patch("axie.AxieClaimsManager.__init__", return_value=None)
@patch("axie.AxieClaimsManager.prepare_claims")
@patch("axie.AxieClaimsManager.verify_inputs")
def test_claim(mock_verify_inputs, mock_prepare_claims, mock_claimsmanager, tmpdir):
    f1 = tmpdir.join("file1.json")
    f1.write('{"ronin:<account_s1_address>": "hello"}')
    f2 = tmpdir.join("file2.json")
    f2.write('{"ronin:<account_s1_address>": "hello"}')
    with patch.object(sys, 'argv', ["", "claim", str(f1), str(f2)]):
        cli.run_cli()
    mock_verify_inputs.assert_called_with()
    mock_prepare_claims.assert_called_with()
    mock_claimsmanager.assert_called_with(str(f1), str(f2))


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


@patch("axie.AxieTransferManager.__init__", return_value=None)
@patch("axie.AxieTransferManager.prepare_transfers")
@patch("axie.AxieTransferManager.verify_inputs")
def test_transfer(mock_verify_inputs, mock_prepare_transfers, mock_transfersmanager, tmpdir):
    f1 = tmpdir.join("file1.json")
    f1.write('{"ronin:<account_s1_address>": "hello"}')
    f2 = tmpdir.join("file2.json")
    f2.write('{"ronin:<account_s1_address>": "hello"}')
    with patch.object(sys, 'argv', ["", "transfer_axies", str(f1), str(f2)]):
        cli.run_cli()
    mock_verify_inputs.assert_called_with()
    mock_prepare_transfers.assert_called_with()
    mock_transfersmanager.assert_called_with(str(f1), str(f2))


def test_axie_morphing_file_check_fail(caplog):
    with patch.object(sys, 'argv', ["", "axie_morphing", "s_file.json", "foo,bar"]):
        cli.run_cli()
    assert "Please provide a correct path to the file. Path provided: s_file.json" in caplog.text
    assert "Please review your file paths and re-try." in caplog.text


@patch("axie.AxieMorphingManager.__init__", return_value=None)
@patch("axie.Axies.__init__", return_value=None)
@patch("axie.Axies.find_axies_to_morph", return_value=[1,2,3])
@patch("axie.AxieMorphingManager.execute")
@patch("axie.AxieMorphingManager.verify_inputs")
def test_axie_morphing(mock_veritfy_inputs, mock_morphing_execute, mock_find_axies, mock_axies_init, mock_morphingmanager, tmpdir):
    f = tmpdir.join("file2.json")
    f.write('{"ronin:<account_s1_address>": "hello"}')
    with patch.object(sys, 'argv', ["", "axie_morphing", str(f), "foo,bar"]):
        cli.run_cli()
    mock_axies_init.assert_has_calls([call('foo'), call('bar')])    
    mock_morphingmanager.assert_has_calls([call([1,2,3], "foo", str(f)), call([1,2,3], "bar", str(f))])
    assert mock_veritfy_inputs.call_count == 2
    assert mock_find_axies.call_count == 2
    assert mock_morphing_execute.call_count == 2


def test_axiebreeding_file_check_fail(caplog):
    with patch.object(sys, 'argv', ["", "axie_breeding", "s_file.json", "b_file.json"]):
        cli.run_cli()
    assert "Please provide a correct path to the file. Path provided: s_file.json" in caplog.text
    assert "Please review your file paths and re-try." in caplog.text


@patch("axie.BreedManager.__init__", return_value=None)
@patch("axie.BreedManager.execute")
@patch("axie.BreedManager.verify_inputs")
def test_breeding(mock_verify_inputs, mock_execute_breeding, mock_breedingmanager, tmpdir):
    acc = "ronin:45a1bc784c665e123597d3f29375e45786611234"
    f1 = tmpdir.join("file1.json")
    f1.write('{"ronin:<account_s1_address>": "hello"}')
    f2 = tmpdir.join("file2.json")
    f2.write('{"ronin:<account_s1_address>": "hello"}')
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


@patch("axie.QRCodeManager.__init__", return_value=None)
@patch("axie.QRCodeManager.execute")
def test_qrcode(mock_execute, mock_qrcodemanager, tmpdir):
    f1 = tmpdir.join("file1.json")
    f1.write('{"ronin:<account_s1_address>": "hello"}')
    f2 = tmpdir.join("file2.json")
    f2.write('{"ronin:<account_s1_address>": "hello"}')
    with patch.object(sys, 'argv', ["", "generate_QR", str(f1), str(f2)]):
        cli.run_cli()
    mock_execute.assert_called_with()
    mock_qrcodemanager.assert_called_with(str(f1), str(f2))
