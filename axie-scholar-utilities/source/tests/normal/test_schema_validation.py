import pytest
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from axie.schemas import payments_schema, payments_percent_schema, transfers_schema, breeding_schema


@pytest.mark.parametrize("json_input, expected_error", [
        ({}, "'Manager' is a required property"),
        ({"Manager": "ronin:123"}, "'Scholars' is a required property"),
        ({"Manager": "ronin:123", "Scholars": [{}]}, "'Name' is a required property"),
        ({"Manager": "ronin:123", "Scholars": [{"Name": "foo"}]},
         "'AccountAddress' is a required property"),
        ({"Manager": "ronin:123", "Scholars": [{
            "Name": "foo", "AccountAddress": "ronin:abc"}]},
         "'ScholarPayoutAddress' is a required property"),
        ({"Manager": "ronin:123", "Scholars": [{
            "Name": "foo",
            "AccountAddress": "ronin:abc",
            "ScholarPayoutAddress": "ronin:def"}]},
         "'ScholarPayout' is a required property"),
        ({"Manager": "ronin:abc", "Scholars": [{
            "Name": "foo",
            "AccountAddress": "ronin:abc",
            "ScholarPayoutAddress": "ronin:def",
            "ScholarPayout": 123}]},
            "'ManagerPayout' is a required property"),
        ({"Manager": "ronin:123", "Scholars": [
          {"Name": "foo", "AccountAddress": "ronin:abc",
           "ScholarPayoutAddress": "ronin:def", "ScholarPayout": 123,
           "ManagerPayout": "345"}]}, "'345' is not of type 'number'"),
        ({"Manager": "ronin:abc", "Scholars": [
          {"Name": "foo", "AccountAddress": "ronin:abc",
           "ScholarPayoutAddress": "ronin:def", "ScholarPayout": "123",
           "ManagerPayout": 345}]}, "'123' is not of type 'number'"),
        ({"Manager": "ronin:rfa", "Scholars": [
          {"Name": "foo", "AccountAddress": "0x:abc",
           "ScholarPayoutAddress": "ronin:def", "ScholarPayout": 123,
           "ManagerPayout": 345}]}, "'0x:abc' does not match '^ronin:'"),
        ({"Manager": "ronin:haga", "Scholars": [
          {"Name": "foo", "AccountAddress": "ronin:abc",
           "ScholarPayoutAddress": "def", "ScholarPayout": 123,
           "ManagerPayout": 345}]}, "'def' does not match '^ronin:'"),
        ({"Manager": "ronin:gha", "Scholars": [
          {"Name": "foo", "AccountAddress": "ronin:abc",
           "ScholarPayoutAddress": "ronin:def", "ScholarPayout": 123,
           "ManagerPayout": 345, "TrainerPayoutAddress": "ronin:xyz"}]},
            "'TrainerPayout' is a dependency of 'TrainerPayoutAddress'"),
        ({"Manager": "ronin:abc", "Scholars": [
          {"Name": "foo", "AccountAddress": "ronin:abc",
           "ScholarPayoutAddress": "ronin:def", "ScholarPayout": 123,
           "ManagerPayout": 345, "TrainerPayout": 678}]},
            "'TrainerPayoutAddress' is a dependency of 'TrainerPayout'"),
        ({"Manager": "ronin:abc", "Scholars": [
          {"Name": "foo", "AccountAddress": "ronin:abc",
           "ScholarPayoutAddress": "ronin:def",
           "ScholarPayout": 123,
           "ManagerPayout": 345, "TrainerPayout": 678,
           "TrainerPayoutAddress": "xyz2"}]},
            "'xyz2' does not match '^ronin:'"),
        ({"Manager": "ronin:abc", "Scholars": [
          {"Name": "foo", "AccountAddress": "ronin:abc",
           "ScholarPayoutAddress": "ronin:def", "ScholarPayout": 123,
           "ManagerPayout": 345, "TrainerPayout": "678",
           "TrainerPayoutAddress": "ronin:xyz2"}]},
            "'678' is not of type 'number'"),
        ({"Manager": "ronin:abc", "Scholars": [
          {"Name": "foo", "AccountAddress": "ronin:abc",
           "ScholarPayoutAddress": "ronin:def", "ScholarPayout": 0,
           "ManagerPayout": 345, "TrainerPayout": 678,
           "TrainerPayoutAddress": "ronin:xyz2"}]},
            "0 is less than the minimum of 1"),
        ({"Manager": "ronin:abc", "Scholars": [
          {"Name": "foo", "AccountAddress": "ronin:abc",
           "ScholarPayoutAddress": "ronin:def", "ScholarPayout": 12,
           "ManagerPayout": 345, "TrainerPayout": 0,
           "TrainerPayoutAddress": "ronin:xyz2"}]},
            "0 is less than the minimum of 1"),
        ({"Manager": "ronin:abc", "Scholars": [
          {"Name": "foo", "AccountAddress": "ronin:abc",
           "ScholarPayoutAddress": "ronin:def", "ScholarPayout": 12,
           "ManagerPayout": 0, "TrainerPayout": 45,
           "TrainerPayoutAddress": "ronin:xyz2"}]},
            "0 is less than the minimum of 1"),
        ({"Manager": "ronin:abc", "Scholars": [
          {"Name": "foo", "AccountAddress": "ronin:abc",
           "ScholarPayoutAddress": "ronin:def", "ScholarPayout": 12,
           "ManagerPayout": 10, "TrainerPayout": 45,
           "TrainerPayoutAddress": "ronin:xyz2"}], "Donations": [{}]},
            "'Name' is a required property"),
        ({"Manager": "ronin:abc", "Scholars": [
          {"Name": "foo", "AccountAddress": "ronin:abc",
           "ScholarPayoutAddress": "ronin:def", "ScholarPayout": 12,
           "ManagerPayout": 10, "TrainerPayout": 45,
           "TrainerPayoutAddress": "ronin:xyz2"}], "Donations": [{
            "Name": "foo"
           }]},
            "'AccountAddress' is a required property"),
        ({"Manager": "ronin:abc", "Scholars": [
          {"Name": "foo", "AccountAddress": "ronin:abc",
           "ScholarPayoutAddress": "ronin:def", "ScholarPayout": 12,
           "ManagerPayout": 10, "TrainerPayout": 45,
           "TrainerPayoutAddress": "ronin:xyz2"}], "Donations": [{
            "Name": "foo", "AccountAddress": "ronin:dono"
           }]},
            "'Percent' is a required property"),
        ({"Manager": "ronin:abc", "Scholars": [
          {"Name": "foo", "AccountAddress": "ronin:abc",
           "ScholarPayoutAddress": "ronin:def", "ScholarPayout": 12,
           "ManagerPayout": 10, "TrainerPayout": 45,
           "TrainerPayoutAddress": "ronin:xyz2"}], "Donations": [{
            "Name": "foo", "AccountAddress": "dono", "Percent": 0.01
           }]},
            "'dono' does not match '^ronin:'"),
        ({"Manager": "ronin:abc", "Scholars": [
          {"Name": "foo", "AccountAddress": "ronin:abc",
           "ScholarPayoutAddress": "ronin:def", "ScholarPayout": 12,
           "ManagerPayout": 10, "TrainerPayout": 45,
           "TrainerPayoutAddress": "ronin:xyz2"}], "Donations": [{
            "Name": "foo", "AccountAddress": "ronin:dono", "Percent": 1.1
           }]},
            "1.1 is greater than the maximum of 1"),
        ({"Manager": "ronin:abc", "Scholars": [
          {"Name": "foo", "AccountAddress": "ronin:abc",
           "ScholarPayoutAddress": "ronin:def", "ScholarPayout": 12,
           "ManagerPayout": 10, "TrainerPayout": 45,
           "TrainerPayoutAddress": "ronin:xyz2"}], "Donations": [{
            "Name": "foo", "AccountAddress": "ronin:dono", "Percent": 0
           }]},
            "0 is less than the minimum of 0.01"),
        ({"Manager": "ronin:abc", "Scholars": [
          {"Name": "foo", "AccountAddress": "ronin:abc",
           "ScholarPayoutAddress": "ronin:def", "ScholarPayout": 12,
           "ManagerPayout": 10, "TrainerPayout": 45,
           "TrainerPayoutAddress": "ronin:xyz2"}], "Donations": [{
            "Name": "foo", "AccountAddress": "ronin:dono", "Percent": -1
           }]},
            "-1 is less than the minimum of 0.01"),
        ({"Manager": "ronin:abc", "Scholars": [
          {"Name": "foo", "AccountAddress": "ronin:abc",
           "ScholarPayoutAddress": "ronin:def", "ScholarPayout": 12,
           "ManagerPayout": 10, "TrainerPayout": 45,
           "TrainerPayoutAddress": "ronin:xyz2"}], "Donations": [{
            "Name": "foo", "AccountAddress": "ronin:dono", "Percent": 0.01
           }], "foo": "bar"},
            "Additional properties are not allowed ('foo' was unexpected)")
        ])
