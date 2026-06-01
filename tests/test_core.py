import pytest
from repo_finance_core import RepoFinanceManager, round_money_down


def test_round_money_down_basic():
    assert round_money_down(1721) == 1000


def test_round_money_down_exact():
    assert round_money_down(2000) == 2000


def test_round_money_down_below_thousand():
    assert round_money_down(999) == 0


def test_round_money_down_zero():
    assert round_money_down(0) == 0


def test_add_player():
    m = RepoFinanceManager()
    assert m.add_player("Simon") == True
    assert "Simon" in m.players


def test_add_duplicate_player():
    m = RepoFinanceManager()
    m.add_player("Simon")
    assert m.add_player("Simon") == False


def test_remove_player():
    m = RepoFinanceManager()
    m.add_player("Simon")
    assert m.remove_player("Simon") == True
    assert "Simon" not in m.players


def test_remove_nonexistent_player():
    m = RepoFinanceManager()
    assert m.remove_player("Ghost") == False


def test_start_new_round():
    m = RepoFinanceManager()
    m.add_player("Simon")
    m.players["Simon"] = 5000
    m.start_new_round()
    assert m.round_number == 2
    assert m.kill_bonuses_this_round == 0.0
    assert m.total_money_at_round_start == 5000


def test_shared_earnings_auto_basic():
    """30k split between 2 players = 15k each"""
    m = RepoFinanceManager()
    m.add_player("Simon")
    m.add_player("Jazkub")
    success, total_new, shared = m.add_shared_earnings_auto(30000)
    assert success == True
    assert m.players["Simon"] == 15000
    assert m.players["Jazkub"] == 15000


def test_shared_earnings_remainder_to_fund():
    """5k split between 4 players = 1k each, 1k to fund"""
    m = RepoFinanceManager()
    for p in ["A", "B", "C", "D"]:
        m.add_player(p)
    m.add_shared_earnings_auto(5000)
    assert m.players["A"] == 1000
    assert m.group_fund == 1000


def test_shared_earnings_subtracts_kill_bonus():
    """Kill bonus is excluded from shared earnings calculation"""
    m = RepoFinanceManager()
    m.add_player("Simon")
    m.add_player("Jazkub")
    # Round 1: earn 30k
    m.add_shared_earnings_auto(30000)
    m.start_new_round()
    # Round 2: Simon gets 2k kill bonus, game shows 42k
    # New money = 42k - 30k = 12k, minus 2k kill bonus = 10k to split
    m.add_kill_bonus(2000, ["Simon"])
    success, total_new, shared = m.add_shared_earnings_auto(42000)
    assert success == True
    assert shared == 10000
    assert m.players["Simon"] == 15000 + 2000 + 5000  # previous + kill + share
    assert m.players["Jazkub"] == 15000 + 5000  # previous + share


def test_kill_bonus_single_player():
    m = RepoFinanceManager()
    m.add_player("Simon")
    m.add_kill_bonus(3000, ["Simon"])
    assert m.players["Simon"] == 3000


def test_kill_bonus_split_between_two():
    m = RepoFinanceManager()
    m.add_player("Simon")
    m.add_player("Jazkub")
    m.add_kill_bonus(3000, ["Simon", "Jazkub"])
    assert m.players["Simon"] == 1000
    assert m.players["Jazkub"] == 1000
    assert m.group_fund == 1000  # remainder


def test_kill_bonus_tracked_for_round():
    m = RepoFinanceManager()
    m.add_player("Simon")
    m.add_kill_bonus(2000, ["Simon"])
    assert m.kill_bonuses_this_round == 2000


def test_remove_player_redistributes_money():
    """Removed player's money goes to remaining players, remainder to fund"""
    m = RepoFinanceManager()
    m.add_player("Simon")
    m.add_player("Jazkub")
    m.add_player("Flowo")
    m.players["Simon"] = 15000
    m.remove_player("Simon")
    assert m.players["Jazkub"] == 7000
    assert m.players["Flowo"] == 7000
    assert m.group_fund == 1000  # remainder


def test_undo_last_transaction():
    m = RepoFinanceManager()
    m.add_player("Simon")
    m.add_shared_earnings_auto(10000)
    assert m.players["Simon"] == 10000
    m.undo_last_transaction()
    assert m.players["Simon"] == 0


def test_undo_empty_history():
    m = RepoFinanceManager()
    assert m.undo_last_transaction() == False


def test_reset_all():
    m = RepoFinanceManager()
    m.add_player("Simon")
    m.players["Simon"] = 5000
    m.group_fund = 1000
    m.round_number = 3
    m.reset_all()
    assert m.players == {}
    assert m.group_fund == 0.0
    assert m.round_number == 1
    assert m.transaction_history == []
