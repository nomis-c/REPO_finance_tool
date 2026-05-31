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
        ui.label('No players added yet.').classes('text-gray-400 italic')
        return
    for player in manager.players:
        with ui.row().classes('w-full items-center justify-between bg-gray-800 rounded p-2'):
            ui.label(player).classes('text-green-400 font-bold')
            ui.button(icon='person_remove',
                      on_click=lambda p=player: remove_player(p)
                      ).props('flat round dense color=red')


@ui.refreshable
def kill_player_checkboxes():
    """Display player checkboxes for kill bonus selection."""
    if not manager.players:
        ui.label('Add players first.').classes('text-gray-400 italic text-sm')
        return
    for player in manager.players:
        cb = ui.checkbox(player).classes('text-white')
        kill_checkboxes[player] = cb

@ui.refreshable
def balances_display():
    """Display all player balances and group fund."""
    rounded = manager.get_all_rounded_balances()

    for player, balance in rounded.items():
        with ui.card().classes('w-full bg-gray-800 border border-green-400'):
            ui.label(player).classes('text-green-400 font-bold text-lg')
            ui.label(format_money(balance)).classes('text-white text-2xl font-bold')

    if manager.players:
        total = sum(rounded.values())
        with ui.card().classes('w-full bg-green-400'):
            ui.label('Total Group Money').classes('text-black font-bold text-lg')
            ui.label(format_money(total)).classes('text-black text-2xl font-bold')

    with ui.card().classes('w-full bg-orange-500'):
        ui.label('Group Fund (Puffer)').classes('text-white font-bold text-lg')
        ui.label(format_money(manager.group_fund)).classes('text-white text-2xl font-bold')

@ui.refreshable
def history_display():
    """Display transaction history with delete buttons."""
    transactions = list(reversed(manager.transaction_history[-20:]))

    if not transactions:
        ui.label('No transactions yet.').classes('text-gray-400 italic')
        return

    for i, t in enumerate(transactions):
        actual_index = len(manager.transaction_history) - 1 - i

        # Build text and color per transaction type
        if t['type'] == 'shared_earnings_auto':
            color = 'border-green-400'
            text = f"Round {t['round']}: {t['description']} — NEW: {t['new_earnings']:.0f} ({t['per_player']} each"
            if t.get('remainder_to_fund', 0) > 0:
                text += f", +{t['remainder_to_fund']:.0f} to fund"
            text += f") [Game: {t['game_total']:.0f}]"

        elif t['type'] == 'kill_bonus':
            color = 'border-blue-400'
            text = f"Round {t['round']}: {t['description']} — {t['total_amount']} to {', '.join(t['players'])}"
            if t.get('group_fund_used', 0) > 0:
                text += f" (used {t['group_fund_used']} from fund)"
            elif t.get('remainder_to_fund', 0) > 0:
                text += f" (+{t['remainder_to_fund']:.0f} to fund)"

        elif t['type'] == 'spending':
            color = 'border-red-400'
            text = f"Round {t['round']}: {t['player']} spent {t['amount']} on {t['description']}"

        elif t['type'] == 'player_removal_redistribution':
            color = 'border-yellow-400'
            text = f"Round {t['round']}: {t['description']} — {t['original_balance']:.0f} redistributed ({t['per_player']} each"
            if t.get('remainder_to_fund', 0) > 0:
                text += f", +{t['remainder_to_fund']:.0f} to fund"
            text += ")"

        elif t['type'] in ('group_fund_addition', 'group_fund_usage'):
            color = 'border-orange-400'
            sign = '+' if t['type'] == 'group_fund_addition' else '-'
            text = f"Round {t['round']}: {sign}{t['amount']} group fund ({t['description']})"

        else:
            color = 'border-gray-400'
            text = str(t)

        with ui.row().classes(f'w-full border-l-4 {color} pl-3 py-1 bg-gray-800 rounded items-center justify-between'):
            ui.label(text).classes('text-white text-sm flex-1')
            ui.button(icon='delete',
                      on_click=lambda idx=actual_index: delete_transaction(idx)
                      ).props('flat round dense color=red')


@ui.refreshable
def round_label():
    """Display current round number."""
    ui.label(f"Round: {manager.round_number}").classes(
        'text-black bg-green-400 font-bold px-4 py-2 rounded'
    )


@ui.refreshable
def current_total_label():
    """Display current total money in shared earnings section."""
    ui.label(f"Current Total Money: {format_money(manager.get_total_money())}").classes(
        'text-green-400 font-bold text-sm'
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



def remove_player(player_name):
    pass

def delete_transaction(index):
    pass


def create_ui():
    pass
