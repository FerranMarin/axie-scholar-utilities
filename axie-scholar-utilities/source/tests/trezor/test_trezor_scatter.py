from mock import patch

from trezor import TrezorScatterRonManager

@patch("trezor.trezor_scatter.get_default_client", return_value='client')
@patch("trezor.trezor_scatter.TrezorScatterRonManager.load_scatter", return_value='foo')
def test_init_scatter_ron_manager(mocked_load, mocked_client):
    s = TrezorScatterRonManager('from_acc', {"foo": "bar"}, {"from_acc": {"bip_path": "path", "passphrase": ""}}, 1)
    mocked_load.assert_called_with({"foo": "bar"})
    assert s.min_ron == 1
    assert s.from_acc == 'from_acc'
    assert s.bip_path == 'path'
    assert s.scatter_accounts_amounts == 'foo'
    assert s.client == 'client'
    mocked_client.assert_called()


@patch("trezor.trezor_scatter.get_default_client", return_value='client')
@patch('trezor.trezor_scatter.check_balance', return_value=0)
def test_load_scatter_ron_manager_new(mocked_check, mocked_client):
    payments = {
    "scholars": [
        {
            "name": "Scholar 1",
            "ronin": "ronin:<account_s1_address>",
            "splits": [
                {
                    "persona": "Manager",
                    "percentage": 44,
                    "ronin": "ronin:<manager_address>"
                },
                {
                    "persona": "Scholar",
                    "percentage": 40,
                    "ronin": "ronin:<scholar_1_address>"
                },
                {
                    "persona": "Other Person",
                    "percentage": 6,
                    "ronin": "ronin:<other_person_address>"
                },
                {
                    "persona": "Trainer",
                    "percentage": 10,
                    "ronin": "ronin:<trainer_address>"
                }
            ]
        },
        {
            "name": "Scholar 2",
            "ronin": "ronin:<account_s2_address>",
            "splits": [
                {
                    "persona": "Manager",
                    "percentage": 5,
                    "ronin": "ronin:<manager_address>"
                },
                {
                    "persona": "Scholar",
                    "percentage": 55,
                    "ronin": "ronin:<scholar_2_address>"
                },
                {
                    "persona": "Other Person",
                    "percentage": 40,
                    "ronin": "ronin:<other_address>"
                }
            ]
        }
    ],
    "donations": [
        {
            "name": "Entity 1",
            "ronin": "ronin:<donation_entity_1_address>",
            "percentage": 1
        },
        {
            "name": "Entity 2",
            "ronin": "ronin:<donation_entity_2_address>",
            "percentage": 1
        }
    ]}
    s = TrezorScatterRonManager('from_acc', payments, {"from_acc": {"bip_path": "path", "passphrase": ""}}, 1)
    assert s.scatter_accounts_amounts == {
        "ronin:<account_s1_address>": 1,
        "ronin:<account_s2_address>": 1
    }
    mocked_check.assert_called()
    mocked_client.assert_called()


@patch("trezor.trezor_scatter.get_default_client", return_value='client')
@patch('trezor.trezor_scatter.check_balance', return_value=0)
def test_load_scatter_ron_manager_old(mocked_check, mocked_client):
    payments = {
    "Manager": "ronin:<Manager address here>",
    "Scholars": [
        {
            "Name": "Scholar 1",
            "AccountAddress": "ronin:<account_s1_address>",
            "ScholarPayoutAddress": "ronin:<scholar_address>",
            "ScholarPercent": 50,
            "TrainerPercent": 10,
            "TrainerPayoutAddress": "ronin:<trainer_address>"
        },
        {
            "Name": "Scholar 2",
            "AccountAddress": "ronin:<account_s2_address>",
            "ScholarPayoutAddress": "ronin:<scholar2_address>",
            "TrainerPayoutAddress": "ronin:<trainer_address>",
            "ScholarPercent": 50,
            "TrainerPercent": 5,
            "ScholarPayout": 14
        },
        {
            "Name": "Scholar 3",
            "AccountAddress": "ronin:<account_s3_address>",
            "ScholarPayoutAddress": "ronin:<scholar3_address>",
            "ScholarPercent": 50
        }
    ],
    "Donations": [
        {
            "Name": "Entity 1",
            "AccountAddress": "ronin:<donation_entity_1_address>",
            "Percent": 1
        },
        {
            "Name": "Entity 2",
            "AccountAddress": "ronin:<donation_entity_2_address>",
            "Percent": 1
        }
    ]}
    s = TrezorScatterRonManager('from_acc', payments, {"from_acc": {"bip_path": "path", "passphrase": ""}}, 1)
    assert s.scatter_accounts_amounts == {
        "ronin:<account_s1_address>": 1,
        "ronin:<account_s2_address>": 1,
        "ronin:<account_s3_address>": 1
    }
    mocked_check.assert_called()
    mocked_client.assert_called()


