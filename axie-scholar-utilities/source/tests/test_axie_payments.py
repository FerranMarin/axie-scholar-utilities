import os

import pytest
from mock import patch, call

from axie import AxiePaymentsManager

@patch("axie.AxiePaymentsManager.load_json")
def test_payments_manager_init(mocked_load_json):
    payments_file = os.path.abspath("./test_data/sample_payments_file.json")
    secrets_file = os.path.abspath("./test_data/sample_secrets_file.json")
    AxiePaymentsManager(payments_file, secrets_file)
    mocked_load_json.assert_has_calls(
        calls=[call(payments_file), call(secrets_file)]
    )

def test_payments_manager_load_json_safeguard():
    with pytest.raises(Exception) as e:
        AxiePaymentsManager.load_json("non_existent.json")
    assert str(e.value) == ("File path non_existent.json does not exist. "
                            "Please provide a correct one")

def test_payments_manager_load_json(tmpdir):
    f = tmpdir.join("test.json")
    f.write('{"foo": "bar"}')
    loaded = AxiePaymentsManager.load_json(f)
    assert loaded == {"foo": "bar"}

def test_payments_manager_load_json_not_json(tmpdir):
    f = tmpdir.join("test.txt")
    f.write("foo bar")
    with pytest.raises(Exception) as e:
        AxiePaymentsManager.load_json(f)
    assert str(e.value) == f"File in path {f} is not a correctly encoded JSON."

def test_payments_manager_verify_input_success(tmpdir):
    p_file = tmpdir.join("p.json")
    scholar_acc = 'ronin:<account_s1_address>'+ "".join([str(x) for x in range(10)]*4)
    scholar_private_acc = '0x<account_s1_private_address>012345'+ "".join([str(x) for x in range(10)]*3)
    p_file.write(('{"Manager":"ronin:<Manager address here>","Scholars":'
                  '[{"Name":"Scholar 1","AccountAddress":"'+scholar_acc+'",'
                  '"ScholarPayoutAddress":"ronin:<scholar_address>","ScholarPayout":10,'
                  '"TrainerPayoutAddress":"ronin:<trainer_address>","TrainerPayout":1,'
                  '"ManagerPayout":9}],"Donations":[{"Name":"Entity 1",'
                  '"AccountAddress": "ronin:<donation_entity_1_address>","Percent":0.01}]}'))
    s_file = tmpdir.join("s.json")
    s_file.write('{"'+scholar_acc+'":"'+scholar_private_acc+'"}')
    print(scholar_private_acc)
    axp = AxiePaymentsManager(p_file, s_file)
    axp.verify_inputs()
    assert axp.manager_acc == "ronin:<Manager address here>"
    assert axp.scholar_accounts == [
        {"Name":"Scholar 1",
         "AccountAddress": scholar_acc,
         "ScholarPayoutAddress":"ronin:<scholar_address>",
         "ScholarPayout":10,
         "TrainerPayoutAddress":"ronin:<trainer_address>",
         "TrainerPayout":1,
         "ManagerPayout":9}]
    assert axp.donations == [
        {"Name":"Entity 1",
         "AccountAddress": "ronin:<donation_entity_1_address>",
         "Percent":0.01}]

