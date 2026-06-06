"""
REPO Finance Manager - GUI Interface

This module contains the graphical user interface for the REPO Finance Manager,
built with NiceGUI. It provides a tabbed interface for managing players,
transactions, balances, and transaction history.
"""

from nicegui import ui
from repo_finance_core import RepoFinanceManager, round_money_down

manager = RepoFinanceManager()
kill_checkboxes: dict = {}
spending_ui: dict = {}


def format_money(amount):
    """
    Format a money amount as a 'k' string for display.
    """
    rounded = round_money_down(amount)
    if rounded >= 1000:
        return f"{rounded // 1000}k"
    return str(rounded)


### Refreshable UI sections ###


@ui.refreshable
def players_list():
    """Display current players with remove buttons."""
    if not manager.players:
        ui.label("No players added yet.").classes("text-gray-400 italic")
        return
    for player in manager.players:
        with ui.row().classes(
            "w-full items-center justify-between bg-gray-800 rounded p-2"
        ):
            ui.label(player).classes("text-green-400 font-bold")
            ui.button(
                icon="person_remove", on_click=lambda p=player: remove_player(p)
            ).props("flat round dense color=red")


@ui.refreshable
def kill_player_checkboxes():
    """Display player checkboxes for kill bonus selection."""
    if not manager.players:
        ui.label("Add players first.").classes("text-gray-400 italic text-sm")
        return
    for player in manager.players:
        cb = ui.checkbox(player).classes("text-white")
        kill_checkboxes[player] = cb


@ui.refreshable
def balances_display():
    """Display all player balances and group fund."""
    rounded = manager.get_all_rounded_balances()

    for player, balance in rounded.items():
        with ui.card().classes("w-full bg-gray-800 border border-green-400"):
            ui.label(player).classes("text-green-400 font-bold text-lg")
            ui.label(format_money(balance)).classes("text-white text-2xl font-bold")

    if manager.players:
        total = sum(rounded.values())
        with ui.card().classes("w-full bg-green-400"):
            ui.label("Total Group Money").classes("text-black font-bold text-lg")
            ui.label(format_money(total)).classes("text-black text-2xl font-bold")

    with ui.card().classes("w-full bg-orange-500"):
        ui.label("Group Fund (Puffer)").classes("text-white font-bold text-lg")
        ui.label(format_money(manager.group_fund)).classes(
            "text-white text-2xl font-bold"
        )


@ui.refreshable
def history_display():
    """Display transaction history with delete buttons."""
    transactions = list(reversed(manager.transaction_history[-20:]))

    if not transactions:
        ui.label("No transactions yet.").classes("text-gray-400 italic")
        return

    for i, t in enumerate(transactions):
        actual_index = len(manager.transaction_history) - 1 - i

        # Build text and color per transaction type
        if t["type"] == "shared_earnings_auto":
            color = "border-green-400"
            text = f"Round {t['round']}: {t['description']} — NEW: {t['shared_earnings']:.0f} ({t['per_player']} each"
            if t.get("remainder_to_fund", 0) > 0:
                text += f", +{t['remainder_to_fund']:.0f} to fund"
            text += f") [Game: {t['game_total']:.0f}]"

        elif t["type"] == "kill_bonus":
            color = "border-blue-400"
            text = f"Round {t['round']}: {t['description']} — {t['total_amount']} to {', '.join(t['players'])}"
            if t.get("group_fund_used", 0) > 0:
                text += f" (used {t['group_fund_used']} from fund)"
            elif t.get("remainder_to_fund", 0) > 0:
                text += f" (+{t['remainder_to_fund']:.0f} to fund)"

        elif t["type"] == "spending":
            color = "border-red-400"
            text = f"Round {t['round']}: {t['player']} spent {t['amount']} on {t['description']}"

        elif t["type"] == "player_removal_redistribution":
            color = "border-yellow-400"
            text = f"Round {t['round']}: {t['description']} — {t['original_balance']:.0f} redistributed ({t['per_player']} each"
            if t.get("remainder_to_fund", 0) > 0:
                text += f", +{t['remainder_to_fund']:.0f} to fund"
            text += ")"

        elif t["type"] in ("group_fund_addition", "group_fund_usage"):
            color = "border-orange-400"
            sign = "+" if t["type"] == "group_fund_addition" else "-"
            text = f"Round {t['round']}: {sign}{t['amount']} group fund ({t['description']})"

        else:
            color = "border-gray-400"
            text = str(t)

        with ui.row().classes(
            f"w-full border-l-4 {color} pl-3 py-1 bg-gray-800 rounded items-center justify-between"
        ):
            ui.label(text).classes("text-white text-sm flex-1")
            ui.button(
                icon="delete", on_click=lambda idx=actual_index: delete_transaction(idx)
            ).props("flat round dense color=red")


