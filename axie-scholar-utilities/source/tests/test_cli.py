import sys
import builtins

from docopt import docopt, DocoptExit
from mock import patch
import pytest

import axie_scholar_cli as cli


@pytest.mark.parametrize("params, expected_result",
                         [
                            (["payout", "file1", "file2"],
                             {"<payments_file>": "file1",
                              "<secrets_file>": "file2",
                              "claim": False,
                              "generate_QR": False,
                              "generate_secrets": False,
                              "payout": True}),
                            (["claim", "file1"],
                             {"<payments_file>": None,
                              "<secrets_file>": "file1",
                              "claim": True,
                              "generate_QR": False,
                              "generate_secrets": False,
                              "payout": False}),
                            (["generate_QR", "file1"],
                             {"<payments_file>": None,
                              "<secrets_file>": "file1",
                              "claim": False,
                              "generate_QR": True,
                              "generate_secrets": False,
                              "payout": False}),
                            (["generate_secrets", "file1"],
                             {"<payments_file>": "file1",
                              "<secrets_file>": None,
                              "claim": False,
                              "generate_QR": False,
                              "generate_secrets": True,
                              "payout": False}),
                            (["generate_secrets", "file1", "file2"],
                             {"<payments_file>": "file1",
                              "<secrets_file>": "file2",
                              "claim": False,
                              "generate_QR": False,
                              "generate_secrets": True,
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
                            (["", "claim", "file1"]),
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
    f2 = tmpdir.join("file2.json")
    f2.write("{}")
    with patch.object(builtins, 'input', lambda _: 'some_input'):
        cli.generate_secrets_file(f1.strpath, f2.strpath)
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
