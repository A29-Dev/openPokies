import random
import tkinter as tk
from tkinter import messagebox
import threading
import tkinter.font as tkFont

# Emojis for pokies
EMOJIS = [
    ("A", 1.5),    # Ace
    ("K", 2),      # King
    ("Q", 5),      # Queen
    ("J", 10),     # Jack
    ("10", 100),   # Ten
    ("W", 0)       # Wild (W)
]

DENOMINATIONS = {
    "1c": 0.01,
    "2c": 0.02,
    "5c": 0.05,
    "10c": 0.10,
    "50c": 0.50,
    "$1": 1.00
}

class PokiesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aussie Pokies")
        self.root.geometry("600x700")
        self.root.configure(bg="black")

        self.balance = 100.0
        self.denom = 0.01
        self.denom_str = "1c"
        self.total_bet = 0.0
        self.jackpot = 0.0

        # Custom font for labels
        self.custom_font = tkFont.Font(family="Comic Sans MS", size=14, weight="bold")

        # UI Elements
        self.jackpot_label = tk.Label(root, text=f"Jackpot: ${self.jackpot:.2f}", font=("Comic Sans MS", 20), fg="gold", bg="black")
        self.jackpot_label.pack(pady=10)

        self.balance_label = tk.Label(root, text=f"Balance: ${self.balance:.2f}", font=self.custom_font, fg="white", bg="black")
        self.balance_label.pack(pady=10)

        self.grid_frame = tk.Frame(root, bg="black")
        self.grid_frame.pack(pady=20)
        self.grid_labels = [[tk.Label(self.grid_frame, text="", font=("Comic Sans MS", 18), width=4, height=2, relief="solid", bg="black", fg="white") for _ in range(5)] for _ in range(3)]
        for i in range(3):
            for j in range(5):
                self.grid_labels[i][j].grid(row=i, column=j, padx=5, pady=5)

        # Add toggle denomination button next to spin button
        self.button_frame = tk.Frame(root, bg="black")
        self.button_frame.pack(pady=10)

        self.spin_button = tk.Button(self.button_frame, text="Spin", command=self.spin_pokies, font=self.custom_font, bg="green", fg="white")
        self.spin_button.grid(row=0, column=0, padx=5)

        self.toggle_denom_button = tk.Button(self.button_frame, text=f"Denomination: {self.denom_str}", command=self.toggle_denomination, font=self.custom_font, bg="blue", fg="white")
        self.toggle_denom_button.grid(row=0, column=1, padx=5)

        self.result_label = tk.Label(root, text="", font=("Comic Sans MS", 16), fg="white", bg="black")
        self.result_label.pack(pady=10)

        # Add slider to adjust odds
        self.odds_scale = tk.Scale(root, from_=1, to=100, orient="horizontal", label="Adjust Odds", font=self.custom_font, bg="black", fg="white")
        self.odds_scale.set(70)  # Default odds increased for more wins
        self.odds_scale.pack(pady=10)

        self.update_jackpot()

    def update_jackpot(self):
        self.jackpot += 1.0
        self.jackpot_label.config(text=f"Jackpot: ${self.jackpot:.2f}")
        self.root.after(1000, self.update_jackpot)

    def toggle_denomination(self):
        denom_keys = list(DENOMINATIONS.keys())
        current_index = denom_keys.index(self.denom_str)
        next_index = (current_index + 1) % len(denom_keys)
        self.denom_str = denom_keys[next_index]
        self.denom = DENOMINATIONS[self.denom_str]
        self.toggle_denom_button.config(text=f"Denomination: {self.denom_str}")

    def spin_pokies(self):
        if self.balance < self.denom:
            self.prompt_deposit()
            return

        self.balance -= self.denom
        self.total_bet += self.denom

        # Adjust weights for more frequent wins
        odds = self.odds_scale.get()
        weights = [odds, odds, odds - 5, odds - 10, odds - 15, 20]  # Increased odds for better chances
        spin = random.choices(EMOJIS, weights=weights, k=15)
        grid = [spin[i:i+5] for i in range(0, 15, 5)]

        for i in range(3):
            for j in range(5):
                self.grid_labels[i][j].config(text=grid[i][j][0], bg="black", fg="white")

        win_lines = self.calculate_payout(grid)

        if win_lines:
            total_win = sum(self.get_multiplier(grid[i][j]) for line, indices in win_lines.items() for i, j in indices)
            self.balance += total_win
            self.flash_winning_lines(win_lines, grid)
            winning_lines = ", ".join(win_lines.keys())
            self.result_label.config(text=f"You won ${total_win:.2f} on lines: {winning_lines}!")
        else:
            self.result_label.config(text="No win this spin.")

        self.balance_label.config(text=f"Balance: ${self.balance:.2f}")

    def flash_winning_lines(self, win_lines, grid):
        def flash():
            for line, indices in win_lines.items():
                for i, j in indices:
                    current_color = self.grid_labels[i][j].cget("bg")
                    new_color = "yellow" if current_color == "black" else "black"
                    self.grid_labels[i][j].config(bg=new_color)
            self.root.after(300, flash)

        flash()

    def calculate_payout(self, grid):
        win_lines = {}
        for i in range(3):
            # Horizontal lines
            if self.check_line(grid[i]):
                win_lines[f"row-{i}"] = [(i, j) for j in range(5)]

            # Vertical lines
            column = [grid[j][i] for j in range(3)]
            if self.check_line(column):
                win_lines[f"col-{i}"] = [(j, i) for j in range(3)]

        # Diagonal lines
        diagonal1 = [grid[i][i] for i in range(3)]
        diagonal2 = [grid[i][4-i] for i in range(3)]
        if self.check_line(diagonal1):
            win_lines["diag-1"] = [(i, i) for i in range(3)]
        if self.check_line(diagonal2):
            win_lines["diag-2"] = [(i, 4-i) for i in range(3)]

        return win_lines

    def check_line(self, line):
        symbols = [e[0] for e in line if e[0] != "W"]
        return len(symbols) >= 3 and len(set(symbols)) == 1

    def get_multiplier(self, line):
        for emoji, multiplier in EMOJIS:
            if emoji in [e[0] for e in line]:
                return multiplier
        return 0

    def prompt_deposit(self):
        deposit_window = tk.Toplevel(self.root)
        deposit_window.title("Deposit Money")

        tk.Label(deposit_window, text="Enter amount to deposit:", font=self.custom_font).pack(pady=10)
        deposit_entry = tk.Entry(deposit_window, font=self.custom_font)
        deposit_entry.pack(pady=10)

        def add_deposit():
            try:
                amount = float(deposit_entry.get())
                if amount > 0:
                    self.balance += amount
                    self.balance_label.config(text=f"Balance: ${self.balance:.2f}")
                    deposit_window.destroy()
                else:
                    messagebox.showerror("Invalid Amount", "Please enter a positive amount.")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number.")

        tk.Button(deposit_window, text="Deposit", command=add_deposit, font=self.custom_font, bg="green", fg="white").pack(pady=10)

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = PokiesApp(root)
    root.mainloop()

