import builtins

from mock import patch, call, mock_open

from axie.utils import check_balance, RONIN_PROVIDER, SLP_CONTRACT


@patch("web3.eth.Eth.contract.functions.get_balance.call", return_value=1)
@patch("web3.Web3.toChecksumAddress", return_value="checksum")
@patch("web3.eth.Eth.contract")
@patch("web3.Web3.HTTPProvider", return_value='foo')
def test_check_balance(mock_provider, mock_contract, mock_checksum, _):
    with patch.object(builtins,
                      "open",
                      mock_open(read_data='{"foo": "bar"}')) as mock_file:
        result = check_balance("ronin:abc")
    mock_file.assert_called_with("axie/min_abi.json")
    mock_provider.assert_called_with(RONIN_PROVIDER)
    mock_checksum.assert_has_calls([call(SLP_CONTRACT), call("0xabc")])
    mock_contract.assert_called_with(address="checksum", abi={"foo": "bar"})
    assert result == 1