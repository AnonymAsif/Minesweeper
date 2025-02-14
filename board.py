_author_ = "Asif Rahman"
_date_ = "Thursday, May 26, 2022"
_version_ = "1.0"
_filename_ = "board.py"
_description_ = "Minesweeper Board classes. Handles game processes. NewBoard creates a new board, LoadBoard loads one from a file."

import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from copy import deepcopy
import json
import random
import time


class Board:
  """ Minesweeper board."""
  # Board symbols
  BOMB_IDENTIFIER = "⬤"
  FLAG_SYMBOL = "⚑"
  INCORRECT_FLAG_SYMBOL = "X"

  # Default size of each square (height, width)
  square_dimensions = [2, 4]

  # Square states and difficulty options
  state_options = ("covered", "uncovered", "flagged", "incorrect_flagged")
  difficulties = {
    "easy" : {
      "board_size" : (8,8),
      "bomb_count" : 10,
    },
  
    "intermediate" : {
      "board_size" : (16,16),
      "bomb_count" : 40,
    },
  
    "expert" : {
      "board_size" : (16,30),
      "bomb_count" : 99,
    } ,
    
    "custom" : {
      "board_size" : [10,10],
      "bomb_count" : 30,
    }
  }

  # Colors for the board (deep copy allows reversion to default colours)
  default_colours = {
    "background" : "#adadad",
    "square" : "#bfbfbf",
    "flag" : "#ff0000",
    "text" : "#000000" 
  }
  
  colours = deepcopy(default_colours)

  @classmethod
  def set_default_colours(cls):
    """Sets board colours back to default."""
    cls.colours = deepcopy(cls.default_colours)
  
  def move(self, new_state, square):
    """ Changes the state of the given square if it's a legal move."""
    # If the game is over 
    if not self.running:
      return
    
    # To uncover a square - only works if previously covered
    if self.states[square[0]][square[1]] == self.state_options[0] and new_state == self.state_options[1]:

      # If it's the first uncovering click of a new board - place bombs 
      if not self.clicked:
        self.place_bombs(square) 
        self.place_bomb_counts()
        self.clicked = True

      # Uncovers square
      self.states[square[0]][square[1]] = self.state_options[1]
      self.uncover_count -= 1

      # If it's a bomb, end game, 
      if self.board[square[0]][square[1]] == self.BOMB_IDENTIFIER:
        self.end_game(False)
      
      # Not a bomb
      else:
        # If the uncovered square was a zero, uncover surroundings
        if self.board[square[0]][square[1]] == 0:
          self.uncover_zeros(square, set())  
  
        # If all squares are uncovered, end game.
        if self.uncover_count == 0:
          self.end_game(True)       

    # To flag a square
    if new_state == self.state_options[2]:
      
      # If it's covered, flag it
      if self.states[square[0]][square[1]] == self.state_options[0]:
        self.states[square[0]][square[1]] = self.state_options[2]
        self.flag_count -= 1

        # Warns user if they no longer have flags
        if self.flag_count == -1:
          messagebox.showwarning(title="Flags Exceeded", message="Number of flags exceeded.")

      # If it's flagged, cover it (remove flag) 
      elif self.states[square[0]][square[1]] == self.state_options[2]:
        self.states[square[0]][square[1]] = self.state_options[0]
        self.flag_count += 1

    # Outputs the square at the end of the move
    self.output_square(square[0], square[1])
    
  def uncover_zeros(self, move, recursed_set):
    """ Given the index of a zero on the board, uncovers all zeros that surround it."""
    # Adds the move to a recursed set - avoids infinite recursion
    recursed_set.add(move)
  
    # For the 3 rows before, after, and including the index
    for i in range(move[0] - 1, move[0] + 2):
  
      # If the row is out of bounds
      if i < 0 or i >= self.board_size[0]:
        continue
      
      # For the 3 columns before, after, and including the index
      for j in range(move[1] - 1, move[1] + 2):
  
        # If the column is out of bounds.
        if j < 0 or j >= self.board_size[1]:
          continue
          
        # If there is a zero surrounding the zero, call uncover_zeros again
        if self.board[i][j] == 0 and (i,j) not in recursed_set:
          self.uncover_zeros((i, j), recursed_set)
  
        # Uncover the square
        if self.states[i][j] != self.state_options[1]:
          
          # If the uncovered square was a flag, increase remaining flags by one
          if self.states[i][j] == self.state_options[2]:
            self.flag_count += 1 
          
          self.states[i][j] = self.state_options[1]
          self.uncover_count -= 1

          # Update it
          self.output_square(i,j)
    
  def output_square(self, row, column):
    """ Outputs the given square (in frame)."""
    BORDER = 2
    TEXT_FONT = ("Roboto", 8, "bold")
    
    # If it is covered, output a blank sqaure
    if self.states[row][column] == self.state_options[0]:
      label = tk.Label(self.frame,
                       relief=tk.RAISED,
                       cursor="dotbox",
                       height=self.square_dimensions[0], 
                       width=self.square_dimensions[1], 
                       bd=BORDER,
                       bg=self.colours["square"])

      # Left-click - uncover square, Right-click - flag square
      label.bind("<Button-1>", lambda event: self.move(self.state_options[1], (row, column)))
      label.bind("<Button-3>", lambda event: self.move(self.state_options[2], (row, column)))
      
    # If it's uncovered, output the number. 
    elif self.states[row][column] == self.state_options[1]:

      # Makes zeros blank
      if self.board[row][column] == 0:
        uncovered_text = ""
      else:
        uncovered_text = self.board[row][column]
      
      label = tk.Label(self.frame, 
                       text=uncovered_text, 
                       relief=tk.SUNKEN, 
                       font=TEXT_FONT, 
                       height=self.square_dimensions[0], 
                       width=self.square_dimensions[1], 
                       bd=BORDER,
                       bg=self.colours["background"],
                       fg=self.colours["text"])
      
    # If it's' flagged, output a flag
    elif self.states[row][column] == self.state_options[2]:
      label = tk.Label(self.frame, 
                       text=self.FLAG_SYMBOL, 
                       relief=tk.RAISED, 
                       font=TEXT_FONT,
                       height=self.square_dimensions[0], 
                       width=self.square_dimensions[1],
                       bd=BORDER,
                       bg=self.colours["square"],
                       fg=self.colours["flag"])
      
      # Right-click - unflag square
      label.bind("<Button-3>", lambda event: self.move(self.state_options[2], (row, column))) 
      
    # If the square is incorrectly flagged (revealed on death)
    else:
      label = tk.Label(self.frame, 
                       text=self.INCORRECT_FLAG_SYMBOL, 
                       relief=tk.RAISED, 
                       font=TEXT_FONT,
                       height=self.square_dimensions[0], 
                       width=self.square_dimensions[1],
                       bd=BORDER,
                       bg=self.colours["square"],
                       fg=self.colours["flag"])

    # Outputs the square
    label.grid(row=row, column=column)

  def output_board(self):
    """ Outputs the entire board."""
    # Clears the old frame
    for widget in self.frame.winfo_children():
      widget.destroy()

    # Outputs updated squares
    for i in range(self.board_size[0]): 
      for j in range(self.board_size[1]):
        self.output_square(i, j)
    
  def end_game(self, is_win):
    """ Reveals the bombs to the player and ends the game."""
    # Ends game 
    self.running = False
    self.game_won = is_win
    self.end_time = time.time()
  
    # Prints game end message
    if is_win:
      messagebox.showinfo(title="Nice Job!", message="You won!\nSee stats for stats")
    else:
      messagebox.showerror(title="Close One!", message="You blew up!\nSee stats for stats")

      # Uncovers all remaining bombs and removes incorrect flags
      for i in range(self.board_size[0]):
        for j in range(self.board_size[1]):
  
          # If the bomb is covered, uncover it and output it
          if self.board[i][j] == self.BOMB_IDENTIFIER:
            if self.states[i][j] == self.state_options[0]:
              self.states[i][j] = self.state_options[1]
              self.output_square(i, j)

          # If a non-bomb is flagged, cover it
          elif self.states[i][j] == self.state_options[2]:
            self.states[i][j] = self.state_options[3]
            self.output_square(i, j)


