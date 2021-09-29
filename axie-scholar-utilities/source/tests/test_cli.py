import sys
import builtins

from docopt import docopt, DocoptExit
from mock import patch
import pytest

import axie_scholar_cli as cli


@pytest.mark.parametrize("params, expected_result",
                         [
                            (["payout", "file1", "file2"],
                             {"--help": False,
                              "--version": False,
                              "--yes": False,
                              "<payments_file>": "file1",
                              "<secrets_file>": "file2",
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              "claim": False,
                              "generate_QR": False,
                              "generate_secrets": False,
                              "payout": True}),
                            (["payout", "file1", "file2", "-y"],
                             {"--help": False,
                              "--version": False,
                              "--yes": True,
                              "<payments_file>": "file1",
                              "<secrets_file>": "file2",
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              "claim": False,
                              "generate_QR": False,
                              "generate_secrets": False,
                              "payout": True}),
                            (["payout", "file1", "file2", "--yes"],
                             {"--help": False,
                              "--version": False,
                              "--yes": True,
                              "<payments_file>": "file1",
                              "<secrets_file>": "file2",
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              "claim": False,
                              "generate_QR": False,
                              "generate_secrets": False,
                              "payout": True}),
                            (["claim", "file1", "file2"],
                             {"--help": False,
                              "--version": False,
                              "--yes": False,
                              "<payments_file>": "file1",
                              "<secrets_file>": "file2",
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              "claim": True,
                              "generate_QR": False,
                              "generate_secrets": False,
                              "payout": False}),
                            (["generate_QR", "file1"],
                             {"--help": False,
                              "--version": False,
                              "--yes": False,
                              "<payments_file>": None,
                              "<secrets_file>": "file1",
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              "claim": False,
                              "generate_QR": True,
                              "generate_secrets": False,
                              "payout": False}),
                            (["generate_secrets", "file1"],
                             {"--help": False,
                              "--version": False,
                              "--yes": False,
                              "<payments_file>": "file1",
                              "<secrets_file>": None,
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              "claim": False,
                              "generate_QR": False,
                              "generate_secrets": True,
                              "payout": False}),
                            (["generate_secrets", "file1", "file2"],
                             {"--help": False,
                              "--version": False,
                              "--yes": False,
                              "<payments_file>": "file1",
                              "<secrets_file>": "file2",
                              '<transfers_file>': None,
                              'transfer_axies': False,
                              "claim": False,
                              "generate_QR": False,
                              "generate_secrets": True,
                              "payout": False}),
                            (["transfer_axies", "file1", "file2"],
                             {"--help": False,
                              "--version": False,
                              "--yes": False,
                              "<payments_file>": None,
                              "<secrets_file>": "file2",
                              '<transfers_file>': "file1",
                              'transfer_axies': True,
                              "claim": False,
                              "generate_QR": False,
                              "generate_secrets": False,
                              "payout": False})
                         ])
def test_parses_params(params, expected_result):
    args = docopt(cli.__doc__, params)
    assert args == expected_result


@pytest.mark.parametrize("params",
                         [
                            (["a", "b", "c"]),
                            (["generate_QR"]),
                            (["generate_secrets"]),
                            (["transfer_axies"]),
                            (["transfer_axies", "file1"]),
                            (["transfer_axies", "file1", "file2", "file3"]),
                            (["claim"]),
                            (["claim", "file1"]),
                            (["payout"]),
                            (["payout", "file1"]),
                            (["payout", "file1", "file2", "file3"])
                         ])
def test_wrong_inputs(params):
    with pytest.raises(DocoptExit):
        docopt(cli.__doc__, params)


def test_payout_file_check_fail(capsys):
    with pytest.raises(Exception) as e:
        with patch.object(sys, 'argv', ["", "payout", "p_file.json", "s_file.json"]):
            cli.run_cli()
            out, _ = capsys.readouterr()
            assert "CRITICAL: Please provide a correct path to the Payments file. Path provided: p_file.json" in out
            assert "CRITICAL: Please provide a correct path to the Secrets file. Path provided: s_file.json" in out
    assert str(e.value) == "Please review your file paths and re-try."


def test_secret_gen_file_check_fail(capsys):
    with pytest.raises(Exception) as e:
        with patch.object(sys, 'argv', ["", "generate_secrets", "p_file.json", "s_file.json"]):
            cli.run_cli()
            out, _ = capsys.readouterr()
            assert "CRITICAL: Please provide a correct path to the Payments file. Path provided: p_file.json" in out
            assert "CRITICAL: Please provide a correct path to the Secrets file. Path provided: s_file.json" in out
    assert str(e.value) == "Please review your file paths and re-try."


def test_secret_gen_file_check_fail_only_payment_file(capsys):
    with pytest.raises(Exception) as e:
        with patch.object(sys, 'argv', ["", "generate_secrets", "p_file.json"]):
            cli.run_cli()
            out, _ = capsys.readouterr()
            assert "CRITICAL: Please provide a correct path to the Payments file. Path provided: p_file.json" in out
            assert "CRITICAL: Please provide a correct path to the Secrets file. Path provided: s_file.json" not in out
    assert str(e.value) == "Please review your file paths and re-try."


@pytest.mark.parametrize("params",
                         [
                            (["", "generate_QR", "file1"])
                         ])
def test_not_implemented_methods(params):
    with pytest.raises(NotImplementedError) as e:
        with patch.object(sys, 'argv', params):
            cli.run_cli()
    assert str(e.value) == "Sorry, I have yet to implement this command"


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


def test_claim_file_check_fail(capsys):
    with pytest.raises(Exception) as e:
        with patch.object(sys, 'argv', ["", "claim", "p_file.json", "s_file.json"]):
            cli.run_cli()
            out, _ = capsys.readouterr()
            assert "CRITICAL: Please provide a correct path to the Payments file. Path provided: p_file.json" in out
            assert "CRITICAL: Please provide a correct path to the Secrets file. Path provided: s_file.json" in out
    assert str(e.value) == "Please review your file paths and re-try."


def test_transfer_file_check_fail(capsys):
    with pytest.raises(Exception) as e:
        with patch.object(sys, 'argv', ["", "transfer_axies", "t_file.json", "s_file.json"]):
            cli.run_cli()
            out, _ = capsys.readouterr()
            assert "CRITICAL: Please provide a correct path to the Payments file. Path provided: t_file.json" in out
            assert "CRITICAL: Please provide a correct path to the Secrets file. Path provided: s_file.json" in out
    assert str(e.value) == "Please review your file paths and re-try."


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