def test_json_validator_payments_schema_error(json_input, expected_error):
    with pytest.raises(ValidationError) as e:
        validate(json_input, payments_schema)
    assert expected_error in str(e.value)


@pytest.mark.parametrize("json_input", [
        ({
            "Manager": "ronin:<Manager address here>",
            "Scholars": [
                {
                    "Name": "Scholar 1",
                    "AccountAddress": "ronin:<account_s1_address>",
                    "ScholarPayoutAddress": "ronin:<scholar_address>",
                    "ScholarPayout": 100,
                    "TrainerPayoutAddress": "ronin:<trainer_address>",
                    "TrainerPayout": 10,
                    "ManagerPayout": 90
                },
                {
                    "Name": "Scholar 2",
                    "AccountAddress": "ronin:<account_s2_address>",
                    "ScholarPayoutAddress": "ronin:<scholar2_address>",
                    "ScholarPayout": 200,
                    "TrainerPayoutAddress": "ronin:<trainer_address>",
                    "TrainerPayout": 14,
                    "ManagerPayout": 190
                }
            ],
            "Donations": [
                {
                    "Name": "Entity 1",
                    "AccountAddress": "ronin:<donation_entity_1_address>",
                    "Percent": 0.01
                },
                {
                    "Name": "Entity 2",
                    "AccountAddress": "ronin:<donation_entity_2_address>",
                    "Percent": 0.01
                }
            ]
        }),
        ({
            "Manager": "ronin:<Manager address here>",
            "Scholars": [
                {
                    "Name": "Scholar 1",
                    "AccountAddress": "ronin:<account_s1_address>",
                    "ScholarPayoutAddress": "ronin:<scholar_address>",
                    "ScholarPayout": 100,
                    "TrainerPayoutAddress": "ronin:<trainer_address>",
                    "TrainerPayout": 10,
                    "ManagerPayout": 90
                },
                {
                    "Name": "Scholar 2",
                    "AccountAddress": "ronin:<account_s2_address>",
                    "ScholarPayoutAddress": "ronin:<scholar2_address>",
                    "ScholarPayout": 200,
                    "TrainerPayoutAddress": "ronin:<trainer_address>",
                    "TrainerPayout": 14,
                    "ManagerPayout": 190
                }]}),
        ({
            "Manager": "ronin:<Manager address here>",
            "Scholars": [
                {
                    "Name": "Scholar 1",
                    "AccountAddress": "ronin:<account_s1_address>",
                    "ScholarPayoutAddress": "ronin:<scholar_address>",
                    "ScholarPayout": 100,
                    "TrainerPayoutAddress": "ronin:<trainer_address>",
                    "TrainerPayout": 10,
                    "ManagerPayout": 90
                },
                {
                    "Name": "Scholar 2",
                    "AccountAddress": "ronin:<account_s2_address>",
                    "ScholarPayoutAddress": "ronin:<scholar2_address>",
                    "ScholarPayout": 200,
                    "ManagerPayout": 190
                }
            ]}),
        ({"Manager": "ronin:abc", "Scholars": []}),
        ({"Manager": "ronin:abc", "Scholars": [], "Donations": []}),
    ])