class NewBoard(Board):
  """ Creates a new Minesweeper board using the Board class."""
  
  def __init__(self, difficulty, frame):
    """ Sets up board and board variables."""
    # Booleans for significant events
    self.running = True
    self.clicked = False
    self.game_won = None

    # Board variables 
    self.game_difficulty = difficulty
    self.board_size = self.difficulties[self.game_difficulty]["board_size"]
    self.bomb_count = self.difficulties[self.game_difficulty]["bomb_count"]
    self.flag_count = self.bomb_count

    # Non-bombs left to uncover
    self.uncover_count = self.board_size[0] * self.board_size[1] - self.bomb_count 

    # Board setup
    self.frame = frame
    self.states = self.default_states()
    self.board = self.empty_board()

    # Outputs board for the first time
    self.output_board()

    # Gets start time of game
    self.start_time = time.time()
    self.end_time = None
    

  def empty_board(self):
    """ Returns an empty 2D list with given dimensions."""
    board = []
    
    # For each row
    for i in range(self.board_size[0]):
      row = []
      
      # For each column
      for j in range(self.board_size[1]):
        row.append(None)
      board.append(row)
    
    return board

  def default_states(self):
    """ Returns a 2D dictionary with dimensions of board_size with all values set to covered."""
    states = {}
  
    # For each row
    for i in range(self.board_size[0]):
      states[i] = {}
      
      # For each column
      for j in range(self.board_size[1]):
        states[i][j] = self.state_options[0]
        
    return states

  def place_bombs(self, square):
    """ Places bomb_count bombs in the empty board."""

    # Gets list of squares around the first clicked square
    bomb_free_zone = [] 
    for i in range(square[0] - 1, square[0] + 2):
      for j in range(square[1] - 1, square[1] + 2):
        bomb_free_zone.append((i,j))

    # Gets list of all squares that are eligible to have a bomb(not in bomb_free_zone)
    bomb_eligible_squares = []
    for i in range(self.board_size[0]):
      for j in range(self.board_size[1]):
        if (i,j) not in bomb_free_zone:
          bomb_eligible_squares.append((i,j))

    # Places bombs 
    for i in range(self.bomb_count):
      
      # Gets a random index in bomb_eligible_squares and removes it
      index = random.randrange(len(bomb_eligible_squares))
      square = bomb_eligible_squares.pop(index)

      # Assigns a bomb to that square on the board
      self.board[square[0]][square[1]] = self.BOMB_IDENTIFIER
    
  def get_surrounding_bombs(self, row, column):
    """ Gets the surrounding bomb count for a given index."""
    bomb_count = 0
    
    # For the 3 rows before, after, and including the index
    for i in range(row - 1, row + 2):
  
      # If the row is out of bounds
      if i < 0 or i >= self.board_size[0]:
        continue
      
      # For the 3 columns before, after, and including the index
      for j in range(column - 1, column + 2):
  
        # If the column is out of bounds
        if j < 0 or j >= self.board_size[1]:
          continue
  
        # If a bomb is found, increment bomb_count
        if self.board[i][j] == self.BOMB_IDENTIFIER:
          bomb_count += 1
        
    return bomb_count
    
  def place_bomb_counts(self):
    """ All non bombs on the board are replaced with their surrounding bomb count."""
    # For each row
    for i in range(self.board_size[0]):
  
      # For each column
      for j in range(self.board_size[1]):
        
        if self.board[i][j] != self.BOMB_IDENTIFIER:
          self.board[i][j] = self.get_surrounding_bombs(i, j)