@ui.refreshable
def round_label():
    """Display current round number."""
    ui.label(f"Round: {manager.round_number}").classes(
        "text-black bg-green-400 font-bold px-4 py-2 rounded"
    )


@ui.refreshable
def current_total_label():
    """Display current total money in shared earnings section."""
    ui.label(f"Current Total Money: {format_money(manager.get_total_money())}").classes(
        "text-green-400 font-bold text-sm"
    )


def refresh():
    """Refresh all dynamic UI sections."""
    round_label.refresh()
    players_list.refresh()
    kill_checkboxes.clear()
    kill_player_checkboxes.refresh()
    balances_display.refresh()
    history_display.refresh()
    current_total_label.refresh()
    if "select" in spending_ui:
        spending_ui["select"].options = list(manager.players.keys())
        spending_ui["select"].update()


def remove_player(player_name):
    """Show confirmation dialog and remove player with money redistribution."""
    balance = manager.players.get(player_name, 0)
    msg = f"Remove {player_name}?"
    if balance > 0:
        msg += f"\n⚠️ {balance:.0f} will be redistributed to remaining players + group fund."

    with ui.dialog() as dialog, ui.card().classes("bg-gray-800"):
        ui.label(msg).classes("text-white text-sm")
        with ui.row():
            ui.button("Cancel", on_click=dialog.close).props("flat color=white")
            ui.button(
                "Remove",
                on_click=lambda: (
                    manager.remove_player(player_name),
                    dialog.close(),
                    refresh(),
                    ui.notify(f"{player_name} removed.", color="warning"),
                ),
            ).props("color=red")
    dialog.open()


def delete_transaction(index):
    """Delete a transaction by index and reverse its effects."""
    if manager.delete_transaction(index):
        refresh()
        ui.notify("Transaction deleted.", color="positive")


# Main UI


