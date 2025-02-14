_author_ = "Asif Rahman"
_date_ = "Wednesday, June 1, 2022"
_version_ = "1.0"
_filename_ = "game_window.py"
_description_ = "Minesweeper window. Handles main game window and menubar."

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import colorchooser
from board import NewBoard
from board import LoadBoard
from board import Board
import json
import time

class GameWindow:
  """ Window for Minesweeper game. Contains menubar with File, Game, and Settings menu. Uses Board classes for game handling."""
  
  def __init__(self, initial_difficulty):
    """ Makes a board instance and outputs it."""
    
    # Saves window
    self.window = tk.Tk()
    self.window.resizable(height=False, width=False)
    
    # Menubar for game window
    self.menubar = tk.Menu(self.window)
    self.window.config(menu=self.menubar)
    self.menubar_setup()
    
    # Frame for the game board
    self.game_frame = tk.Frame(self.window)
    self.game_frame.pack()
    
    # Sets up a new board object with difficulty (and updates window title)
    self.board = NewBoard(initial_difficulty, self.game_frame)
    self.set_title()

    # Gets the time of the game starting
    self.session_start = time.time()

    # Win/Loss stats
    self.win_count = 0
    self.loss_count = 0

    # Starts window
    self.window.mainloop()
    
  def set_title(self):
    """ Sets the title of the window based on the difficulty."""
    self.window.title(f"Minesweeper - {self.board.game_difficulty.capitalize()}")
    
  def menubar_setup(self):
    """ Sets up menubar with File, Game, and Settings cascades."""
    # File menu
    file_menu = tk.Menu(self.menubar, tearoff=0)
    self.menubar.add_cascade(label="File", menu=file_menu)  
    file_menu.add_command(label="Open", command=self.load_game)
    file_menu.add_command(label="Save", command=self.save_game)

    # Game menu setup
    self.game_menu()
    
    # Settings menu
    self.menubar.add_command(label="Settings", command=self.settings_menu) 

  def game_menu(self):
    """ Game menu for menubar."""
    # Game menu
    game_menu = tk.Menu(self.menubar, tearoff=0)
    self.menubar.add_cascade(label="Game", menu=game_menu)  
    
    # New game
    new_game_menu = tk.Menu(game_menu, tearoff=False)
    game_menu.add_cascade(label="New", menu=new_game_menu)
    
    # For every difficulty
    for game_difficulty in NewBoard.difficulties:
      new_game_menu.add_command(label=game_difficulty.capitalize(), command=
                                lambda difficulty=game_difficulty: self.new_game(difficulty))

    # Stats window
    game_menu.add_command(label="Stats", command=self.stats_window_output)
    
  def stats_window_output(self):
    """ Displays game stats in a top level window. """

    def stats_update():
      """ Updates the stats in the stats_window."""
      # Updates Wins and Losses
      self.update_wins()
  
      # Dictionary of game and session statistics
      # Game Time and W/L ratio initialized to preserve order - value set below
      stats = {
        "Difficulty" : self.board.game_difficulty.capitalize(),
        "Board Size" : f"{self.board.board_size[0]}x{self.board.board_size[1]}",
        "Bombs" : self.board.bomb_count,
        "Remaining Flags" : self.board.flag_count,
        "Game Time" : None,  
        "Session Time": self.time_between(self.session_start, time.time()),
        "Session Wins" : self.win_count,
        "Session Losses" : self.loss_count,
        "Win/Loss Ratio" : None 
      }
      
      # Set game time (\n to separate Game and Sessions stats)
      if self.board.running:
        stats["Game Time"] = self.time_between(self.board.start_time, time.time())
        
      else:
        stats["Game Time"] = self.time_between(self.board.start_time, self.board.end_time) + "\n(completed)"
      stats["Game Time"] += "\n"
      
      # Divides ratio only if user has lost a game (prevents ZeroDivisionError)
      if self.loss_count > 0:
        stats["Win/Loss Ratio"] = round(self.win_count / self.loss_count, 2)
      else:
        stats["Win/Loss Ratio"] = f"{self.win_count}:{self.loss_count}"

      # Outputs all stats in the stats window
      for i, statistic in enumerate(stats):
        tk.Label(stats_window, text=f"{statistic}: {stats[statistic]}", width=20, anchor=tk.W).grid(row=i)
  
      # Refresh button to refresh stats again - outputted a row after the stats
      tk.Button(stats_window, text="Refresh", command=stats_update).grid(row=i + 1)

    # New top level window 
    stats_window = tk.Toplevel()
    stats_window.title("Stats")
    stats_window.attributes("-topmost", True)
    stats_window.resizable(height=False, width=False)
    stats_update()

  def time_between(self, event_time, end_time):
    """ Returns the time passed for an event time in hours, seconds and minutes, given times in seconds."""
    # Time passed in seconds
    seconds = round(end_time - event_time)

    # Conversion to hours, seconds and minutes 
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    return f"{hours:02}:{minutes:02}:{seconds:02}"  
    
  def new_game(self, difficulty):
    """ Creates a new minesweeper game."""
    # Updates wins and losses (if previous game was completed)
    self.update_wins()
    
    # Clears game frame
    self.game_frame.pack_forget()

    # Creates new game frame with new board
    self.game_frame = tk.Frame(self.window)
    self.board = NewBoard(difficulty, self.game_frame)
    self.game_frame.pack() 

    # Changes window title
    self.set_title()

  def load_game(self):
    """ Loads a game (board) from a file."""
    # Creates new game frame with new board
    new_frame = tk.Frame(self.window)
    new_board = LoadBoard(new_frame)

    # If loading failed
    # No error message as that is handled in LoadBoard
    if not new_board.loaded:
      return
    
    # Updates wins and losses (if previous game was completed)
    self.update_wins()
    
    # Clears old game frame
    self.game_frame.pack_forget()

    # Starts new game with loaded board
    self.game_frame = new_frame
    self.board = new_board
    self.game_frame.pack() 
    self.set_title()
    
  def save_game(self):
    """ Saves current game to a text file."""
    # If the game hasn't started (no bombs generated yet), or is finished, error
    if not self.board.clicked:
      messagebox.showerror(title="Game Not Started", message="Cannot save game that has not begun.")
      return

    if not self.board.running:
      messagebox.showerror(title="Game Over", message="Cannot save game that has completed.")
      return
    
    # Creates save file (.txt)
    save_file = filedialog.asksaveasfile(defaultextension=".json", filetypes=[("JSON File", ".json")])
    if save_file == None:
      return
    
    try:
      # Gets board object without frame 
      board_vars = vars(self.board)
      temp_frame = board_vars.pop("frame")
      
      # Writes to the save_file
      json.dump(board_vars, save_file)
      save_file.close()

      # Adds frame again
      board_vars["frame"] = temp_frame

    # If the file isn't saved, show an error message
    except TypeError:
      messagebox.showerror(title="File Error", message="Could not save data to save file.")

  def settings_menu(self):
    """ Settings window from menubar."""
    # New top level window 
    settings_window = tk.Toplevel()
    settings_window.title("Settings")
    settings_window.resizable(height=False, width=False)

    # Settings notebook (tabs)
    settings = ttk.Notebook(settings_window)

    # Appearance settings
    appearance_settings = tk.Frame(settings)
    settings.add(appearance_settings, text="Appearance")
    self.appearance_settings(appearance_settings)
  
    # Game settings
    game_settings = tk.Frame(settings)
    settings.add(game_settings, text="Game")
    self.game_settings(game_settings)

    # Packs the settings notebook
    settings.pack()

  def settings_title(self, frame, text):
    """ Returns a generic settings title."""
    return tk.Label(frame, text=text, font=("Arial", 15))

  def settings_header(self, frame, text):
    """ Returns a generic settings header."""
    return tk.Label(frame, text=text, anchor=tk.W, width=15)
    
  def appearance_settings(self, frame):
    """ Apperance settings in settings window."""

    def change_colour(colour_attribute):
      """ Changes color in board class based on users choice, given the changed attribute."""
      new_colour = colorchooser.askcolor(self.board.colours[colour_attribute])
      Board.colours[colour_attribute] = new_colour[1]
      self.board.output_board()

    def apply_height(new_height):
      """ Applies changes to height."""
      self.board.square_dimensions[0] = new_height
      self.board.output_board()
      
    def apply_width(new_width):
      """ Applies changes to width."""
      self.board.square_dimensions[1] = new_width
      self.board.output_board()

    def set_default_colours():
      """ Reverts to default colours (calls classmethod)."""
      Board.set_default_colours()
      self.board.output_board() 
      
    # Colours title
    self.settings_title(frame, "Colours").grid(row=0, columnspan=2)
    
    # For every color option on the board, give the user a color editor to edit it
    for i, colour in enumerate(self.board.colours, start=1):
      label_text = colour.capitalize() + ":"
      tk.Label(frame, text=label_text, anchor=tk.W, width=15).grid(row=i)
      tk.Button(frame, text="Choose Colour", width=15, command=
                lambda attribute=colour: change_colour(attribute)).grid(row=i, column=1)

    # Button to revert to default colours
    tk.Button(frame, text="Default Colours", width=15, 
              command=set_default_colours).grid(row=i + 1, columnspan=2)

    # Size title (with new line before)
    self.settings_title(frame, "\nGame Size").grid(row=i + 2, columnspan=2)

    # Height scale
    self.settings_header(frame, "Height:").grid(row=i + 3)
    height_scale = tk.Scale(frame,
                            from_=1, 
                            to=5,
                            orient=tk.HORIZONTAL,
                            command=apply_height)
    height_scale.set(self.board.square_dimensions[0])
    height_scale.grid(row=i + 4, columnspan=2)
 
    # Width scale
    self.settings_header(frame, "Width:").grid(row=i + 5)
    width_scale = tk.Scale(frame,
                           from_=1, 
                           to=5,
                           orient=tk.HORIZONTAL,
                           command=apply_width)
    width_scale.set(self.board.square_dimensions[1])
    width_scale.grid(row=i + 6, columnspan=2)

  def game_settings(self, frame):
    """ Game settings in settings window."""

    def validate_int(text_input):
      """ Returns true if text_input is an int (or empty)."""
      if text_input.isdigit() or text_input == "":
        return True
      return False

    def save_changes():
      """ Validates users input to bomb entry field."""
      # Dimensions and bomb variables
      rows = row_count.get()
      columns = column_count.get()
      bombs = int(bomb_input.get())
      
      # There can't be more bombs than validsquares 
      # The game must uncover 4 to 9 squares minimum on first click 
      # This is because the bomb generation ensures the first uncover is always 0
      max_bombs = max(0, rows * columns - 9)

      if bombs > max_bombs:
        messagebox.showerror(title="Invalid bomb count", message="Bomb count cannot be higher than square count minus nine.")
        return

      # A board needs at least one bomb 
      if bombs < 1:
        messagebox.showerror(title="Invalid bomb count", message="Board must contain at least one bomb.")
        return

      # The user is already in a custom game, ask them if they would like to create a new game.
      new_game = False
      if self.board.game_difficulty == "custom":
        if messagebox.askokcancel(title="Currently in Custom game", message="You are currently in a custom game. Create new game?"):
          new_game = True
        else:
          return
          
      # Applies dimensions and bomb_count
      self.board.difficulties["custom"]["board_size"][0] = rows
      self.board.difficulties["custom"]["board_size"][1] = columns
      self.board.difficulties["custom"]["bomb_count"] = bombs

      # Creates new game if user was in custom
      if new_game:
        self.new_game("custom")

    # Max board dimensions
    MAX_ROWS = 20
    MAX_COLUMNS = 40
    
    # Custom difficulty editor
    self.settings_title(frame, "Custom Difficulty").grid(row=0, columnspan=2)

    # Rows
    self.settings_header(frame, "Rows:").grid(row=1)
    row_count = tk.Scale(frame,
                         from_=1, 
                         to=MAX_ROWS,
                         orient=tk.HORIZONTAL,)
    row_count.set(self.board.difficulties["custom"]["board_size"][0])
    row_count.grid(row=1, column=2)

    # Columns
    self.settings_header(frame, "Columns:").grid(row=2)
    column_count = tk.Scale(frame,
                         from_=1, 
                         to=MAX_COLUMNS,
                         orient=tk.HORIZONTAL,)
    column_count.set(self.board.difficulties["custom"]["board_size"][1])
    column_count.grid(row=2, column=2)

    # Bombs
    # Frame for the text entry area
    text_frame = tk.Frame(frame, height=20, width=40)
    text_frame.pack_propagate(0)
    text_frame.grid(row=3, column=2)

    # Validation command
    validation_cmd = text_frame.register(validate_int)

    # Bomb count text entry area
    self.settings_header(frame, "Bombs:").grid(row=3)
    bomb_input = tk.Entry(text_frame, validate="key", validatecommand=(validation_cmd, '%P'))
    bomb_input.insert(0, self.board.difficulties["custom"]["bomb_count"])
    bomb_input.pack()

    # Submit button
    tk.Button(frame, text="Save Changes", width=10, command=save_changes).grid(row=4, columnspan=3)
    
  def update_wins(self):
    """ Updates wins and loss counts in stats."""
    # Updates win/loss count based on game_won value
    if self.board.game_won:
      self.win_count += 1
    elif self.board.game_won == False:
      self.loss_count += 1

    # Reverts game_won back to None - Win/Loss counts will never update again for this board instance
    self.board.game_won = None 