@patch("trezor.trezor_scatter.get_default_client", return_value='client')
@patch('trezor.trezor_scatter.check_balance', return_value=0.5)
def test_load_scatter_ron_manager_new_only_missing_ron(mocked_check, mocked_client):
    payments = {
    "scholars": [
        {
            "name": "Scholar 1",
            "ronin": "ronin:<account_s1_address>",
            "splits": [
                {
                    "persona": "Manager",
                    "percentage": 44,
                    "ronin": "ronin:<manager_address>"
                },
                {
                    "persona": "Scholar",
                    "percentage": 40,
                    "ronin": "ronin:<scholar_1_address>"
                },
                {
                    "persona": "Other Person",
                    "percentage": 6,
                    "ronin": "ronin:<other_person_address>"
                },
                {
                    "persona": "Trainer",
                    "percentage": 10,
                    "ronin": "ronin:<trainer_address>"
                }
            ]
        },
        {
            "name": "Scholar 2",
            "ronin": "ronin:<account_s2_address>",
            "splits": [
                {
                    "persona": "Manager",
                    "percentage": 5,
                    "ronin": "ronin:<manager_address>"
                },
                {
                    "persona": "Scholar",
                    "percentage": 55,
                    "ronin": "ronin:<scholar_2_address>"
                },
                {
                    "persona": "Other Person",
                    "percentage": 40,
                    "ronin": "ronin:<other_address>"
                }
            ]
        }
    ],
    "donations": [
        {
            "name": "Entity 1",
            "ronin": "ronin:<donation_entity_1_address>",
            "percentage": 1
        },
        {
            "name": "Entity 2",
            "ronin": "ronin:<donation_entity_2_address>",
            "percentage": 1
        }
    ]}
    s = TrezorScatterRonManager('from_acc', payments, {"from_acc": {"bip_path": "path", "passphrase": ""}}, 1)
    assert s.scatter_accounts_amounts == {
        "ronin:<account_s1_address>": 0.5,
        "ronin:<account_s2_address>": 0.5}
    mocked_check.assert_called()
    mocked_client.assert_called()


@patch("trezor.trezor_scatter.get_default_client", return_value='client')
@patch('trezor.trezor_scatter.check_balance', return_value=0.5)
def test_load_scatter_ron_manager_old_only_missing_ron(mocked_check, mocked_client):
    payments = {
    "Manager": "ronin:<Manager address here>",
    "Scholars": [
        {
            "Name": "Scholar 1",
            "AccountAddress": "ronin:<account_s1_address>",
            "ScholarPayoutAddress": "ronin:<scholar_address>",
            "ScholarPercent": 50,
            "TrainerPercent": 10,
            "TrainerPayoutAddress": "ronin:<trainer_address>"
        },
        {
            "Name": "Scholar 2",
            "AccountAddress": "ronin:<account_s2_address>",
            "ScholarPayoutAddress": "ronin:<scholar2_address>",
            "TrainerPayoutAddress": "ronin:<trainer_address>",
            "ScholarPercent": 50,
            "TrainerPercent": 5,
            "ScholarPayout": 14
        },
        {
            "Name": "Scholar 3",
            "AccountAddress": "ronin:<account_s3_address>",
            "ScholarPayoutAddress": "ronin:<scholar3_address>",
            "ScholarPercent": 50
        }
    ],
    "Donations": [
        {
            "Name": "Entity 1",
            "AccountAddress": "ronin:<donation_entity_1_address>",
            "Percent": 1
        },
        {
            "Name": "Entity 2",
            "AccountAddress": "ronin:<donation_entity_2_address>",
            "Percent": 1
        }
    ]}
    s = TrezorScatterRonManager('from_acc', payments, {"from_acc": {"bip_path": "path", "passphrase": ""}}, 1)
    assert s.scatter_accounts_amounts == {
        "ronin:<account_s1_address>": 0.5,
        "ronin:<account_s2_address>": 0.5,
        "ronin:<account_s3_address>": 0.5
    }
    mocked_check.assert_called()
    mocked_client.assert_called()


@patch("trezor.trezor_scatter.get_default_client", return_value='client')
@patch("axie_utils.TrezorScatter.execute")
@patch("axie_utils.TrezorScatter.__init__", return_value=None)
@patch("trezor.trezor_scatter.TrezorScatterRonManager.load_scatter", return_value='foo')
def test_scatter_ron_manager_execute(mocked_load, mocked_scatter_init, mocked_scatter_execute, mocked_client):
    s = TrezorScatterRonManager('from_acc', {"foo": "bar"}, {"from_acc": {"bip_path": "path", "passphrase": ""}}, 1)
    mocked_load.assert_called()
    mocked_client.assert_called()
    s.execute()
    mocked_scatter_init.assert_called_with(
        'ron',  s.from_acc, s.client, s.bip_path, 'foo'
    )
    mocked_scatter_execute.assert_called()
