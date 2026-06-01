"""
REPO Finance Manager - File Operations Handler

This module handles all file operations for the REPO Finance Manager,
including saving/loading sessions and exporting summaries.
"""

import json
import os
from datetime import datetime
from tkinter import filedialog, messagebox


class RepoFileManager:
    """
    Handles all file operations for the REPO Finance Manager.

    This class provides methods for saving/loading session data and
    exporting human-readable summaries, with proper error handling
    and user feedback through dialog boxes.
    """

    def __init__(self, manager):
        """
        Initialize the file manager with a reference to the finance manager.

        Parameters
        ----------
        manager : RepoFinanceManager
            The finance manager instance to save/load data from.
        """
        self.manager = manager

    def save_session(self):
        """
        Save current session to a JSON file with user file dialog.

        Opens a file dialog for the user to choose save location,
        then saves all session data including players, transactions,
        and settings to a JSON file.

        Returns
        -------
        bool
            True if save was successful, False otherwise.
        """
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("REPO Finance Files", "*.json"), ("All Files", "*.*")],
            title="Save REPO Finance Session",
        )

        if not filepath:
            return False

        try:
            save_data = {
                "version": "1.0",
                "saved_at": datetime.now().isoformat(),
                "players": self.manager.players,
                "round_number": self.manager.round_number,
                "transaction_history": self.manager.transaction_history,
                "group_fund": self.manager.group_fund,
                "total_money_at_round_start": self.manager.total_money_at_round_start,
                "kill_bonuses_this_round": self.manager.kill_bonuses_this_round,
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)

            messagebox.showinfo(
                "Success", f"Session saved to:\n{os.path.basename(filepath)}"
            )
            return True

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save session:\n{str(e)}")
            return False

    def load_session(self):
        """
        Load session from a JSON file with user file dialog.

        Opens a file dialog for the user to choose a file to load,
        then loads all session data and updates the finance manager.
        Shows confirmation dialog before overwriting current data.

        Returns
        -------
        bool
            True if load was successful, False otherwise.
        """
        # Confirm before loading
        if not messagebox.askyesno(
            "Confirm", "Loading will replace current data. Continue?"
        ):
            return False

        filepath = filedialog.askopenfilename(
            filetypes=[("REPO Finance Files", "*.json"), ("All Files", "*.*")],
            title="Load REPO Finance Session",
        )

        if not filepath:
            return False

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                save_data = json.load(f)

            # Validate data structure
            if not isinstance(save_data, dict):
                raise ValueError("Invalid file format")

            # Load data with defaults for missing fields
            self.manager.players = save_data.get("players", {})
            self.manager.round_number = save_data.get("round_number", 1)
            self.manager.transaction_history = save_data.get("transaction_history", [])
            self.manager.group_fund = save_data.get("group_fund", 0.0)
            self.manager.total_money_at_round_start = save_data.get(
                "total_money_at_round_start", 0.0
            )
            self.manager.kill_bonuses_this_round = save_data.get(
                "kill_bonuses_this_round", 0.0
            )

            messagebox.showinfo(
                "Success", f"Session loaded from:\n{os.path.basename(filepath)}"
            )
            return True

        except json.JSONDecodeError:
            messagebox.showerror(
                "Error", "File is not a valid JSON file or is corrupted."
            )
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load session:\n{str(e)}")
            return False

    def export_summary(self):
        """
        Export a human-readable summary to a text file.

        Opens a file dialog for the user to choose export location,
        then creates a formatted text report with all current data
        including player balances, group fund, and transaction history.

        Returns
        -------
        bool
            True if export was successful, False otherwise.
        """
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Export Summary Report",
        )

        if not filepath:
            return False

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                # Header
                f.write("REPO Finance Manager - Session Summary\n")
                f.write("=" * 50 + "\n")
                f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Current Round: {self.manager.round_number}\n\n")

                # Player balances
                f.write("PLAYER BALANCES (Rounded to REPO Currency)\n")
                f.write("-" * 50 + "\n")
                rounded_balances = self.manager.get_all_rounded_balances()

                if rounded_balances:
                    for player, balance in sorted(rounded_balances.items()):
                        if balance >= 1000:
                            balance_text = f"{balance // 1000}k"
                        else:
                            balance_text = f"{balance}"
                        f.write(f"{player:<20}: {balance_text}\n")

                    total_player_money = sum(rounded_balances.values())
                    f.write("-" * 30 + "\n")
                    if total_player_money >= 1000:
                        total_text = f"{total_player_money // 1000}k"
                    else:
                        total_text = f"{total_player_money}"
                    f.write(f"{'Total Player Money':<20}: {total_text}\n")
                else:
                    f.write("No players currently in the group.\n")

                # Group fund
                group_fund_rounded = self.manager.get_group_fund_rounded()
                if group_fund_rounded >= 1000:
                    fund_text = f"{group_fund_rounded // 1000}k"
                else:
                    fund_text = f"{group_fund_rounded}"
                f.write(f"{'Group Fund':<20}: {fund_text}\n")

                # Grand total
                if rounded_balances:
                    grand_total = sum(rounded_balances.values()) + group_fund_rounded
                    if grand_total >= 1000:
                        grand_total_text = f"{grand_total // 1000}k"
                    else:
                        grand_total_text = f"{grand_total}"
                    f.write(f"{'GRAND TOTAL':<20}: {grand_total_text}\n\n")

                # Transaction history
                f.write("TRANSACTION HISTORY\n")
                f.write("-" * 50 + "\n")

                if self.manager.transaction_history:
                    # Show last 20 transactions, newest first
                    recent_transactions = list(
                        reversed(self.manager.transaction_history[-20:])
                    )

                    for transaction in recent_transactions:
                        # Format transaction based on type
                        if transaction["type"] == "shared_earnings_auto":
                            f.write(
                                f"Round {transaction['round']}: {transaction['description']}\n"
                            )
                            f.write(
                                f"  → NEW EARNINGS: {transaction.get('shared_earnings', 0):.0f}\n"
                            )
                            f.write(
                                f"  → Per player: {transaction.get('per_player', 0)}\n"
                            )
                            if transaction.get("remainder_to_fund", 0) > 0:
                                f.write(
                                    f"  → To group fund: {transaction['remainder_to_fund']:.0f}\n"
                                )

                        elif transaction["type"] == "kill_bonus":
                            f.write(
                                f"Round {transaction['round']}: {transaction['description']}\n"
                            )
                            f.write(f"  → Total: {transaction['total_amount']}\n")
                            f.write(
                                f"  → Players: {', '.join(transaction['players'])}\n"
                            )
                            if transaction.get("group_fund_used", 0) > 0:
                                f.write(
                                    f"  → Used from group fund: {transaction['group_fund_used']}\n"
                                )

                        elif transaction["type"] == "spending":
                            f.write(
                                f"Round {transaction['round']}: {transaction['player']} Spending\n"
                            )
                            f.write(f"  → Amount: {transaction['amount']}\n")
                            f.write(f"  → Item: {transaction['description']}\n")

                        elif transaction["type"] == "group_fund_addition":
                            f.write(
                                f"Round {transaction['round']}: Group Fund Addition\n"
                            )
                            f.write(f"  → Amount: {transaction['amount']}\n")
                            f.write(f"  → Reason: {transaction['description']}\n")

                        elif transaction["type"] == "group_fund_usage":
                            f.write(f"Round {transaction['round']}: Group Fund Usage\n")
                            f.write(f"  → Amount: {transaction['amount']}\n")
                            f.write(f"  → Reason: {transaction['description']}\n")

                        elif transaction["type"] == "player_removal_redistribution":
                            f.write(f"Round {transaction['round']}: Player Removal\n")
                            f.write(
                                f"  → Removed: {transaction.get('removed_player', 'Unknown')}\n"
                            )
                            f.write(
                                f"  → Redistributed: {transaction.get('original_balance', 0):.0f}\n"
                            )

                        f.write("\n")
                else:
                    f.write("No transactions recorded.\n\n")

                # Footer
                f.write("-" * 50 + "\n")
                f.write("End of Report\n")

            messagebox.showinfo(
                "Success", f"Summary exported to:\n{os.path.basename(filepath)}"
            )
            return True

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export summary:\n{str(e)}")
            return False

    def quick_save(self, filename=None):
        """
        Quick save without dialog to a default or specified filename.

        Parameters
        ----------
        filename : str, optional
            Filename to save to. If None, uses timestamp-based name.

        Returns
        -------
        bool
            True if save was successful, False otherwise.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"repo_session_{timestamp}.json"

        try:
            save_data = {
                "version": "1.0",
                "saved_at": datetime.now().isoformat(),
                "players": self.manager.players,
                "round_number": self.manager.round_number,
                "transaction_history": self.manager.transaction_history,
                "group_fund": self.manager.group_fund,
                "total_money_at_round_start": self.manager.total_money_at_round_start,
                "kill_bonuses_this_round": self.manager.kill_bonuses_this_round,
            }

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)

            return True

        except Exception:
            return False