def test_json_validator_pass_payments_schema_optional_params(json_input):
    validate(json_input, payments_schema)


@pytest.mark.parametrize("json_input, expected_error", [
    ({}, "{} is not of type 'array"),
    ([{}], "'AccountAddress' is a required property"),
    ([{"AccountAddress": "hello", "Transfers": []}],
     "'hello' does not match '^ronin:'"),
    ([{"AccountAddress": "ronin:abc", "Transfers": [{}]}],
     "'AxieId' is a required property"),
    ([{"AccountAddress": "ronin:abc", "Transfers": [
        {"AxieId": "abc"}
    ]}],
       "'ReceiverAddress' is a required property"),
    ([{"AccountAddress": "ronin:abc", "Transfers": [
        {"AxieId": "abc", "ReceiverAddress": "foo"}
    ]}],
       "'abc' is not of type 'number'"),
    ([{"AccountAddress": "ronin:abc", "Transfers": [
        {"AxieId": 123, "ReceiverAddress": "foo"}
    ]}],
       "'foo' does not match '^ronin:'"),
])
def test_json_validator_transfers_schema_error(json_input, expected_error):
    with pytest.raises(ValidationError) as e:
        validate(json_input, transfers_schema)
    assert expected_error in str(e.value)


@pytest.mark.parametrize("json_input", [
    ([{"AccountAddress": "ronin:abc", "Transfers": [
        {"AxieId": 123, "ReceiverAddress": "ronin:foo"}
    ]}]),
    ([{"AccountAddress": "ronin:abc", "Transfers": [
        {"AxieId": 123, "ReceiverAddress": "ronin:foo"}
    ]}, {"AccountAddress": "ronin:abc", "Transfers": [
        {"AxieId": 123, "ReceiverAddress": "ronin:foo"}
    ]}]),
    ([{"AccountAddress": "ronin:abc", "Transfers": [
        {"AxieId": 123, "ReceiverAddress": "ronin:foo"},
        {"AxieId": 123, "ReceiverAddress": "ronin:foo"},
        {"AxieId": 123, "ReceiverAddress": "ronin:foo"}
    ]}, {"AccountAddress": "ronin:abc", "Transfers": [
        {"AxieId": 123, "ReceiverAddress": "ronin:foo"},
        {"AxieId": 123, "ReceiverAddress": "ronin:foo"}
    ]}])
])
def test_json_validator_pass_transfers_schema_optional_params(json_input):
    validate(json_input, transfers_schema)