def create_ui():
    """Build the complete NiceGUI interface."""

    ui.query("body").style("background-color: #1a1a2e; color: white;")

    # Header
    with ui.header().classes("bg-gray-900 items-center justify-between px-6 py-3"):
        ui.label("🤖 REPO Finance Manager").classes("text-green-400 text-2xl font-bold")
        with ui.row().classes("items-center gap-4"):
            round_label()
            ui.button(
                "🔄 Start New Round",
                on_click=lambda: (
                    manager.start_new_round(),
                    refresh(),
                    ui.notify(
                        f"Round {manager.round_number} started!", color="positive"
                    ),
                ),
            ).classes("bg-green-500 text-black font-bold")

    # Tabs
    with ui.tabs().classes("w-full bg-gray-900 text-green-400") as tabs:
        tab_players = ui.tab("👥 Players")
        tab_transactions = ui.tab("💰 Transactions")
        tab_balances = ui.tab("💳 Balances")
        tab_history = ui.tab("📜 History")

    with ui.tab_panels(tabs, value=tab_players).classes("w-full bg-transparent"):

        # Players Tab
        with ui.tab_panel(tab_players):
            with ui.card().classes("w-full bg-gray-800 mb-4"):
                ui.label("Add Player").classes("text-green-400 font-bold text-lg mb-2")
                player_input = ui.input(placeholder="Player name...").classes("w-full")

                def add_player():
                    name = player_input.value.strip()
                    if not name:
                        ui.notify("Please enter a name.", color="negative")
                        return
                    if not manager.add_player(name):
                        ui.notify(f"{name} already exists!", color="warning")
                        return
                    player_input.value = ""
                    refresh()
                    ui.notify(f"{name} added!", color="positive")

                player_input.on("keydown.enter", add_player)
                ui.button("Add Player", on_click=add_player).classes(
                    "bg-green-500 text-black font-bold mt-2"
                )

            with ui.card().classes("w-full bg-gray-800"):
                ui.label("Current Players").classes(
                    "text-green-400 font-bold text-lg mb-2"
                )
                players_list()
                ui.separator().classes("my-2")

                def reset_confirm():
                    with ui.dialog() as d, ui.card().classes("bg-gray-800"):
                        ui.label("Reset ALL data?").classes("text-white")
                        with ui.row():
                            ui.button("Cancel", on_click=d.close).props(
                                "flat color=white"
                            )
                            ui.button(
                                "Reset",
                                on_click=lambda: (
                                    manager.reset_all(),
                                    d.close(),
                                    refresh(),
                                    ui.notify("All data reset.", color="warning"),
                                ),
                            ).props("color=red")
                    d.open()

                ui.button("🗑️ Reset All", on_click=reset_confirm).classes(
                    "bg-red-600 text-white font-bold"
                )

        # Transactions Tab
        with ui.tab_panel(tab_transactions):
            with ui.column().classes("w-full gap-4"):

                # Kill Bonus
                with ui.card().classes("w-full bg-gray-800"):
                    ui.label("💀 Kill Bonus (Enter First)").classes(
                        "text-green-400 font-bold text-lg mb-2"
                    )
                    kill_amount = ui.number(label="Amount", format="%.0f").classes(
                        "w-full"
                    )
                    kill_desc = ui.input(label="Description (optional)").classes(
                        "w-full"
                    )
                    ui.label("Players involved:").classes("text-gray-300 text-sm mt-2")
                    kill_player_checkboxes()
                    kill_use_fund = ui.checkbox(
                        "Use Group Fund if amounts too small"
                    ).classes("text-white mt-2")

                    def on_add_kill_bonus():
                        try:
                            amount = float(kill_amount.value)
                        except (ValueError, TypeError):
                            ui.notify("Enter a valid amount.", color="negative")
                            return
                        selected = [p for p, cb in kill_checkboxes.items() if cb.value]
                        if not selected:
                            ui.notify("Select at least one player.", color="negative")
                            return
                        desc = kill_desc.value or "Kill bonus"
                        if manager.add_kill_bonus(
                            amount, selected, desc, kill_use_fund.value
                        ):
                            kill_amount.value = ""
                            kill_desc.value = ""
                            kill_use_fund.value = False
                            refresh()
                            ui.notify(
                                f"Kill bonus of {amount} added!", color="positive"
                            )

                    ui.button("Add Kill Bonus", on_click=on_add_kill_bonus).classes(
                        "bg-blue-500 text-white font-bold mt-2"
                    )

                # Shared Earnings
                with ui.card().classes("w-full bg-gray-800"):
                    ui.label("💰 Shared Earnings (Auto-Calculate)").classes(
                        "text-green-400 font-bold text-lg mb-2"
                    )
                    current_total_label()
                    shared_amount = ui.number(
                        label="Total Money Shown in REPO", format="%.0f"
                    ).classes("w-full")
                    shared_desc = ui.input(label="Description (optional)").classes(
                        "w-full"
                    )

                    def on_add_shared():
                        try:
                            total = float(shared_amount.value)
                        except (ValueError, TypeError):
                            ui.notify("Enter a valid amount.", color="negative")
                            return
                        desc = shared_desc.value or "Round earnings"
                        success, total_new, shared = manager.add_shared_earnings_auto(
                            total, desc
                        )
                        if success:
                            shared_amount.value = ""
                            shared_desc.value = ""
                            refresh()
                            ui.notify(
                                f"Split {shared:.0f}! (Kill bonuses: {manager.kill_bonuses_this_round:.0f} excluded)",
                                color="positive",
                            )
                        elif total_new <= 0:
                            ui.notify(
                                f"No new money. Game: {total:.0f} vs previous: {manager.total_money_at_round_start:.0f}",
                                color="warning",
                            )
                        else:
                            ui.notify("Add players first.", color="negative")

                    ui.button(
                        "Auto-Split New Earnings", on_click=on_add_shared
                    ).classes("bg-green-500 text-black font-bold mt-2")

                # Group Fund
                with ui.card().classes("w-full bg-gray-800"):
                    ui.label("🏦 Group Fund Management").classes(
                        "text-green-400 font-bold text-lg mb-2"
                    )

                    ui.label("Add to Group Fund:").classes("text-gray-300 text-sm")
                    with ui.row().classes("w-full gap-2 items-center"):
                        fund_add_amount = ui.number(
                            label="Amount", format="%.0f"
                        ).classes("flex-1")
                        fund_add_desc = ui.input(label="Description").classes("flex-1")
                        ui.button(
                            "Add to Fund",
                            on_click=lambda: (
                                manager.add_to_group_fund(
                                    float(fund_add_amount.value or 0),
                                    fund_add_desc.value or "Group fund addition",
                                ),
                                setattr(fund_add_amount, "value", ""),
                                setattr(fund_add_desc, "value", ""),
                                refresh(),
                                ui.notify("Added to fund!", color="positive"),
                            ),
                        ).classes("bg-orange-500 text-white font-bold")

                    ui.separator().classes("my-2")

                    ui.label("Use from Group Fund:").classes("text-gray-300 text-sm")
                    with ui.row().classes("w-full gap-2 items-center"):
                        fund_use_amount = ui.number(
                            label="Amount", format="%.0f"
                        ).classes("flex-1")
                        fund_use_desc = ui.input(label="Description").classes("flex-1")

                        def on_use_fund():
                            try:
                                amount = float(fund_use_amount.value)
                            except (ValueError, TypeError):
                                ui.notify("Enter a valid amount.", color="negative")
                                return
                            if manager.use_group_fund(
                                amount, fund_use_desc.value or "Group fund usage"
                            ):
                                fund_use_amount.value = ""
                                fund_use_desc.value = ""
                                refresh()
                                ui.notify("Used from fund!", color="positive")
                            else:
                                ui.notify("Insufficient funds!", color="negative")

                        ui.button("Use from Fund", on_click=on_use_fund).classes(
                            "bg-orange-700 text-white font-bold"
                        )

                # Player Spending
                with ui.card().classes("w-full bg-gray-800"):
                    ui.label("🛒 Player Spending").classes(
                        "text-green-400 font-bold text-lg mb-2"
                    )
                    spending_select = ui.select(
                        options=list(manager.players.keys()), label="Select Player"
                    ).classes("w-full")
                    spending_ui["select"] = spending_select
                    spending_amount = ui.number(label="Amount", format="%.0f").classes(
                        "w-full"
                    )
                    spending_desc = ui.input(label="Item purchased (optional)").classes(
                        "w-full"
                    )

                    def on_record_spending():
                        if not spending_select.value:
                            ui.notify("Select a player.", color="negative")
                            return
                        try:
                            amount = float(spending_amount.value)
                        except (ValueError, TypeError):
                            ui.notify("Enter a valid amount.", color="negative")
                            return
                        desc = spending_desc.value or "Purchase"
                        if manager.record_spending(spending_select.value, amount, desc):
                            spending_select.value = None
                            spending_amount.value = ""
                            spending_desc.value = ""
                            refresh()
                            ui.notify(f"Spending recorded!", color="positive")
                        else:
                            ui.notify("Player not found.", color="negative")

                    ui.button("Record Spending", on_click=on_record_spending).classes(
                        "bg-red-600 text-white font-bold mt-2"
                    )

        # Balances Tab
        with ui.tab_panel(tab_balances):
            with ui.card().classes("w-full bg-gray-800"):
                ui.label("💳 Current Balances").classes(
                    "text-green-400 font-bold text-xl mb-4"
                )
                balances_display()

        # History Tab
        with ui.tab_panel(tab_history):
            with ui.card().classes("w-full bg-gray-800"):
                with ui.row().classes("items-center justify-between mb-4"):
                    ui.label("📜 Transaction History").classes(
                        "text-green-400 font-bold text-xl"
                    )
                    ui.button(
                        "↶ Undo Last",
                        on_click=lambda: (
                            manager.undo_last_transaction()
                            if manager.transaction_history
                            else None,
                            refresh(),
                            ui.notify("Undone!", color="positive"),
                        ),
                    ).classes("bg-blue-500 text-white font-bold")
                history_display()
