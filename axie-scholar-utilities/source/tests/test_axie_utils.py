import builtins

import pytest
from mock import patch, call, mock_open

from axie.utils import (
    check_balance,
    load_json,
    get_nonce,
    RONIN_PROVIDER,
    SLP_CONTRACT
)


@patch("web3.eth.Eth.contract.functions.balanceOf.call", return_value=1)
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("web3.eth.Eth.contract")
@patch("web3.Web3.HTTPProvider", return_value='foo')
def test_check_balance(mock_provider, mock_contract, mock_checksum, _):
    with patch.object(builtins,
                      "open",
                      mock_open(read_data='{"foo": "bar"}')) as mock_file:
        result = check_balance("ronin:abc")
    mock_file.assert_called_with("axie/slp_abi.json")
    mock_provider.assert_called_with(RONIN_PROVIDER)
    mock_checksum.assert_has_calls([call(SLP_CONTRACT), call("0xabc")])
    mock_contract.assert_called_with(address="checksum", abi={"foo": "bar"})
    assert result == 1


def test_load_json_safeguard():
    with pytest.raises(Exception) as e:
        load_json("non_existent.json")
    assert str(e.value) == ("File path non_existent.json does not exist. "
                            "Please provide a correct one")


def test_load_json(tmpdir):
    f = tmpdir.join("test.json")
    f.write('{"foo": "bar"}')
    loaded = load_json(f)
    assert loaded == {"foo": "bar"}


def test_load_json_not_json(tmpdir):
    f = tmpdir.join("test.txt")
    f.write("foo bar")
    with pytest.raises(Exception) as e:
        load_json(f)
    assert str(e.value) == f"File in path {f} is not a correctly encoded JSON."


@patch("web3.Web3.toChecksumAddress", return_value="foo")
@patch("web3.eth.Eth.get_transaction_count", return_value=123)
def test_get_nonce_calls_w3(mocked_transaction_count, mocked_checksum):
    nonce = get_nonce("ronin:from_ronin")
    mocked_checksum.assert_called_with("0xfrom_ronin")
    mocked_transaction_count.assert_called_with("foo")
    assert nonce == 123
