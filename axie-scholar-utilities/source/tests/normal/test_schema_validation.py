import pytest
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from axie.schemas import legacy_payments_schema, payments_schema, transfers_schema, breeding_schema


@pytest.mark.parametrize("json_input, expected_error", [
        ({}, "'scholars' is a required property"),
        ({"scholars": "foo"}, "'foo' is not of type 'array'"),
        ({"scholars": [{}]}, "'name' is a required property"),
        ({"scholars": [{"name": "foo"}]}, "'ronin' is a required property"),
        ({"scholars": [{"name": "foo", "ronin": "foo"}]}, "'splits' is a required property"),
        ({"scholars": [{"name": "foo", "ronin": "foo", "splits": "bar"}]}, "'foo' does not match '^ronin:"),
        ({"scholars": [{"name": "foo", "ronin": "ronin:foo", "splits": "bar"}]}, "'bar' is not of type 'array'"),
        ({"scholars": [{"name": "foo", "ronin": "ronin:foo", "splits": [{}]}]}, "'persona' is a required property"),
        ({"scholars": [{"name": "foo", "ronin": "ronin:foo", "splits": [
            {"persona": "foo"}]}]}, "'ronin' is a required property"),
        ({"scholars": [{"name": "foo", "ronin": "ronin:foo", "splits": [
            {"persona": "foo", "ronin": "ronin:foo"}]}]}, "'percentage' is a required property"),
        ({"scholars": [{"name": "foo", "ronin": "ronin:foo", "splits": [
            {"persona": "foo", "ronin": "ronin:foo", "percentage": "foo"}]}]}, "'foo' is not of type 'number'"),
        ({"scholars": [{"name": "foo", "ronin": "ronin:foo", "splits": [
            {"persona": "foo", "ronin": "foo", "percentage": 10}]}]}, "'foo' does not match '^ronin:"),
        ({"scholars": [{"name": "foo", "ronin": "ronin:foo", "splits": [
            {"persona": "foo", "ronin": "ronin:foo", "percentage": 0}]}]}, "0 is less than the minimum of 1"),
        ({"scholars": [{"name": "foo", "ronin": "ronin:foo", "splits": [
            {"persona": "foo", "ronin": "ronin:foo", "percentage": 101}]}]}, "101 is greater than the maximum of 100"),
        ])
def test_json_validator_payments_schema_error(json_input, expected_error):
    with pytest.raises(ValidationError) as e:
        validate(json_input, payments_schema)
    assert expected_error in str(e.value)


@pytest.mark.parametrize("json_input", [
        ({"scholars": []}),
        ({"scholars": [{"name": "foo", "ronin": "ronin:foo", "splits": []}]}),
        ({"scholars": [{"name": "foo", "ronin": "ronin:foo", "splits": [
         {"persona": "foo", "ronin": "ronin:foo", "percentage": 10}]}]}),
        ({"scholars": [{"name": "foo", "ronin": "ronin:foo", "splits": [
         {"persona": "foo", "ronin": "ronin:foo", "percentage": 10}]}],
          "donations": []}),
        ({"scholars": [{"name": "foo", "ronin": "ronin:foo", "splits": [
         {"persona": "foo", "ronin": "ronin:foo", "percentage": 10}]}],
         "donations": [{"name": "bar", "percentage": 1, "ronin": "ronin:blah"}]}),
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
def test_json_validator_legacy_payments_schema_error(json_input, expected_error):
    with pytest.raises(ValidationError) as e:
        validate(json_input, legacy_payments_schema)
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
                    "TrainerPayoutAddress": "ronin:<trainer_address>",
                    "TrainerPercent": 10
                },
                {
                    "Name": "Scholar 2",
                    "AccountAddress": "ronin:<account_s2_address>",
                    "ScholarPayoutAddress": "ronin:<scholar2_address>",
                    "ScholarPercent": 55,
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
def test_json_validator_pass_legacy_payments_schema_optional_params(json_input):
    validate(json_input, legacy_payments_schema)


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