@pytest.mark.parametrize("json_input, expected_error", [
        ({}, "'Manager' is a required property"),
        ({"Manager": "ronin:123"}, "'Scholars' is a required property"),
        ({"Manager": "ronin:123", "Scholars": [{}]}, "'Name' is a required property"),
        ({"Manager": "ronin:123", "Scholars": [{"Name": "foo"}]},
         "'AccountAddress' is a required property"),
        ({"Manager": "ronin:123", "Scholars": [{
            "Name": "foo", "AccountAddress": "ronin:abc"}]},
         "'ScholarPayoutAddress' is a required property"),
        ({"Manager": "ronin:123", "Scholars": [{
            "Name": "foo",
            "AccountAddress": "ronin:abc",
            "ScholarPayoutAddress": "ronin:def"}]},
         "'ScholarPercent' is a required property"),
        ({"Manager": "ronin:abc", "Scholars": [{
            "Name": "foo",
            "AccountAddress": "ronin:abc",
            "ScholarPayoutAddress": "ronin:def",
            "ScholarPercent": 45,
            "TrainerPayoutAddress": "abc"}]},
            "'TrainerPercent' is a dependency of 'TrainerPayoutAddress'"),
        ({"Manager": "ronin:abc", "Scholars": [{
            "Name": "foo",
            "AccountAddress": "ronin:abc",
            "ScholarPayoutAddress": "ronin:def",
            "ScholarPercent": 45,
            "TrainerPayoutAddress": "abc",
            "TrainerPercent": "1"}]},
            "'abc' does not match '^ronin:'"),
        ({"Manager": "ronin:abc", "Scholars": [{
            "Name": "foo",
            "AccountAddress": "ronin:abc",
            "ScholarPayoutAddress": "ronin:def",
            "ScholarPercent": 45,
            "TrainerPayoutAddress": "ronin:abc",
            "TrainerPercent": "1"}]},
            "'1' is not of type 'number'"),
        ({"Manager": "ronin:abc", "Scholars": [{
            "Name": "foo",
            "AccountAddress": "ronin:abc",
            "ScholarPayoutAddress": "ronin:def",
            "ScholarPercent": 45,
            "TrainerPayoutAddress": "ronin:abc",
            "TrainerPercent": 1,
            "foo": "bar"}]},
            "Additional properties are not allowed ('foo' was unexpected)"),
        ({"Manager": "ronin:abc", "Scholars": [{
            "Name": "foo",
            "AccountAddress": "ronin:abc",
            "ScholarPayoutAddress": "ronin:def",
            "ScholarPercent": 100,
            "TrainerPayoutAddress": "ronin:abc",
            "TrainerPercent": 0}]},
            "100 is greater than the maximum of 99"),
        ({"Manager": "ronin:abc", "Scholars": [{
            "Name": "foo",
            "AccountAddress": "ronin:abc",
            "ScholarPayoutAddress": "ronin:def",
            "ScholarPercent": 10,
            "TrainerPayoutAddress": "ronin:abc",
            "TrainerPercent": 0}]},
            "10 is less than the minimum of 30"),
        ({"Manager": "ronin:abc", "Scholars": [{
            "Name": "foo",
            "AccountAddress": "ronin:abc",
            "ScholarPayoutAddress": "ronin:def",
            "ScholarPercent": 45,
            "TrainerPayoutAddress": "ronin:abc",
            "TrainerPercent": 100}]},
            "100 is greater than the maximum of 98"),
        ({"Manager": "ronin:abc", "Scholars": [{
            "Name": "foo",
            "AccountAddress": "ronin:abc",
            "ScholarPayoutAddress": "ronin:def",
            "ScholarPercent": 45,
            "TrainerPayoutAddress": "ronin:abc",
            "TrainerPercent": 10,
            "ManagerPayout": 10}]},
            "'ManagerPayout' was unexpected"),
])
def test_json_validator_payments_percent_schema_error(json_input, expected_error):
    with pytest.raises(ValidationError) as e:
        validate(json_input, payments_percent_schema)
    assert expected_error in str(e.value)


