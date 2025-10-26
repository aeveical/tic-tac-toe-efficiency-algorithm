"""
Tic Tac Toe - Human vs Computer AI

A graphical tic-tac-toe game implemented using tkinter where a human player
competes against an AI opponent. The AI uses the minimax algorithm with
alpha-beta pruning to make optimal moves.
"""

import tkinter as tk
from tkinter import messagebox


class TicTacToe:
    """
    A Tic Tac Toe game with AI opponent using minimax algorithm.

    This class implements a complete tic-tac-toe game where a human player (X)
    competes against an unbeatable AI opponent (O). The AI uses the minimax
    algorithm with alpha-beta pruning to calculate the optimal move.

    Attributes:
        window (tk.Tk): The main GUI window
        current_player (str): The current player ('X' or 'O')
        human_player (str): Symbol for human player ('X')
        computer_player (str): Symbol for computer player ('O')
        board (list): 3x3 list representing the game board
        buttons (list): 3x3 list of tkinter Button objects for the GUI
    """

    def __init__(self):
        """
        Initialize the Tic Tac Toe game.

        Sets up the main game window, initializes the game state, and creates
        the 3x3 grid of buttons for the game board. The human player always
        starts first with 'X' symbol.

        Creates:
            - Main tkinter window with title
            - 3x3 grid of clickable buttons
            - Initial empty game board
            - Player assignments (human=X, computer=O)
        """
        self.window = tk.Tk()
        self.window.title("Tic Tac Toe - Human vs Computer")
        self.current_player = "X"
        self.human_player = "X"
        self.computer_player = "O"
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]

        for i in range(3):
            for j in range(3):
                self.buttons[i][j] = tk.Button(
                    self.window,
                    text=" ",
                    font=("Arial", 20),
                    width=10,
                    height=5,
                    command=lambda row=i, col=j: self.on_button_click(row, col),
                )
                self.buttons[i][j].grid(row=i, column=j)

    def on_button_click(self, row, col):
        """
        Handle human player button clicks.

        This method is called when a human player clicks on a button in the grid.
        It validates the move, updates the board, checks for game end conditions,
        and triggers the computer's turn if the game continues.

        Args:
            row (int): The row index of the clicked button (0-2)
            col (int): The column index of the clicked button (0-2)
        """
        # Only allow human player to click buttons
        if self.current_player == self.human_player and self.board[row][col] == " ":
            # Human move
            self.board[row][col] = self.human_player
            self.buttons[row][col]["text"] = self.human_player

            if self.check_winner():
                self.show_winner_message()
                self.reset_game()
            elif self.check_draw():
                self.show_draw_message()
                self.reset_game()
            else:
                self.switch_player()
                # Trigger computer move after a short delay for better UX
                self.window.after(500, self.make_computer_move)

    def check_winner(self):
        """
        Check if there's a winner in the current game state.

        Examines all possible winning conditions: rows, columns, and diagonals
        to determine if any player has achieved three in a row.

        Returns:
            bool: True if there's a winner, False otherwise
        """
        # Check rows
        for row in self.board:
            if row[0] == row[1] == row[2] != " ":
                return True

        # Check columns
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != " ":
                return True

        # Check diagonals
        if (
            self.board[0][0] == self.board[1][1] == self.board[2][2] != " "
            or self.board[0][2] == self.board[1][1] == self.board[2][0] != " "
        ):
            return True

        return False

    def show_winner_message(self):
        """
        Display a message box announcing the winner.

        Shows a popup dialog with the current player as the winner.
        Called when a winning condition is detected.
        """
        messagebox.showinfo("Tic Tac Toe", f"Player {self.current_player} wins!")

    def check_draw(self):
        """
        Check if the game is a draw.

        A draw occurs when all board positions are filled and no player has won.

        Returns:
            bool: True if the game is a draw, False otherwise
        """
        for row in self.board:
            if " " in row:
                return False
        return True

    def show_draw_message(self):
        """
        Display a message box announcing a draw.

        Shows a popup dialog indicating that the game ended in a draw.
        Called when the board is full with no winner.
        """
        messagebox.showinfo("Tic Tac Toe", "It's a draw!")

    def minimax(self, board, depth, is_maximizing, alpha, beta):
        """
        Minimax algorithm with alpha-beta pruning for optimal move calculation.

        This is the core AI algorithm that evaluates all possible game states
        to find the optimal move. Alpha-beta pruning is used to eliminate
        branches that won't affect the final decision, improving efficiency.

        Args:
            board (list): 3x3 list representing the current board state
            depth (int): Current depth in the game tree (0 = current state)
            is_maximizing (bool): True if maximizing player (computer), False if minimizing (human)
            alpha (float): Best value the maximizing player can guarantee
            beta (float): Best value the minimizing player can guarantee

        Returns:
            int: The evaluation score for the current board state
                 Positive values favor the computer (O)
                 Negative values favor the human (X)
                 Zero indicates a draw
        """
        # Check terminal states
        winner = self.get_winner(board)
        if winner == "O":
            return 10 - depth
        elif winner == "X":
            return depth - 10
        elif self.is_board_full(board):
            return 0

        if is_maximizing:
            max_eval = float("-inf")
            for i in range(3):
                for j in range(3):
                    if board[i][j] == " ":
                        board[i][j] = "O"
                        eval_score = self.minimax(board, depth + 1, False, alpha, beta)
                        board[i][j] = " "
                        max_eval = max(max_eval, eval_score)
                        alpha = max(alpha, eval_score)
                        if beta <= alpha:
                            break
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float("inf")
            for i in range(3):
                for j in range(3):
                    if board[i][j] == " ":
                        board[i][j] = "X"
                        eval_score = self.minimax(board, depth + 1, True, alpha, beta)
                        board[i][j] = " "
                        min_eval = min(min_eval, eval_score)
                        beta = min(beta, eval_score)
                        if beta <= alpha:
                            break
                if beta <= alpha:
                    break
            return min_eval

    def get_best_move(self):
        """
        Find the best move for the computer using minimax with alpha-beta pruning.

        Iterates through all empty cells on the board and uses the minimax algorithm
        to evaluate each possible move. Returns the move that yields the highest score
        for the computer player.

        Returns:
            tuple: (row, col) coordinates of the best move, or None if no moves available
        """
        best_score = float("-inf")
        best_move = None

        for i in range(3):
            for j in range(3):
                if self.board[i][j] == " ":
                    self.board[i][j] = "O"
                    score = self.minimax(
                        self.board, 0, False, float("-inf"), float("inf")
                    )
                    self.board[i][j] = " "  # Undo move

                    if score > best_score:
                        best_score = score
                        best_move = (i, j)

        return best_move

    def get_winner(self, board):
        """
        Check if there's a winner on the given board state.

        This is a helper method used by the minimax algorithm to evaluate
        board positions. It checks all winning conditions without modifying
        the actual game state.

        Args:
            board (list): 3x3 list representing a board state to check

        Returns:
            str or None: 'X' if X wins, 'O' if O wins, None if no winner
        """
        # Check rows
        for row in board:
            if row[0] == row[1] == row[2] != " ":
                return row[0]

        # Check columns
        for col in range(3):
            if board[0][col] == board[1][col] == board[2][col] != " ":
                return board[0][col]

        # Check diagonals
        if board[0][0] == board[1][1] == board[2][2] != " ":
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] != " ":
            return board[0][2]

        return None

    def is_board_full(self, board):
        """
        Check if the board is completely filled.

        This helper method is used by the minimax algorithm to detect
        terminal states where no more moves can be made.

        Args:
            board (list): 3x3 list representing the board state to check

        Returns:
            bool: True if all positions are filled, False otherwise
        """
        for row in board:
            if " " in row:
                return False
        return True

    def make_computer_move(self):
        """
        Make the computer's move using the minimax algorithm.

        This method is called automatically after the human player makes a move.
        It uses the minimax algorithm to find the optimal move, updates the board
        and UI, then checks for game end conditions.
        """
        if (
            self.current_player == self.computer_player
            and not self.check_winner()
            and not self.check_draw()
        ):
            move = self.get_best_move()
            if move:
                row, col = move
                self.board[row][col] = self.computer_player
                self.buttons[row][col]["text"] = self.computer_player

                if self.check_winner():
                    self.show_winner_message()
                    self.reset_game()
                elif self.check_draw():
                    self.show_draw_message()
                    self.reset_game()
                else:
                    self.switch_player()

    def switch_player(self):
        """
        Switch between human and computer players.

        Toggles the current_player between human ('X') and computer ('O').
        This method is called after each successful move to alternate turns.
        """
        if self.current_player == self.human_player:
            self.current_player = self.computer_player
        else:
            self.current_player = self.human_player

    def reset_game(self):
        """
        Reset the game to initial state.

        Clears the board, resets all button displays, and sets the human
        player to go first. This method is called automatically after
        each game ends (win or draw).
        """
        self.current_player = self.human_player
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                self.buttons[i][j]["text"] = " "

    def run(self):
        """
        Start the game by launching the tkinter main event loop.

        This method should be called to begin the game. It starts the
        GUI event loop and keeps the window open for user interaction.
        """
        self.window.mainloop()


if __name__ == "__main__":
    game = TicTacToe()
    game.run()
