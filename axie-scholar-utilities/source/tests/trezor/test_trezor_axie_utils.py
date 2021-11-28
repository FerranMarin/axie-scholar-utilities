import pytest
from mock import patch, call

from axie.utils import (
    check_balance,
    load_json,
    get_nonce,
    RONIN_PROVIDER,
    SLP_CONTRACT,
    AXS_CONTRACT,
    AXIE_CONTRACT,
    WETH_CONTRACT,
    BALANCE_ABI,
    USER_AGENT
)


@patch("web3.eth.Eth.contract.functions.balanceOf.call", return_value=1)
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("web3.eth.Eth.contract")
@patch("web3.Web3.HTTPProvider", return_value='foo')
def test_check_balance_slp(mock_provider, mock_contract, mock_checksum, _):
    result = check_balance("ronin:abc")
    mock_provider.assert_called_with(
        RONIN_PROVIDER,
        request_kwargs={"headers":{"content-type":"application/json","user-agent": USER_AGENT}}
    )
    mock_checksum.assert_has_calls([call(SLP_CONTRACT), call("0xabc")])
    mock_contract.assert_called_with(address="checksum", abi=BALANCE_ABI)
    assert result == 1


@patch("web3.eth.Eth.contract.functions.balanceOf.call", return_value=1)
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("web3.eth.Eth.contract")
@patch("web3.Web3.HTTPProvider", return_value='foo')
def test_check_balance_slp_explicit(mock_provider, mock_contract, mock_checksum, _):
    result = check_balance("ronin:abc", 'slp')
    mock_provider.assert_called_with(
        RONIN_PROVIDER,
        request_kwargs={"headers":{"content-type":"application/json","user-agent": USER_AGENT}}
    )
    mock_checksum.assert_has_calls([call(SLP_CONTRACT), call("0xabc")])
    mock_contract.assert_called_with(address="checksum", abi=BALANCE_ABI)
    assert result == 1


@patch("web3.eth.Eth.contract.functions.balanceOf.call", return_value=1)
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("web3.eth.Eth.contract")
@patch("web3.Web3.HTTPProvider", return_value='foo')
def test_check_balance_axs(mock_provider, mock_contract, mock_checksum, _):
    result = check_balance("ronin:abc", "axs")
    mock_provider.assert_called_with(
        RONIN_PROVIDER,
        request_kwargs={"headers":{"content-type":"application/json","user-agent": USER_AGENT}}
    )
    mock_checksum.assert_has_calls([call(AXS_CONTRACT), call("0xabc")])
    mock_contract.assert_called_with(address="checksum", abi=BALANCE_ABI)
    assert result == 1


@patch("web3.eth.Eth.contract.functions.balanceOf.call", return_value=1000000000000000000)
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("web3.eth.Eth.contract")
@patch("web3.Web3.HTTPProvider", return_value='foo')
def test_check_balance_weth(mock_provider, mock_contract, mock_checksum, _):
    result = check_balance("ronin:abc", "weth")
    mock_provider.assert_called_with(
        RONIN_PROVIDER,
        request_kwargs={"headers":{"content-type":"application/json","user-agent": USER_AGENT}}
    )
    mock_checksum.assert_has_calls([call(WETH_CONTRACT), call("0xabc")])
    mock_contract.assert_called_with(address="checksum", abi=BALANCE_ABI)
    assert result == 1.0


@patch("web3.eth.Eth.contract.functions.balanceOf.call", return_value=1)
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("web3.eth.Eth.contract")
@patch("web3.Web3.HTTPProvider", return_value='foo')
def test_check_balance_axie(mock_provider, mock_contract, mock_checksum, _):
    result = check_balance("ronin:abc", "axies")
    mock_provider.assert_called_with(
        RONIN_PROVIDER,
        request_kwargs={"headers":{"content-type":"application/json","user-agent": USER_AGENT}}
    )
    mock_checksum.assert_has_calls([call(AXIE_CONTRACT), call("0xabc")])
    mock_contract.assert_called_with(address="checksum", abi=BALANCE_ABI)
    assert result == 1


@patch("web3.eth.Eth.contract.functions.balanceOf.call", return_value=1)
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("web3.eth.Eth.contract")
@patch("web3.Web3.HTTPProvider", return_value='foo')
def test_check_balance_wrong(mock_provider, mock_contract, mock_checksum, _):
    result = check_balance("ronin:abc", "foo")
    mock_provider.assert_not_called()
    mock_checksum.assert_not_called()
    mock_contract.assert_not_called()
    assert result == 0


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