@pytest.mark.parametrize("json_input", [
    ({
            "Manager": "ronin:<Manager address here>",
            "Scholars": [
                {
                    "Name": "Scholar 1",
                    "AccountAddress": "ronin:<account_s1_address>",
                    "ScholarPayoutAddress": "ronin:<scholar_address>",
                    "ScholarPercent": 41,
                    "TrainerPayoutAddress": "ronin:<trainer_address>",
                    "TrainerPercent": 10
                },
                {
                    "Name": "Scholar 2",
                    "AccountAddress": "ronin:<account_s2_address>",
                    "ScholarPayoutAddress": "ronin:<scholar2_address>",
                    "ScholarPercent": 30,
                    "TrainerPayoutAddress": "ronin:<trainer_address>",
                    "TrainerPercent": 14
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
            ]
        }),
    ({
            "Manager": "ronin:<Manager address here>",
            "Scholars": [
                {
                    "Name": "Scholar 1",
                    "AccountAddress": "ronin:<account_s1_address>",
                    "ScholarPayoutAddress": "ronin:<scholar_address>",
                    "ScholarPercent": 41,
                    "TrainerPayoutAddress": "ronin:<trainer_address>",
                    "TrainerPercent": 0,
                    "TrainerPayout": 100
                },
                {
                    "Name": "Scholar 2",
                    "AccountAddress": "ronin:<account_s2_address>",
                    "ScholarPayoutAddress": "ronin:<scholar2_address>",
                    "ScholarPercent": 40,
                    "TrainerPayoutAddress": "ronin:<trainer_address>",
                    "TrainerPercent": 0
                }
            ]
        }),
    ({
            "Manager": "ronin:<Manager address here>",
            "Scholars": [
                {
                    "Name": "Scholar 1",
                    "AccountAddress": "ronin:<account_s1_address>",
                    "ScholarPayoutAddress": "ronin:<scholar_address>",
                    "ScholarPercent": 50,
                    "ScholarAdjustment": -100
                    "TrainerPayoutAddress": "ronin:<trainer_address>",
                    "TrainerPercent": 10
                },
                {
                    "Name": "Scholar 2",
                    "AccountAddress": "ronin:<account_s2_address>",
                    "ScholarPayoutAddress": "ronin:<scholar2_address>",
                    "ScholarPercent": 55,
                    "ScholarAdjustment": +100
                    "TrainerPayoutAddress": "ronin:<trainer_address>",
                    "TrainerPercent": 14,
                    "TrainerPayout": 100
                }]}),
    ({
            "Manager": "ronin:<Manager address here>",
            "Scholars": [
                {
                    "Name": "Scholar 1",
                    "AccountAddress": "ronin:<account_s1_address>",
                    "ScholarPayoutAddress": "ronin:<scholar_address>",
                    "ScholarPercent": 60,
                    "ScholarPayout": 100,
                    "TrainerPayoutAddress": "ronin:<trainer_address>",
                    "TrainerPercent": 10
                },
                {
                    "Name": "Scholar 2",
                    "AccountAddress": "ronin:<account_s2_address>",
                    "ScholarPayoutAddress": "ronin:<scholar2_address>",
                    "ScholarPercent": 45
                }
            ]}),
    ({
            "Manager": "ronin:<Manager address here>",
            "Scholars": [
                {
                    "Name": "Scholar 1",
                    "AccountAddress": "ronin:<account_s1_address>",
                    "ScholarPayoutAddress": "ronin:<scholar_address>",
                    "ScholarPercent": 60,
                    "ScholarPayout": 100,
                    "TrainerPayoutAddress": "ronin:<trainer_address>",
                    "TrainerPercent": 10,
                    "TrainerPayout": 100,
                },
                {
                    "Name": "Scholar 2",
                    "AccountAddress": "ronin:<account_s2_address>",
                    "ScholarPayoutAddress": "ronin:<scholar2_address>",
                    "ScholarPercent": 45
                }
            ]}),
    ({"Manager": "ronin:abc", "Scholars": []}),
    ({"Manager": "ronin:abc", "Scholars": [], "Donations": []}),
])
def test_json_validator_pass_payments_percent_schema_optional_params(json_input):
    validate(json_input, payments_percent_schema)


@pytest.mark.parametrize("json_input, expected_error", [
        ([{}], "'AccountAddress' is a required property"),
        ([{"AccountAddress": "foo"}], "'Sire' is a required property"),
        ([{"AccountAddress": "foo", "Sire": "foo"}], "'Matron' is a required property"),
        ([{"AccountAddress": "foo", "Sire": "foo", "Matron": "foo"}], "'foo' does not match '^ronin:'"),
        ([{"AccountAddress": "ronin:foo", "Sire": "foo", "Matron": "foo"}], "'foo' is not of type 'number'"),
        ([{"AccountAddress": "ronin:foo", "Sire": 0, "Matron": "foo"}], "'foo' is not of type 'number'"),
        ([{"AccountAddress": "ronin:foo", "Sire": 0, "Matron": "foo"}], "'foo' is not of type 'number'"),
        ([{"AccountAddress": "ronin:foo", "Sire": "0", "Matron": "foo"}], "'0' is not of type 'number'")
])
def test_json_validator_breeding_schema_error(json_input, expected_error):
    with pytest.raises(ValidationError) as e:
        validate(json_input, breeding_schema)
    assert expected_error in str(e.value)
