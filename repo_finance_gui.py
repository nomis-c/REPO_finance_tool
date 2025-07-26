"""
REPO Finance Manager - GUI Interface

This module contains the graphical user interface for the REPO Finance Manager,
built with tkinter. It provides a tabbed interface for managing players,
transactions, balances, and transaction history.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkinter import font as tkFont

from repo_finance_core import RepoFinanceManager, round_money_down


class RepoFinanceGUI:
    """
    Graphical user interface for the REPO Finance Manager.

    This class provides a tkinter-based GUI for managing REPO group finances,
    including tabs for player management, transactions, balance viewing, and
    transaction history with full mouse wheel support.
    """

    def __init__(self, root):
        """
        Initialize the GUI with the main window and all interface components.

        Parameters
        ----------
        root : tk.Tk
            The main tkinter window root object.
        """
        self.root = root
        self.manager = RepoFinanceManager()

        # Configure main window
        self.root.title("🤖 REPO Finance Manager")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1a1a2e')

        # Configure styles
        self.setup_styles()

        # Create main interface
        self.create_widgets()

        # Update display
        self.update_display()

    def setup_styles(self):
        """
        Configure the visual styles and themes for the GUI components.

        Sets up custom colors, fonts, and styling for labels, buttons, and other
        tkinter widgets to match the REPO gaming aesthetic.
        """
        style = ttk.Style()
        style.theme_use('clam')

        # Configure colors
        style.configure('Title.TLabel',
                        background='#1a1a2e',
                        foreground='#00ff88',
                        font=('Segoe UI', 20, 'bold'))

        style.configure('Heading.TLabel',
                        background='#1a1a2e',
                        foreground='#00ff88',
                        font=('Segoe UI', 12, 'bold'))

        style.configure('Custom.TLabel',
                        background='#1a1a2e',
                        foreground='white',
                        font=('Segoe UI', 10))

        style.configure('Round.TLabel',
                        background='#00ff88',
                        foreground='black',
                        font=('Segoe UI', 14, 'bold'),
                        padding=10)

        style.configure('Custom.TButton',
                        font=('Segoe UI', 10, 'bold'))

        style.configure('Custom.TEntry',
                        font=('Segoe UI', 10))

    def create_widgets(self):
        """
        Create and layout all GUI widgets including tabs, frames, and controls.

        Sets up the main window layout with title, round indicator, and tabbed
        interface containing Players, Transactions, Balances, and History tabs.
        """
        # Main container
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Title and round indicator
        title_frame = tk.Frame(main_frame, bg='#1a1a2e')
        title_frame.pack(fill='x', pady=(0, 20))

        title_label = ttk.Label(title_frame, text="🤖 REPO Finance Manager", style='Title.TLabel')
        title_label.pack()

        round_frame = tk.Frame(title_frame, bg='#1a1a2e')
        round_frame.pack(pady=10)

        self.round_label = ttk.Label(round_frame, text="Round: 1", style='Round.TLabel')
        self.round_label.pack(side='left', padx=5)

        new_round_btn = ttk.Button(round_frame, text="🔄 Start New Round",
                                   command=self.start_new_round, style='Custom.TButton')
        new_round_btn.pack(side='left', padx=5)

        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)

        # Players tab
        players_frame = tk.Frame(notebook, bg='#2c2c54')
        notebook.add(players_frame, text="👥 Players")
        self.create_players_tab(players_frame)

        # Transactions tab
        transactions_frame = tk.Frame(notebook, bg='#2c2c54')
        notebook.add(transactions_frame, text="💰 Transactions")
        self.create_transactions_tab(transactions_frame)

        # Balances tab
        balances_frame = tk.Frame(notebook, bg='#2c2c54')
        notebook.add(balances_frame, text="💳 Balances")
        self.create_balances_tab(balances_frame)

        # History tab
        history_frame = tk.Frame(notebook, bg='#2c2c54')
        notebook.add(history_frame, text="📜 History")
        self.create_history_tab(history_frame)

    def create_players_tab(self, parent):
        """
        Create the Players tab interface for adding and removing players.

        Parameters
        ----------
        parent : tk.Widget
            The parent widget to contain this tab's content.
        """
        frame = tk.Frame(parent, bg='#2c2c54')
        frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Add player section
        add_frame = tk.LabelFrame(frame, text="Add Player", bg='#2c2c54', fg='#00ff88',
                                  font=('Segoe UI', 12, 'bold'))
        add_frame.pack(fill='x', pady=(0, 20))

        input_frame = tk.Frame(add_frame, bg='#2c2c54')
        input_frame.pack(fill='x', padx=10, pady=10)

        self.player_name_entry = ttk.Entry(input_frame, font=('Segoe UI', 12), width=30)
        self.player_name_entry.pack(side='left', padx=(0, 10))
        self.player_name_entry.bind('<Return>', lambda e: self.add_player())

        add_btn = ttk.Button(input_frame, text="Add Player", command=self.add_player)
        add_btn.pack(side='left')

        # Current players section
        players_frame = tk.LabelFrame(frame, text="Current Players", bg='#2c2c54', fg='#00ff88',
                                      font=('Segoe UI', 12, 'bold'))
        players_frame.pack(fill='both', expand=True)

        # Players listbox with scrollbar
        listbox_frame = tk.Frame(players_frame, bg='#2c2c54')
        listbox_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.players_listbox = tk.Listbox(listbox_frame, bg='#1a1a2e', fg='white',
                                          font=('Segoe UI', 11), selectbackground='#00ff88')
        scrollbar = ttk.Scrollbar(listbox_frame, orient='vertical', command=self.players_listbox.yview)
        self.players_listbox.configure(yscrollcommand=scrollbar.set)

        # Bind mouse wheel to players listbox
        def _on_mousewheel_players(event):
            self.players_listbox.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_to_mousewheel_players(event):
            self.players_listbox.bind_all("<MouseWheel>", _on_mousewheel_players)

        def _unbind_from_mousewheel_players(event):
            self.players_listbox.unbind_all("<MouseWheel>")

        self.players_listbox.bind('<Enter>', _bind_to_mousewheel_players)
        self.players_listbox.bind('<Leave>', _unbind_from_mousewheel_players)

        self.players_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Remove player button
        remove_btn = ttk.Button(players_frame, text="Remove Selected Player",
                                command=self.remove_player)
        remove_btn.pack(pady=10)

        # Reset button
        reset_btn = ttk.Button(players_frame, text="🗑️ Reset All", command=self.reset_all)
        reset_btn.pack(pady=5)

    def create_transactions_tab(self, parent):
        """
        Create the Transactions tab interface for managing all types of transactions.

        Parameters
        ----------
        parent : tk.Widget
            The parent widget to contain this tab's content.
        """
        # Create main frame with padding
        main_frame = tk.Frame(parent, bg='#2c2c54')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Create canvas and scrollbar for scrolling
        canvas = tk.Canvas(main_frame, bg='#2c2c54', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.transactions_scrollable_frame = tk.Frame(canvas, bg='#2c2c54')

        # Configure scrolling
        self.transactions_scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.transactions_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Bind mouse wheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Now use the scrollable frame for content
        frame = self.transactions_scrollable_frame

        # Shared earnings
        shared_frame = tk.LabelFrame(frame, text="Shared Earnings (Auto-Calculate)", bg='#2c2c54', fg='#00ff88',
                                     font=('Segoe UI', 12, 'bold'))
        shared_frame.pack(fill='x', pady=(0, 15), padx=10)

        shared_input = tk.Frame(shared_frame, bg='#2c2c54')
        shared_input.pack(fill='x', padx=10, pady=10)

        # Show current total for reference
        self.current_total_label = tk.Label(shared_input, text="Current Total Money: 0k",
                                            bg='#2c2c54', fg='#00ff88', font=('Segoe UI', 10, 'bold'))
        self.current_total_label.pack(anchor='w', pady=(0, 5))

        tk.Label(shared_input, text="Total Money Shown in REPO:", bg='#2c2c54', fg='white').pack(anchor='w')
        self.shared_amount_entry = ttk.Entry(shared_input, font=('Segoe UI', 10))
        self.shared_amount_entry.pack(fill='x', pady=(0, 5))

        tk.Label(shared_input, text="Description:", bg='#2c2c54', fg='white').pack(anchor='w')
        self.shared_desc_entry = ttk.Entry(shared_input, font=('Segoe UI', 10))
        self.shared_desc_entry.pack(fill='x', pady=(0, 5))

        ttk.Button(shared_input, text="Auto-Split New Earnings", command=self.add_shared_earnings_auto).pack(pady=5)

        # Kill bonus
        kill_frame = tk.LabelFrame(frame, text="Kill Bonus", bg='#2c2c54', fg='#00ff88',
                                   font=('Segoe UI', 12, 'bold'))
        kill_frame.pack(fill='x', pady=(0, 15), padx=10)

        kill_input = tk.Frame(kill_frame, bg='#2c2c54')
        kill_input.pack(fill='x', padx=10, pady=10)

        tk.Label(kill_input, text="Amount:", bg='#2c2c54', fg='white').pack(anchor='w')
        self.kill_amount_entry = ttk.Entry(kill_input, font=('Segoe UI', 10))
        self.kill_amount_entry.pack(fill='x', pady=(0, 5))

        tk.Label(kill_input, text="Description:", bg='#2c2c54', fg='white').pack(anchor='w')
        self.kill_desc_entry = ttk.Entry(kill_input, font=('Segoe UI', 10))
        self.kill_desc_entry.pack(fill='x', pady=(0, 5))

        tk.Label(kill_input, text="Players involved:", bg='#2c2c54', fg='white').pack(anchor='w')

        self.kill_players_frame = tk.Frame(kill_input, bg='#2c2c54')
        self.kill_players_frame.pack(fill='x', pady=(0, 5))

        ttk.Button(kill_input, text="Add Kill Bonus", command=self.add_kill_bonus).pack(pady=5)

        # Checkbox for using group fund
        self.use_group_fund_var = tk.BooleanVar()
        group_fund_cb = tk.Checkbutton(kill_input, text="Use Group Fund if amounts too small",
                                       variable=self.use_group_fund_var, bg='#2c2c54', fg='white',
                                       selectcolor='#1a1a2e')
        group_fund_cb.pack(pady=5)

        # Group Fund Management
        fund_frame = tk.LabelFrame(frame, text="Group Fund Management", bg='#2c2c54', fg='#00ff88',
                                   font=('Segoe UI', 12, 'bold'))
        fund_frame.pack(fill='x', padx=10, pady=(15, 0))

        fund_input = tk.Frame(fund_frame, bg='#2c2c54')
        fund_input.pack(fill='x', padx=10, pady=10)

        # Add to group fund
        tk.Label(fund_input, text="Add to Group Fund:", bg='#2c2c54', fg='white').pack(anchor='w')
        fund_add_frame = tk.Frame(fund_input, bg='#2c2c54')
        fund_add_frame.pack(fill='x', pady=(0, 10))

        self.fund_add_amount_entry = ttk.Entry(fund_add_frame, font=('Segoe UI', 10), width=15)
        self.fund_add_amount_entry.pack(side='left', padx=(0, 5))
        self.fund_add_desc_entry = ttk.Entry(fund_add_frame, font=('Segoe UI', 10))
        self.fund_add_desc_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        ttk.Button(fund_add_frame, text="Add to Fund", command=self.add_to_group_fund).pack(side='left')

        # Use from group fund
        tk.Label(fund_input, text="Use from Group Fund:", bg='#2c2c54', fg='white').pack(anchor='w')
        fund_use_frame = tk.Frame(fund_input, bg='#2c2c54')
        fund_use_frame.pack(fill='x')

        self.fund_use_amount_entry = ttk.Entry(fund_use_frame, font=('Segoe UI', 10), width=15)
        self.fund_use_amount_entry.pack(side='left', padx=(0, 5))
        self.fund_use_desc_entry = ttk.Entry(fund_use_frame, font=('Segoe UI', 10))
        self.fund_use_desc_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        ttk.Button(fund_use_frame, text="Use from Fund", command=self.use_group_fund).pack(side='left')

        # Spending
        spending_frame = tk.LabelFrame(frame, text="Player Spending", bg='#2c2c54', fg='#00ff88',
                                       font=('Segoe UI', 12, 'bold'))
        spending_frame.pack(fill='x', padx=10, pady=(15, 0))

        spending_input = tk.Frame(spending_frame, bg='#2c2c54')
        spending_input.pack(fill='x', padx=10, pady=10)

        tk.Label(spending_input, text="Player:", bg='#2c2c54', fg='white').pack(anchor='w')
        self.spending_player_combo = ttk.Combobox(spending_input, font=('Segoe UI', 10), state='readonly')
        self.spending_player_combo.pack(fill='x', pady=(0, 5))

        tk.Label(spending_input, text="Amount:", bg='#2c2c54', fg='white').pack(anchor='w')
        self.spending_amount_entry = ttk.Entry(spending_input, font=('Segoe UI', 10))
        self.spending_amount_entry.pack(fill='x', pady=(0, 5))

        tk.Label(spending_input, text="Item purchased (optional):", bg='#2c2c54', fg='white').pack(anchor='w')
        self.spending_desc_entry = ttk.Entry(spending_input, font=('Segoe UI', 10))
        self.spending_desc_entry.pack(fill='x', pady=(0, 5))

        ttk.Button(spending_input, text="Record Spending", command=self.record_spending).pack(pady=5)

    def create_balances_tab(self, parent):
        """
        Create the Balances tab interface for viewing current player balances.

        Parameters
        ----------
        parent : tk.Widget
            The parent widget to contain this tab's content.
        """
        frame = tk.Frame(parent, bg='#2c2c54')
        frame.pack(fill='both', expand=True, padx=20, pady=20)

        title = tk.Label(frame, text="Current Balances", bg='#2c2c54', fg='#00ff88',
                         font=('Segoe UI', 16, 'bold'))
        title.pack(pady=(0, 20))

        # Scrollable frame for balances
        canvas = tk.Canvas(frame, bg='#2c2c54', highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        self.balances_frame = tk.Frame(canvas, bg='#2c2c54')

        self.balances_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.balances_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Bind mouse wheel to canvas
        def _on_mousewheel_balances(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_to_mousewheel_balances(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel_balances)

        def _unbind_from_mousewheel_balances(event):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind('<Enter>', _bind_to_mousewheel_balances)
        canvas.bind('<Leave>', _unbind_from_mousewheel_balances)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_history_tab(self, parent):
        """
        Create the History tab interface for viewing and managing transaction history.

        Parameters
        ----------
        parent : tk.Widget
            The parent widget to contain this tab's content.
        """
        frame = tk.Frame(parent, bg='#2c2c54')
        frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Control buttons
        controls = tk.Frame(frame, bg='#2c2c54')
        controls.pack(fill='x', pady=(0, 10))

        ttk.Button(controls, text="↶ Undo Last Transaction",
                   command=self.undo_last_transaction).pack(side='left', padx=(0, 10))

        # Transaction history
        history_label = tk.Label(frame, text="Transaction History", bg='#2c2c54', fg='#00ff88',
                                 font=('Segoe UI', 14, 'bold'))
        history_label.pack(anchor='w', pady=(0, 10))

        # History listbox with scrollbar
        history_frame = tk.Frame(frame, bg='#2c2c54')
        history_frame.pack(fill='both', expand=True)

        self.history_listbox = tk.Listbox(history_frame, bg='#1a1a2e', fg='white',
                                          font=('Segoe UI', 10), selectbackground='#00ff88')
        history_scrollbar = ttk.Scrollbar(history_frame, orient='vertical',
                                          command=self.history_listbox.yview)
        self.history_listbox.configure(yscrollcommand=history_scrollbar.set)

        # Bind mouse wheel to history listbox
        def _on_mousewheel_history(event):
            self.history_listbox.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_to_mousewheel_history(event):
            self.history_listbox.bind_all("<MouseWheel>", _on_mousewheel_history)

        def _unbind_from_mousewheel_history(event):
            self.history_listbox.unbind_all("<MouseWheel>")

        self.history_listbox.bind('<Enter>', _bind_to_mousewheel_history)
        self.history_listbox.bind('<Leave>', _unbind_from_mousewheel_history)

        self.history_listbox.pack(side='left', fill='both', expand=True)
        history_scrollbar.pack(side='right', fill='y')

        # Delete transaction button
        delete_btn = ttk.Button(frame, text="❌ Delete Selected Transaction",
                                command=self.delete_selected_transaction)
        delete_btn.pack(pady=10)

    def update_display(self):
        """
        Update all GUI display elements with current data.

        Refreshes the round indicator, player lists, balance displays, transaction
        history, and all dropdowns/checkboxes to reflect current state.
        """
        self.update_round_display()
        self.update_players_display()
        self.update_balances_display()
        self.update_history_display()
        self.update_kill_checkboxes()
        self.update_spending_combo()
        self.update_current_total_display()

    def update_current_total_display(self):
        """Update the current total money display in the transactions tab."""
        if hasattr(self, 'current_total_label'):
            total = self.manager.get_total_money()
            total_rounded = round_money_down(total)
            if total_rounded >= 1000:
                total_text = f"{total_rounded // 1000}k"
            else:
                total_text = f"{total_rounded}"
            self.current_total_label.config(text=f"Current Total Money: {total_text}")

    def update_round_display(self):
        """Update the round number display in the header."""
        self.round_label.config(text=f"Round: {self.manager.round_number}")

    def update_players_display(self):
        """Update the player list display in the Players tab."""
        self.players_listbox.delete(0, tk.END)
        for player in self.manager.players:
            self.players_listbox.insert(tk.END, player)

    def update_balances_display(self):
        """
        Update the balance display with current player balances rounded to thousands.

        Displays each player's balance rounded down to nearest thousand (REPO format)
        and calculates the total group money. This reflects the actual spendable
        amounts in-game since REPO only allows thousand-unit transactions.
        """
        # Clear existing balance widgets
        for widget in self.balances_frame.winfo_children():
            widget.destroy()

        # Get rounded balances
        rounded_balances = self.manager.get_all_rounded_balances()

        # Add balance cards
        for player, rounded_balance in rounded_balances.items():
            balance_card = tk.Frame(self.balances_frame, bg='#1a1a2e', relief='raised', bd=2)
            balance_card.pack(fill='x', padx=10, pady=5)

            player_label = tk.Label(balance_card, text=player, bg='#1a1a2e', fg='#00ff88',
                                    font=('Segoe UI', 14, 'bold'))
            player_label.pack(pady=(10, 5))

            # Format as thousands (e.g., "2k" instead of "2000")
            if rounded_balance >= 1000:
                balance_text = f"{rounded_balance // 1000}k"
            else:
                balance_text = f"{rounded_balance}"

            balance_label = tk.Label(balance_card, text=balance_text, bg='#1a1a2e', fg='white',
                                     font=('Segoe UI', 18, 'bold'))
            balance_label.pack(pady=(0, 10))

        # Total (also rounded)
        if self.manager.players:
            total_rounded = sum(rounded_balances.values())
            total_card = tk.Frame(self.balances_frame, bg='#00ff88', relief='raised', bd=2)
            total_card.pack(fill='x', padx=10, pady=10)

            tk.Label(total_card, text="Total Group Money", bg='#00ff88', fg='black',
                     font=('Segoe UI', 14, 'bold')).pack(pady=(10, 5))

            # Format total as thousands
            if total_rounded >= 1000:
                total_text = f"{total_rounded // 1000}k"
            else:
                total_text = f"{total_rounded}"

            tk.Label(total_card, text=total_text, bg='#00ff88', fg='black',
                     font=('Segoe UI', 18, 'bold')).pack(pady=(0, 10))

        # Group Fund
        group_fund_rounded = self.manager.get_group_fund_rounded()
        fund_card = tk.Frame(self.balances_frame, bg='#ff6b35', relief='raised', bd=2)
        fund_card.pack(fill='x', padx=10, pady=5)

        tk.Label(fund_card, text="🏦 Group Fund (Puffer)", bg='#ff6b35', fg='white',
                 font=('Segoe UI', 14, 'bold')).pack(pady=(10, 5))

        # Format group fund as thousands
        if group_fund_rounded >= 1000:
            fund_text = f"{group_fund_rounded // 1000}k"
        else:
            fund_text = f"{group_fund_rounded}"

        tk.Label(fund_card, text=fund_text, bg='#ff6b35', fg='white',
                 font=('Segoe UI', 18, 'bold')).pack(pady=(0, 10))

    def update_history_display(self):
        """
        Update the transaction history display.

        Shows the most recent 20 transactions in reverse chronological order
        (newest first) with formatted descriptions for each transaction type,
        including group fund information and new auto-calculation features.
        """
        self.history_listbox.delete(0, tk.END)

        for i, transaction in enumerate(reversed(self.manager.transaction_history[-20:])):
            if transaction['type'] == 'shared_earnings':
                text = f"Round {transaction['round']}: {transaction['description']} - {transaction['total_amount']} total ({transaction['per_player']} each"
                if 'remainder_to_fund' in transaction and transaction['remainder_to_fund'] > 0:
                    text += f", +{transaction['remainder_to_fund']:.0f} to fund"
                text += ")"

            elif transaction['type'] == 'shared_earnings_auto':
                text = f"Round {transaction['round']}: {transaction['description']} - NEW: {transaction['new_earnings']:.0f} ({transaction['per_player']} each"
                if 'remainder_to_fund' in transaction and transaction['remainder_to_fund'] > 0:
                    text += f", +{transaction['remainder_to_fund']:.0f} to fund"
                text += f") [Game: {transaction['game_total']:.0f}]"

            elif transaction['type'] == 'player_removal_redistribution':
                text = f"Round {transaction['round']}: {transaction['description']} - {transaction['original_balance']:.0f} redistributed ({transaction['per_player']} each"
                if 'remainder_to_fund' in transaction and transaction['remainder_to_fund'] > 0:
                    text += f", +{transaction['remainder_to_fund']:.0f} to fund"
                text += ")"

            elif transaction['type'] == 'kill_bonus':
                text = f"Round {transaction['round']}: {transaction['description']} - {transaction['total_amount']} to {', '.join(transaction['players'])}"
                if 'group_fund_used' in transaction and transaction['group_fund_used'] > 0:
                    text += f" (used {transaction['group_fund_used']} from fund)"
                elif 'remainder_to_fund' in transaction and transaction['remainder_to_fund'] > 0:
                    text += f" (+{transaction['remainder_to_fund']:.0f} to fund)"

            elif transaction['type'] == 'spending':
                text = f"Round {transaction['round']}: {transaction['player']} spent {transaction['amount']} on {transaction['description']}"

            elif transaction['type'] == 'group_fund_addition':
                text = f"Round {transaction['round']}: +{transaction['amount']} to group fund ({transaction['description']})"

            elif transaction['type'] == 'group_fund_usage':
                text = f"Round {transaction['round']}: -{transaction['amount']} from group fund ({transaction['description']})"

            self.history_listbox.insert(tk.END, text)

    def update_kill_checkboxes(self):
        """
        Update the kill bonus player selection checkboxes.

        Recreates the checkbox interface for selecting which players participated
        in a monster kill when adding kill bonuses.
        """
        # Clear existing checkboxes
        for widget in self.kill_players_frame.winfo_children():
            widget.destroy()

        self.kill_checkboxes = {}
        for player in self.manager.players:
            var = tk.BooleanVar()
            cb = tk.Checkbutton(self.kill_players_frame, text=player, variable=var,
                                bg='#2c2c54', fg='white', selectcolor='#1a1a2e')
            cb.pack(side='left', padx=5)
            self.kill_checkboxes[player] = var

    def update_spending_combo(self):
        """Update the player selection dropdown for recording spending."""
        self.spending_player_combo['values'] = list(self.manager.players.keys())

    def add_player(self):
        """
        Add a new player from the input field.

        Reads the player name from the entry field, attempts to add them to the
        manager, and updates the display. Shows error message if unsuccessful.
        """
        name = self.player_name_entry.get().strip()
        if name and self.manager.add_player(name):
            self.player_name_entry.delete(0, tk.END)
            self.update_display()
        else:
            messagebox.showerror("Error", "Please enter a valid player name or player already exists.")

    def remove_player(self):
        """
        Remove the selected player from the group with money redistribution.

        Removes the currently selected player from the listbox after confirmation.
        Warns user about money redistribution and shows error message if no player is selected.
        """
        try:
            selected = self.players_listbox.curselection()[0]
            player_name = self.players_listbox.get(selected)

            # Get player's current balance to show in confirmation
            player_balance = self.manager.players.get(player_name, 0)

            # Show detailed confirmation with money redistribution info
            if player_balance > 0:
                confirmation_msg = (f"Remove {player_name} from the group?\n\n"
                                    f"⚠️ {player_name} has {player_balance:.0f} money remaining.\n"
                                    f"This money will be redistributed equally among:\n"
                                    f"• Remaining players\n"
                                    f"• Group fund\n\n"
                                    f"Continue with removal?")
            else:
                confirmation_msg = f"Remove {player_name} from the group?"

            if messagebox.askyesno("Confirm Player Removal", confirmation_msg):
                self.manager.remove_player(player_name)
                self.update_display()

        except IndexError:
            messagebox.showerror("Error", "Please select a player to remove.")

    def start_new_round(self):
        """Start a new round and update the display."""
        self.manager.start_new_round()
        self.update_display()

    def add_shared_earnings_auto(self):
        """
        Add shared earnings using automatic calculation of new money.

        Uses the new auto-calculation feature to determine how much new money
        was earned this round based on the total shown in REPO.
        """
        try:
            total_in_game = float(self.shared_amount_entry.get())
            description = self.shared_desc_entry.get() or "Round earnings"

            if total_in_game >= 0:
                success, new_earnings = self.manager.add_shared_earnings_auto(total_in_game, description)

                if success:
                    self.shared_amount_entry.delete(0, tk.END)
                    self.shared_desc_entry.delete(0, tk.END)
                    self.update_display()

                elif new_earnings <= 0:
                    messagebox.showwarning("No New Earnings",
                                           f"No new money to split.\n"
                                           f"Game total ({total_in_game:.0f}) is not higher than previous total "
                                           f"({self.manager.total_money_at_round_start:.0f}).")
                else:
                    messagebox.showerror("Error", "Please add players first.")
            else:
                messagebox.showerror("Error", "Please enter a valid amount.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")

    def add_kill_bonus(self):
        """
        Add kill bonus from the input fields and selected players.

        Reads amount and description from the kill bonus form, collects selected
        players from checkboxes, validates input, and adds the bonus. Clears
        fields and unchecks boxes on success.
        """
        try:
            amount = float(self.kill_amount_entry.get())
            description = self.kill_desc_entry.get() or "Kill bonus"
            use_group_fund = self.use_group_fund_var.get()

            selected_players = [player for player, var in self.kill_checkboxes.items() if var.get()]

            if amount > 0 and selected_players:
                if self.manager.add_kill_bonus(amount, selected_players, description, use_group_fund):
                    self.kill_amount_entry.delete(0, tk.END)
                    self.kill_desc_entry.delete(0, tk.END)
                    for var in self.kill_checkboxes.values():
                        var.set(False)
                    self.use_group_fund_var.set(False)
                    self.update_display()
            else:
                messagebox.showerror("Error", "Please enter a valid amount and select at least one player.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")

    def add_to_group_fund(self):
        """
        Add money to the group fund from the input fields.

        Reads amount and description from the group fund addition form,
        validates input, and adds to the fund. Clears fields on success.
        """
        try:
            amount = float(self.fund_add_amount_entry.get())
            description = self.fund_add_desc_entry.get() or "Group fund addition"

            if amount > 0:
                self.manager.add_to_group_fund(amount, description)
                self.fund_add_amount_entry.delete(0, tk.END)
                self.fund_add_desc_entry.delete(0, tk.END)
                self.update_display()
            else:
                messagebox.showerror("Error", "Please enter a valid positive amount.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")

    def use_group_fund(self):
        """
        Use money from the group fund from the input fields.

        Reads amount and description from the group fund usage form,
        validates input, and uses from the fund. Clears fields on success.
        """
        try:
            amount = float(self.fund_use_amount_entry.get())
            description = self.fund_use_desc_entry.get() or "Group fund usage"

            if amount > 0:
                if self.manager.use_group_fund(amount, description):
                    self.fund_use_amount_entry.delete(0, tk.END)
                    self.fund_use_desc_entry.delete(0, tk.END)
                    self.update_display()
                else:
                    messagebox.showerror("Error", "Insufficient funds in group fund.")
            else:
                messagebox.showerror("Error", "Please enter a valid positive amount.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")

    def record_spending(self):
        """
        Record player spending from the input fields.

        Reads player, amount, and description from the spending form, validates
        the input, and records the spending. Clears fields on success.
        """
        try:
            player = self.spending_player_combo.get()
            amount = float(self.spending_amount_entry.get())
            description = self.spending_desc_entry.get() or "Purchase"

            if player and amount > 0:
                if self.manager.record_spending(player, amount, description):
                    self.spending_player_combo.set('')
                    self.spending_amount_entry.delete(0, tk.END)
                    self.spending_desc_entry.delete(0, tk.END)
                    self.update_display()
            else:
                messagebox.showerror("Error", "Please select a player and enter a valid amount.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")

    def undo_last_transaction(self):
        """
        Undo the most recent transaction after confirmation.

        Shows a confirmation dialog and undoes the last transaction if confirmed.
        Updates the display to reflect the changes.
        """
        if not self.manager.transaction_history:
            messagebox.showinfo("Info", "No transactions to undo.")
            return

        if messagebox.askyesno("Confirm", "Undo the last transaction?"):
            if self.manager.undo_last_transaction():
                self.update_display()

    def delete_selected_transaction(self):
        """
        Delete the currently selected transaction from the history.

        Deletes the selected transaction from the history listbox after confirmation.
        Reverses the transaction's effects on player balances.
        """
        try:
            selected = self.history_listbox.curselection()[0]
            # Convert from reversed display index to actual index
            actual_index = len(self.manager.transaction_history) - 1 - selected

            if messagebox.askyesno("Confirm",
                                   "Delete this transaction? This will reverse its effects on player balances."):
                if self.manager.delete_transaction(actual_index):
                    self.update_display()
        except IndexError:
            messagebox.showerror("Error", "Please select a transaction to delete.")

    def reset_all(self):
        """
        Reset all data after confirmation.

        Clears all players, transactions, and resets to initial state after
        user confirmation. Updates display to show empty state.
        """
        if messagebox.askyesno("Confirm", "This will reset all data. Are you sure?"):
            self.manager.reset_all()
            self.update_display()