"""
REPO Finance Manager - Core Business Logic

This module contains the core financial management functionality for REPO group finances,
including player management, transaction recording, and balance calculations.
"""

import math


def round_money_down(amount):
    """
    Helper function to round money down to nearest thousand for REPO currency system.

    REPO only allows spending in thousands (1k, 2k, etc.), so this function
    rounds any amount down to the nearest thousand.

    Parameters
    ----------
    amount : float
        The amount to be rounded down.

    Returns
    -------
    int
        The amount rounded down to nearest thousand.

    Raises
    ------
    ValueError
        If amount is negative.
    """
    if amount < 0:
        raise ValueError(f"Amount cannot be negative: {amount}")
    return int(math.floor(amount / 1000) * 1000)


class RepoFinanceManager:
    """
    Core finance management class for REPO group transactions.

    This class handles all financial operations including player management,
    transaction recording, balance calculations, and group fund management
    for a REPO gaming group.
    """

    def __init__(self):
        """
        Initialize the finance manager with empty player data and group fund.

        Sets up the initial state with no players, starting at round 1,
        an empty transaction history, and zero group fund.
        """
        self.players = {}
        self.round_number = 1
        self.transaction_history = []
        self.group_fund = 0.0  # Puffer money for the group
        self.total_money_at_round_start = 0.0  # Track money at start of each round
        self.kill_bonuses_this_round = 0.0

    def add_player(self, player_name):
        """
        Add a new player to the group.

        Parameters
        ----------
        player_name : str
            Name of the player to add. Must be non-empty and unique.

        Returns
        -------
        bool
            True if player was successfully added, False if player already exists
            or name is invalid.
        """
        if player_name and player_name not in self.players:
            self.players[player_name] = 0.0
            return True
        return False

    def remove_player(self, player_name):
        """
        Remove a player from the group and redistribute their money.

        When a player is removed mid-round, their remaining money is split
        between remaining players and the group fund to prevent money loss.

        Parameters
        ----------
        player_name : str
            Name of the player to remove.

        Returns
        -------
        bool
            True if player was successfully removed, False if player doesn't exist.
        """
        if player_name not in self.players:
            return False

        player_balance = self.players[player_name]

        # Remove the player
        del self.players[player_name]

        # Redistribute their money if they had any
        if player_balance > 0 and len(self.players) > 0:
            # Split money among remaining players first, remainder to group fund
            per_player = round_money_down(player_balance / len(self.players))

            # Give rounded amount to each remaining player
            for player in self.players:
                self.players[player] += per_player

            # Calculate remainder and add ALL of it to group fund
            total_to_players = per_player * len(self.players)
            remainder = player_balance - total_to_players
            self.group_fund += remainder

            # Record the redistribution transaction
            self.transaction_history.append(
                {
                    "round": self.round_number,
                    "type": "player_removal_redistribution",
                    "description": f"Redistributed {player_name}'s money after removal",
                    "removed_player": player_name,
                    "original_balance": player_balance,
                    "per_player": per_player,
                    "remainder_to_fund": remainder,
                    "players": list(self.players.keys()),
                }
            )

        return True

    def start_new_round(self):
        """
        Start a new round by incrementing the round counter and saving current total.

        This should be called at the beginning of each new REPO mission/round
        to properly track which transactions belong to which round and enable
        automatic calculation of new earnings.
        """
        self.round_number += 1
        # Save total money at start of new round for automatic calculation
        self.total_money_at_round_start = self.get_total_money()
        self.kill_bonuses_this_round = 0.0

    def get_total_money(self):
        """
        Get the total money across all players and group fund.

        Returns
        -------
        float
            Total money in the system (all players + group fund).
        """
        return sum(self.players.values()) + self.group_fund

    def calculate_new_earnings(self, current_total_shown_in_game):
        """
        Calculate how much new money was earned this round.

        Takes the total money shown in REPO and subtracts what we had at
        round start to find the actual new earnings to split.

        Parameters
        ----------
        current_total_shown_in_game : float
            The total money amount currently shown in REPO.

        Returns
        -------
        float
            The new money earned this round that should be split.
        """
        return current_total_shown_in_game - self.total_money_at_round_start

    def add_shared_earnings_auto(
        self, current_total_shown_in_game, description="Round earnings"
    ):
        if len(self.players) == 0:
            return False, 0, 0

        total_new_money = current_total_shown_in_game - self.total_money_at_round_start
        shared_earnings = total_new_money - self.kill_bonuses_this_round

        if total_new_money <= 0:
            return False, total_new_money, shared_earnings
        if shared_earnings <= 0:
            return False, total_new_money, shared_earnings

        per_player_exact = shared_earnings / len(self.players)
        per_player_rounded = round_money_down(per_player_exact)

        for player in self.players:
            self.players[player] += per_player_rounded

        total_distributed = per_player_rounded * len(self.players)
        remainder = shared_earnings - total_distributed
        self.group_fund += remainder

        self.transaction_history.append(
            {
                "round": self.round_number,
                "type": "shared_earnings_auto",
                "description": description,
                "game_total": current_total_shown_in_game,
                "previous_total": self.total_money_at_round_start,
                "total_new_money": total_new_money,
                "kill_bonuses_this_round": self.kill_bonuses_this_round,
                "shared_earnings": shared_earnings,
                "per_player": per_player_rounded,
                "remainder_to_fund": remainder,
                "players": list(self.players.keys()),
            }
        )

        return True, total_new_money, shared_earnings

    def add_kill_bonus(
        self, amount, players_involved, description="Kill bonus", use_group_fund=False
    ):
        """
        Add kill bonus to specific player(s) who participated in a monster kill.

        When players kill monsters in REPO, they receive monster orbs that have
        monetary value. This bonus is split among players who participated.
        Can optionally use group fund to supplement small individual amounts.

        Parameters
        ----------
        amount : float
            Total kill bonus amount to be distributed.
        players_involved : list of str
            List of player names who participated in the kill.
        description : str, optional
            Description of the kill/monster (default: "Kill bonus").
        use_group_fund : bool, optional
            Whether to use group fund to supplement small amounts (default: False).

        Returns
        -------
        bool
            True if bonus was successfully added, False if no players specified
            or invalid player names provided.
        """
        if not players_involved:
            return False

        per_player_exact = amount / len(players_involved)
        per_player_rounded = round_money_down(per_player_exact)

        # If individual amount is too small and group fund available, supplement
        group_fund_used = 0
        if (
            use_group_fund
            and per_player_rounded == 0
            and self.group_fund >= 1000 * len(players_involved)
        ):
            per_player_rounded = 1000  # Give 1k to each player
            group_fund_used = 1000 * len(players_involved)
            self.group_fund -= group_fund_used

        # Add amount to each participating player
        for player in players_involved:
            if player in self.players:
                self.players[player] += per_player_rounded

        # Add remainder to group fund if not using group fund
        if not use_group_fund:
            total_distributed = per_player_rounded * len(players_involved)
            remainder = amount - total_distributed
            self.group_fund += remainder
        else:
            remainder = 0

        self.kill_bonuses_this_round += amount
        self.transaction_history.append(
            {
                "round": self.round_number,
                "type": "kill_bonus",
                "description": description,
                "total_amount": amount,
                "per_player": per_player_rounded,
                "remainder_to_fund": remainder,
                "group_fund_used": group_fund_used,
                "players": players_involved,
            }
        )
        return True

    def record_spending(self, player_name, amount, description="Purchase"):
        """
        Record money spent by a specific player on equipment/items.

        When a player buys equipment in REPO (weapons, health packs, etc.),
        this function deducts the cost from their balance.

        Parameters
        ----------
        player_name : str
            Name of the player who made the purchase.
        amount : float
            Amount spent on the purchase.
        description : str, optional
            Description of what was purchased (default: "Purchase").

        Returns
        -------
        bool
            True if spending was successfully recorded, False if player doesn't exist.
        """
        if player_name not in self.players:
            return False

        self.players[player_name] -= amount

        self.transaction_history.append(
            {
                "round": self.round_number,
                "type": "spending",
                "description": description,
                "amount": amount,
                "player": player_name,
            }
        )
        return True

    def add_to_group_fund(self, amount, description="Group fund addition"):
        """
        Add money directly to the group fund.

        Parameters
        ----------
        amount : float
            Amount to add to the group fund.
        description : str, optional
            Description of the addition (default: "Group fund addition").
        """
        self.group_fund += amount

        self.transaction_history.append(
            {
                "round": self.round_number,
                "type": "group_fund_addition",
                "description": description,
                "amount": amount,
            }
        )

    def use_group_fund(self, amount, description="Group fund usage"):
        """
        Use money from the group fund.

        Parameters
        ----------
        amount : float
            Amount to use from the group fund.
        description : str, optional
            Description of the usage (default: "Group fund usage").

        Returns
        -------
        bool
            True if successful, False if insufficient funds.
        """
        if self.group_fund >= amount:
            self.group_fund -= amount

            self.transaction_history.append(
                {
                    "round": self.round_number,
                    "type": "group_fund_usage",
                    "description": description,
                    "amount": amount,
                }
            )
            return True
        return False

    def get_group_fund_rounded(self):
        """
        Get the group fund balance rounded down to nearest thousand.

        Returns
        -------
        int
            Group fund balance rounded down to nearest thousand.
        """
        return round_money_down(self.group_fund)

    def undo_last_transaction(self):
        """
        Undo the most recent transaction and reverse its effects on player balances and group fund.

        This is useful for correcting mistakes made during data entry.
        The transaction is completely removed from history and balances are restored.

        Returns
        -------
        bool
            True if transaction was successfully undone, False if no transactions exist.
        """
        if not self.transaction_history:
            return False

        last_transaction = self.transaction_history.pop()

        if last_transaction["type"] == "shared_earnings":
            for player in last_transaction["players"]:
                if player in self.players:
                    self.players[player] -= last_transaction["per_player"]
            # Reverse group fund addition
            if "remainder_to_fund" in last_transaction:
                self.group_fund -= last_transaction["remainder_to_fund"]

        elif last_transaction["type"] == "shared_earnings_auto":
            for player in last_transaction["players"]:
                if player in self.players:
                    self.players[player] -= last_transaction["per_player"]
            # Reverse group fund addition
            if "remainder_to_fund" in last_transaction:
                self.group_fund -= last_transaction["remainder_to_fund"]

        elif last_transaction["type"] == "player_removal_redistribution":
            for player in last_transaction["players"]:
                if player in self.players:
                    self.players[player] -= last_transaction["per_player"]
            # Reverse group fund changes
            if "remainder_to_fund" in last_transaction:
                self.group_fund -= last_transaction["remainder_to_fund"]

        elif last_transaction["type"] == "kill_bonus":
            for player in last_transaction["players"]:
                if player in self.players:
                    self.players[player] -= last_transaction["per_player"]
            # Reverse group fund changes
            if "remainder_to_fund" in last_transaction:
                self.group_fund -= last_transaction["remainder_to_fund"]
            if "group_fund_used" in last_transaction:
                self.group_fund += last_transaction["group_fund_used"]
            self.kill_bonuses_this_round = max(0, self.kill_bonuses_this_round - last_transaction['total_amount'])

        elif last_transaction["type"] == "spending":
            if last_transaction["player"] in self.players:
                self.players[last_transaction["player"]] += last_transaction["amount"]

        elif last_transaction["type"] == "group_fund_addition":
            self.group_fund -= last_transaction["amount"]

        elif last_transaction["type"] == "group_fund_usage":
            self.group_fund += last_transaction["amount"]

        return True

    def delete_transaction(self, transaction_index):
        """
        Delete a specific transaction by index and reverse its effects.

        Allows removal of any transaction from the history, not just the most recent.
        Useful for correcting mistakes made several transactions ago.

        Parameters
        ----------
        transaction_index : int
            Index of the transaction to delete in the transaction_history list.

        Returns
        -------
        bool
            True if transaction was successfully deleted, False if index is invalid.
        """
        if transaction_index < 0 or transaction_index >= len(self.transaction_history):
            return False

        transaction = self.transaction_history[transaction_index]

        if transaction["type"] == "shared_earnings":
            for player in transaction["players"]:
                if player in self.players:
                    self.players[player] -= transaction["per_player"]
            # Reverse group fund addition
            if "remainder_to_fund" in transaction:
                self.group_fund -= transaction["remainder_to_fund"]

        elif transaction["type"] == "shared_earnings_auto":
            for player in transaction["players"]:
                if player in self.players:
                    self.players[player] -= transaction["per_player"]
            # Reverse group fund addition
            if "remainder_to_fund" in transaction:
                self.group_fund -= transaction["remainder_to_fund"]

        elif transaction["type"] == "player_removal_redistribution":
            # Reverse the money redistribution
            for player in transaction["players"]:
                if player in self.players:
                    self.players[player] -= transaction["per_player"]
            # Reverse group fund changes
            if "remainder_to_fund" in transaction:
                self.group_fund -= transaction["remainder_to_fund"]

        elif transaction["type"] == "kill_bonus":
            for player in transaction["players"]:
                if player in self.players:
                    self.players[player] -= transaction["per_player"]
            # Reverse group fund changes
            if "remainder_to_fund" in transaction:
                self.group_fund -= transaction["remainder_to_fund"]
            if "group_fund_used" in transaction:
                self.group_fund += transaction["group_fund_used"]
            self.kill_bonuses_this_round = max(0, self.kill_bonuses_this_round - transaction['total_amount'])

        elif transaction["type"] == "spending":
            if transaction["player"] in self.players:
                self.players[transaction["player"]] += transaction["amount"]

        elif transaction["type"] == "group_fund_addition":
            self.group_fund -= transaction["amount"]

        elif transaction["type"] == "group_fund_usage":
            self.group_fund += transaction["amount"]

        self.transaction_history.pop(transaction_index)
        return True

    def get_rounded_balance(self, player_name):
        """
        Get a player's balance rounded down to nearest thousand (REPO currency format).

        REPO only allows spending in thousands, so this returns the usable balance
        that can actually be spent in-game.

        Parameters
        ----------
        player_name : str
            Name of the player whose balance to retrieve.

        Returns
        -------
        int
            Player's balance rounded down to nearest thousand, or 0 if player doesn't exist.
        """
        if player_name not in self.players:
            return 0
        return round_money_down(self.players[player_name])

    def get_all_rounded_balances(self):
        """
        Get all players' balances rounded down to nearest thousand.

        Returns a dictionary of all player balances in REPO-compatible format
        (rounded down to nearest thousand).

        Returns
        -------
        dict
            Dictionary mapping player names to their rounded balances.
        """
        return {
            player: round_money_down(balance)
            for player, balance in self.players.items()
        }

    def reset_all(self):
        """
        Reset all data to initial state.

        Clears all players, resets round number to 1, clears transaction history,
        and resets group fund to zero. This is useful when starting a new gaming
        session or testing.
        """
        self.players = {}
        self.round_number = 1
        self.transaction_history = []
        self.group_fund = 0.0
        self.total_money_at_round_start = 0.0
        self.kill_bonuses_this_round = 0.0
