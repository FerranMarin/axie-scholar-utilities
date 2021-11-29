import pytest

from axie.payments import PaymentsSummary


def test_summary_is_singleton():
    s = PaymentsSummary()
    s_copy = PaymentsSummary()
    s_copy.increase_payout(1, "ronin:1", "manager")
    assert s == s_copy
    assert s.manager == s_copy.manager
    assert s.manager['slp'] == 1
    assert str(s) == "Paid 1 managers, 1 SLP.\n"


@pytest.mark.parametrize("payouts, expected_output", [
    ([[10, "ronin:1", "manager"]], "Paid 1 managers, 10 SLP.\n"),
    ([
        [10, "ronin:1", "manager"],
        [10, "ronin:1", "manager"]
    ], "Paid 1 managers, 20 SLP.\n"),
    ([
        [10, "ronin:1", "manager"],
        [10, "ronin:2", "manager"]
    ], "Paid 2 managers, 20 SLP.\n"),
    ([
        [10, "ronin:1", "scholar"],
        [10, "ronin:2", "manager"]
    ], "Paid 1 managers, 10 SLP.\nPaid 1 scholars, 10 SLP.\n"),
    ([
        [10, "ronin:1", "scholar"],
        [10, "ronin:2", "manager"],
        [10, "ronin:3", "donation"]
    ], "Paid 1 managers, 10 SLP.\nPaid 1 scholars, 10 SLP.\n"
       "Donated to 1 organisations, 10 SLP.\n"),
    ([
        [10, "ronin:1", "scholar"],
        [10, "ronin:2", "manager"],
        [10, "ronin:3", "donation"],
        [10, "ronin:3", "trainer"]
    ], "Paid 1 managers, 10 SLP.\nPaid 1 scholars, 10 SLP.\n"
       "Paid 1 trainers, 10 SLP.\nDonated to 1 organisations, 10 SLP.\n"),
    ([
        [10, "ronin:1", "scholar"],
        [10, "ronin:2", "scholar"],
        [10, "ronin:3", "scholar"],
        [10, "ronin:4", "scholar"],
        [10, "ronin:2", "manager"],
        [10, "ronin:2", "manager"],
        [10, "ronin:3", "manager"],
        [10, "ronin:3", "donation"],
        [10, "ronin:3", "donation"],
        [10, "ronin:3", "donation"],
        [10, "ronin:3", "trainer"],
        [10, "ronin:2", "trainer"]
    ], "Paid 2 managers, 30 SLP.\nPaid 4 scholars, 40 SLP.\n"
       "Paid 2 trainers, 20 SLP.\nDonated to 1 organisations, 30 SLP.\n")
])
def test_summary_correct_output(payouts, expected_output):
    PaymentsSummary().clear()
    s = PaymentsSummary()
    for p in payouts:
        s.increase_payout(p[0], p[1], p[2])
    assert str(s) == expected_output