class LoadBoard(Board):
  """ Loads a Board from a file into an object."""
  
  def __init__(self, frame):
    """ Gets board data from file."""
    # Identifies when the board has been successfully loaded 
    self.loaded = False

    # Tkinter Frame
    self.frame = frame 
    
    # Opens file
    with filedialog.askopenfile(filetypes=[("JSON Files", ".json")]) as save_file:
      if save_file == None:
        return

      # Converts JSON file data
      try:
        save_data = json.load(save_file)

      # Invalid data in JSON file
      except json.decoder.JSONDecodeError:
        self.file_error()
        return

    # JSON Module converts dict keys to strings
    # The states dictionary keys need to be converted back to integers to allow indexing
    # Copies every key/value from save_data into new_states but with integer typed keys
    try:
      new_states = {}
      for row in save_data["states"]:
        new_states[int(row)] = {}
        
        for square in save_data["states"][row]:
          new_states[int(row)][int(square)] = save_data["states"][row][square]
  
      # Replaces old states with new states (with integer typed keys) 
      save_data["states"] = new_states

    # One of the keys was not an integer
    except ValueError:
      self.file_error()
      return

    # If the data is valid JSON but not a valid board
    if not self.data_verification(save_data):
      self.file_error()
      return
      
    # Loads sava data into board
    self.__dict__.update(save_data)

    # Initial board output
    self.output_board()
    self.loaded = True

  def data_verification(self, save_data):
    """ Verifies the data from JSON file."""

    def check_types(types):
      """ Verifies that the keys and values in the dictionary type are valid."""
      for data_type, data_list in types.items():
        for variable in data_list:
          if type(data_type) is not type(variable):
            return False
      return True
    
    # Variables that should be the correct type corresponding to their list
    # The keys have a value of the their respective type
    try:
      types = {
      2 : [save_data["bomb_count"], save_data["flag_count"], save_data["uncover_count"]],
      3.0 : [save_data["start_time"]],
      True : [save_data["running"], save_data["clicked"]],
      None : [save_data["game_won"], save_data["end_time"]]
      }

      # Checks all other necessary keys by assigning them
      board_size = save_data["board_size"]
      difficulty = save_data["game_difficulty"]
      states = save_data["states"] 
      board = save_data["board"]

    # The keys are not in the save file
    except KeyError: 
      return False

    # Checks difficulty
    if difficulty not in self.difficulties:
      return False

    # Checks board_size, if valid add the dimensions to should-be ints
    if len(board_size) == 2:
      for dimension in board_size:
        types[2].append(dimension)
        
    else:
      return False
      
    # Checks states - keys should be board size and values should be in state options
    # Checks board - should contain ints (surrounding bomb count) or bomb identifier
    for i in range(board_size[0]):
      for j in range(board_size[1]):
        
        try: # Checks if the state is valid
          if states[i][j] not in self.state_options:
            return False
        except KeyError: # If the dict does not have [i][j] as a valid key (wrong size)
          return False
        
        try: # If the square is valid and not a bomb, it should be an int
          if board[i][j] != self.BOMB_IDENTIFIER:
            types[2].append(board[i][j])           
        except IndexError: # If the list does not have index [i][j] (wrong size)
          return False

    # Checks the types of all the variables
    if not check_types(types):
      return False
      
    return True

  def file_error(self):
    """ Outputs an error messagebox for file errors. """
    messagebox.showerror(title="File Error", message="Invalid data. Please check your save file.")