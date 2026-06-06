import pytest
from repo_finance_core import RepoFinanceManager, round_money_down


@pytest.fixture
def manager_with_players():
    """Manager with Simon and Jazkub already added."""
    m = RepoFinanceManager()
    m.add_player("Simon")
    m.add_player("Jazkub")
    return m


def test_round_money_down_below_thousand():
    assert round_money_down(999) == 0


def test_round_money_down_just_above_thousand():
    assert round_money_down(1001) == 1000


def test_round_money_down_just_below_next_thousand():
    assert round_money_down(1999) == 1000


def test_round_money_down_zero():
    assert round_money_down(0) == 0


@pytest.mark.parametrize("amount", [-1, -999, -1001])
def test_round_money_down_negative_values(amount):
    with pytest.raises(ValueError):
        round_money_down(amount)


def test_round_money_down_basic():
    assert round_money_down(1721) == 1000


def test_round_money_down_exact():
    assert round_money_down(2000) == 2000


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

    # Method return values are part of the public contract
    assert success is True
    assert total_new == 30000
    assert shared == 30000

    # Final balances should reflect the shared earnings
    assert m.players["Simon"] == 15000
    assert m.players["Jazkub"] == 15000


def test_shared_earnings_auto_no_players():
    """Calling add_shared_earnings_auto with no players should fail and not allocate money."""
    m = RepoFinanceManager()

    success, total_new, shared = m.add_shared_earnings_auto(30000)

    assert success is False
    assert total_new == 0
    assert shared == 0
    assert m.players == {}


def test_shared_earnings_auto_zero_total_game_money():
    """Zero total_game_money should be treated as invalid input."""
    m = RepoFinanceManager()
    m.add_player("Simon")

    success, total_new, shared = m.add_shared_earnings_auto(0)

    assert success is False
    assert total_new == 0
    assert shared == 0
    # Balance should remain unchanged
    assert m.players["Simon"] == 0


def test_shared_earnings_auto_negative_total_game_money():
    """Negative total_game_money should be treated as invalid input."""
    m = RepoFinanceManager()
    m.add_player("Simon")

    success, total_new, shared = m.add_shared_earnings_auto(-1000)

    assert success is False
    assert total_new == -1000
    assert shared == 0
    # Balance should remain unchanged
    assert m.players["Simon"] == 0


def test_shared_earnings_auto_total_less_than_round_start():
    """
    total_game_money lower than total_money_at_round_start should be rejected.

    This simulates a case where the game has lost money compared to the start of the round,
    which should not produce shared earnings.
    """
    m = RepoFinanceManager()
    m.add_player("Simon")

    # Give Simon some money and start a new round so that total_money_at_round_start is > 0
    m.players["Simon"] = 20000
    m.start_new_round()
    assert m.total_money_at_round_start == 20000

    # Now report a lower total_game_money than we had at round start
    success, total_new, shared = m.add_shared_earnings_auto(15000)

    assert success is False
    assert total_new == -5000
    assert shared == 0
    # Balances should not be adjusted on failure
    assert m.players["Simon"] == 20000


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


def test_undo_kill_bonus_decrements_counter():
    m = RepoFinanceManager()
    m.add_player("Simon")
    m.add_kill_bonus(2000, ["Simon"])
    assert m.kill_bonuses_this_round == 2000
    assert m.players["Simon"] == 2000
    m.undo_last_transaction()
    assert m.kill_bonuses_this_round == 0
    assert m.players["Simon"] == 0


def test_delete_non_last_kill_bonus_decrements_counter():
    m = RepoFinanceManager()
    m.add_player("Simon")
    m.add_player("Jazkub")
    m.add_kill_bonus(2000, ["Simon"])   # index 0
    m.add_kill_bonus(3000, ["Jazkub"]) # index 1
    assert m.kill_bonuses_this_round == 5000
    m.delete_transaction(0)
    assert m.kill_bonuses_this_round == 3000
    assert m.players["Simon"] == 0
    assert m.players["Jazkub"] == 3000


def test_reset_all(manager_with_players):
    manager_with_players.add_shared_earnings_auto(10000)
    manager_with_players.add_kill_bonus(2000, ["Simon"])
    manager_with_players.start_new_round()
    manager_with_players.reset_all()
    assert manager_with_players.players == {}
    assert manager_with_players.group_fund == 0.0
    assert manager_with_players.round_number == 1
    assert manager_with_players.transaction_history == []
    assert manager_with_players.kill_bonuses_this_round == 0.0
    assert manager_with_players.total_money_at_round_start == 0.0
