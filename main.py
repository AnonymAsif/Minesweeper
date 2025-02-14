_author_ = "Asif Rahman"
_date_ = "Wednesday, May 11, 2022"
_version_ = "1.0"
_filename_ = "main.py"
_description_ = "Minesweeper Game for Final Assignment. Contains initial window for difficulty choice."

import tkinter as tk
from board import Board
from game_window import GameWindow

def set_difficulty(choice):
  """ Saves difficulty choice and starts game."""
  # Destroys difficulty choice window and starts game window
  initial_window.destroy()
  GameWindow(choice.lower())

# Window to contain widgets 
initial_window = tk.Tk()
initial_window.resizable(height=False, width=False)

# Listbox to contain difficulty choices
tk.Label(initial_window, text="Choose your initial difficulty:").pack()
difficulty_listbox = tk.Listbox(initial_window)

# Gives user the option of every difficulty
for i, difficulty in enumerate(Board.difficulties):
  difficulty_listbox.insert(i, difficulty.capitalize())
difficulty_listbox.pack()

# Submit button
tk.Button(initial_window, text="Submit Choice", command=
          lambda: set_difficulty(difficulty_listbox.get(difficulty_listbox.curselection()))).pack()

# Waits on users input
initial_window.mainloop()


