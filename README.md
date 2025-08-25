
# R.E.P.O. Finance Tool

This tool is designed for the game [R.E.P.O](https://store.steampowered.com/app/3241660/REPO) to manage finances as a group. 

## Key Features 

|     Features       |    Description      |                   
|----------------|-------------------------------|
|Player Management|    Add/remove players with automatic money redistribution     |       
|  Kill Bonus Tracking   |Distribute monster kill rewards among participating players|
|  Auto-Split Earnings      |  Automatically calculate and split new round earnings|
| Individual Spending     |Track personal equipment purchases and expenses|
| Transaction History    |Complete log of all financial activities with undo functionalitys|
| Save/Load Sessions   |Preserve progress across gaming sessions|






## Usage Guide


### **Players**
**Add players**

- Enter player name and click "Add Player" or press Enter

- New players start with 0 balance

**Remove Selected Player**

- Select a player from the list
 Click "Remove Selected Player"

- Player's remaining money is redistributed among remaining players and group fund

**Reset All**

- Clears all data and starts fresh

- Requires confirmation

### **Transaction**
**Kill Bonus**
- Amount: Total money from monster kill
- Use Group Fund: Supplement small amounts with group fund money if needed
- Automatically splits bonus among selected players

**Shared Earnings**
- Total Money Shown in REPO: Current total displayed in game

- Automatically calculates NEW earnings 

- Splits only the new money (excludes already-distributed kill bonuses)
- Remainder goes to group fund

**Group Fund Management**

- Add to Group Fund: Deposit money into shared pool
- Use from Group Fund: Withdraw money from shared pool
- Tracks all fund transactions

**Player Spending**

- Player: Select from dropdown
- Amount: Purchase cost
- Item purchased: Equipment or item name (optional)
- Deducts cost from player's balance

### Balances 
Displays current balances rounded to REPO's thousand-based currency:

- Individual player balances
- Total group money
- Group fund balance
- All amounts shown in "k" format (e.g., "5k" = 5000)


### History 
**Transaction History**
- Shows last 20 transactions (newest first)
- Detailed breakdown of all financial activities
- Color-coded by transaction type

**Undo Last Transaction**

- Reverses the most recent transaction
- Restores previous balances

### **File Operations**

**Save Session**
- Saves all data to JSON file
- Choose location and filename
- Preserves all players, transactions, and settings

**Load Session**
- Loads previously saved session
- Replaces current data (with confirmation)
- Restores complete game state

**Export Summary**
- Creates human-readable text report
- Includes current balances and recent transaction history
- Suitable for sharing or record-keeping

## Usage Example

1. **Start of Round**: Click "Start New Round"
2. **Kill monsters**: use "Kill bonus" for each monster kill
3. **End of Round**: Enter total money shown in REPO using "Auto-SPlit new Earning"
4. **Buy Equipment**: Record purchases using "Player Spending"
5. **Save Progress**: Use "Save Session" to preserve data

## How REPO Currency Works
REPO only allows transactions in thousands (1k, 2k, etc.). This tool:

- Rounds all player balances DOWN to nearest thousand
- Stores fractional amounts in the group fund
- Ensures no money is lost due to rounding
- Displays amounts in REPO-compatible format
