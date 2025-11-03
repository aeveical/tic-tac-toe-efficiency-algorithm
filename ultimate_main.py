"""
Tic Tac Toe - Human vs Computer AI

A graphical tic-tac-toe game implemented using tkinter where a human player
competes against an AI opponent. The AI uses the minimax algorithm with
alpha-beta pruning to make optimal moves.
"""

import tkinter as tk
from tkinter import messagebox
import copy
from functools import partial


class UltimateTicTacToeBoard:
    """
    Ultimate Tic-Tac-Toe game board with AI opponent.

    This class implements the complete game logic for Ultimate Tic-Tac-Toe,
    a variant where players must win small 3x3 boards to control positions
    in a larger 3x3 grid. The AI uses minimax with alpha-beta pruning and
    supports multiple difficulty levels.

    Attributes:
        EMPTY_CELL (str): Symbol for empty cells (" ")
        TIE_CELL (str): Symbol for tied small boards ("T")
        PLAYER_X (str): Symbol for player X
        PLAYER_O (str): Symbol for player O
        human_player (str): Symbol assigned to human player
        computer_player (str): Symbol assigned to AI player
        current_player (str): Currently active player
        difficulty (str): AI difficulty level ("easy", "medium", "hard")
        weights (dict): Evaluation weights based on difficulty
        search_depth (int): Search depth for minimax algorithm
        grand_board (list): 3x3 grid tracking small board winners
        boards (list): 3x3x3x3 grid of all small board cells
        next_board_coords (tuple): Coordinates of required next board
    """

    EMPTY_CELL = " "
    TIE_CELL = "T"
    PLAYER_X = "X"
    PLAYER_O = "O"

    def __init__(self, human_marker=PLAYER_X, difficulty="hard"):
        # default is x for human player and y for bot

        self.human_player = human_marker
        self.computer_player = (
            self.PLAYER_O if human_marker == self.PLAYER_X else self.PLAYER_X
        )

        self.current_player = self.PLAYER_X
        self.difficulty = difficulty.lower()

        # Set weights based on difficulty level
        self._set_difficulty_weights()

        self.grand_board = [[self.EMPTY_CELL for _ in range(3)] for _ in range(3)]

        self.boards = []
        for _ in range(3):
            board_row = []
            for _ in range(3):

                small_board = [[self.EMPTY_CELL for _ in range(3)] for _ in range(3)]
                board_row.append(small_board)
            self.boards.append(board_row)

        self.next_board_coords = None

    def _set_difficulty_weights(self):
        """
        Set evaluation weights based on difficulty level.

        Easy: Suboptimal weights that make the AI play poorly
        Medium: Moderately good weights
        Hard: Optimal weights for best play
        """
        if self.difficulty == "easy":
            self.weights = {
                "grand_win": 50000,
                "grand_line_two": 20,
                "grand_line_one": 2,
                "small_board_win": 10,
                "small_line_two": 1,
                "small_line_one": 0.2,
                "center_bonus": 2,
                "randomness": 0.3,
            }
            self.search_depth = 2
        elif self.difficulty == "medium":
            self.weights = {
                "grand_win": 75000,
                "grand_line_two": 60,
                "grand_line_one": 60,
                "small_board_win": 30,
                "small_line_two": 3,
                "small_line_one": 3,
                "center_bonus": 6,
                "randomness": 0.1,
            }
            self.search_depth = 3
        else:
            self.weights = {
                "grand_win": 100000,
                "grand_line_two": 100,
                "grand_line_one": 100,
                "small_board_win": 50,
                "small_line_two": 5,
                "small_line_one": 5,
                "center_bonus": 10,
                "randomness": 0,
            }
            self.search_depth = 4

    def _check_win_3x3(self, board):
        """
        Check if there's a winner in a 3x3 board.

        Examines rows, columns, and diagonals to determine if any player
        has achieved three in a row in the given 3x3 board.

        Args:
            board (list): 3x3 list representing a small board or grand board

        Returns:
            str or None: Player symbol ('X' or 'O') if there's a winner, None otherwise
        """
        for player in [self.PLAYER_X, self.PLAYER_O]:

            for row in board:
                if row.count(player) == 3:
                    return player

            for col in range(3):
                if board[0][col] == board[1][col] == board[2][col] == player:
                    return player

            if board[0][0] == board[1][1] == board[2][2] == player:
                return player
            if board[0][2] == board[1][1] == board[2][0] == player:
                return player
        return None

    def _is_board_full_3x3(self, board):
        """
        Check if a 3x3 board is completely filled.

        Determines whether all cells in a 3x3 board contain player symbols
        (no empty cells remaining).

        Args:
            board (list): 3x3 list representing a board to check

        Returns:
            bool: True if all cells are filled, False if any empty cells remain
        """
        for row in board:
            if self.EMPTY_CELL in row:
                return False
        return True

    def deep_copy(self):
        """
        Create a deep copy of the game board.

        Creates a complete copy of the current game state including all boards,
        player assignments, difficulty settings, and game progress. Used by
        the minimax algorithm to simulate moves without affecting the actual game.

        Returns:
            UltimateTicTacToeBoard: A new board instance with identical state
        """
        new_board = UltimateTicTacToeBoard(
            human_marker=self.human_player, difficulty=self.difficulty
        )
        new_board.grand_board = copy.deepcopy(self.grand_board)
        new_board.boards = copy.deepcopy(self.boards)
        new_board.next_board_coords = self.next_board_coords
        new_board.current_player = self.current_player
        return new_board

    def _check_small_board_win(self, br, bc):
        """
        Check if a small board has been won or tied.

        Examines a specific small board to determine if it has been won
        by either player or if it's completely filled (tie).

        Args:
            br (int): Board row coordinate (0-2)
            bc (int): Board column coordinate (0-2)

        Returns:
            str or None: Player symbol if won, 'T' if tied, None if still active
        """
        small_board = self.boards[br][bc]
        winner = self._check_win_3x3(small_board)

        if winner:
            return winner
        elif self._is_board_full_3x3(small_board):
            return self.TIE_CELL

        return None

    def make_move(self, board_r, board_c, cell_r, cell_c):
        """
        Execute a move on the game board.

        Places the current player's symbol in the specified cell and updates
        the game state. Checks for small board completion, updates the grand
        board if necessary, determines the next required board, and switches
        to the next player.

        Args:
            board_r (int): Small board row coordinate (0-2)
            board_c (int): Small board column coordinate (0-2)
            cell_r (int): Cell row within the small board (0-2)
            cell_c (int): Cell column within the small board (0-2)

        Returns:
            bool: True if the small board status changed (won/tied), False otherwise
        """
        player = self.current_player

        self.boards[board_r][board_c][cell_r][cell_c] = player

        small_board_status_before = self.grand_board[board_r][board_c]
        if small_board_status_before == self.EMPTY_CELL:
            winner_or_tie = self._check_small_board_win(board_r, board_c)
            if winner_or_tie:
                self.grand_board[board_r][board_c] = winner_or_tie

        self.next_board_coords = (cell_r, cell_c)

        self.current_player = (
            self.PLAYER_O if self.current_player == self.PLAYER_X else self.PLAYER_X
        )

        return small_board_status_before != self.grand_board[board_r][board_c]

    def get_legal_moves(self):
        """
        Get all legal moves in the current game state.

        Determines which cells can be legally played based on Ultimate Tic-Tac-Toe
        rules. If a specific small board is required (based on last move), only
        moves in that board are legal. If the required board is completed or full,
        any move in any active small board is legal.

        Returns:
            list: List of tuples (board_r, board_c, cell_r, cell_c) representing
                  all legal moves in the current position
        """
        moves = []
        required_br, required_bc = self.next_board_coords or (None, None)

        is_required_board_active = (
            required_br is not None
            and self.grand_board[required_br][required_bc] == self.EMPTY_CELL
        )

        if is_required_board_active:
            for cell_r in range(3):
                for cell_c in range(3):
                    if (
                        self.boards[required_br][required_bc][cell_r][cell_c]
                        == self.EMPTY_CELL
                    ):
                        moves.append((required_br, required_bc, cell_r, cell_c))

        if not is_required_board_active or not moves:
            for board_r in range(3):
                for board_c in range(3):

                    if self.grand_board[board_r][board_c] == self.EMPTY_CELL:
                        for cell_r in range(3):
                            for cell_c in range(3):
                                if (
                                    self.boards[board_r][board_c][cell_r][cell_c]
                                    == self.EMPTY_CELL
                                ):
                                    moves.append((board_r, board_c, cell_r, cell_c))

        return moves

    def check_grand_win(self):
        """
        Check if the game has ended (win or tie).

        Examines the grand board (3x3 grid of small board winners) to determine
        if any player has won the overall game by getting three small boards
        in a row, or if the game is a tie.

        Returns:
            str or None: Player symbol ('X' or 'O') if game won, 'T' if tie,
                        None if game is still ongoing
        """
        winner = self._check_win_3x3(self.grand_board)
        if winner:
            return winner

        is_grand_board_full = all(
            self.grand_board[r][c] != self.EMPTY_CELL
            for r in range(3)
            for c in range(3)
        )
        if is_grand_board_full:
            return self.TIE_CELL

        return None

    def _count_lines(self, board, player):
        """
        Count strategic line formations for a player on a 3x3 board.

        Evaluates rows, columns, and diagonals to count how many lines
        have potential for the specified player. Awards points for lines
        with 2 of the player's symbols (strong threat) and 1 symbol (potential).

        Args:
            board (list): 3x3 board to evaluate
            player (str): Player symbol to count lines for ('X' or 'O')

        Returns:
            int: Strategic score based on line formations
                 10 points per 2-in-a-row with 1 empty
                 1 point per 1-in-a-row with 2 empty
        """
        score = 0

        lines = []

        for i in range(3):
            lines.append([board[i][j] for j in range(3)])

        for j in range(3):
            lines.append([board[i][j] for i in range(3)])

        lines.append([board[i][i] for i in range(3)])
        lines.append([board[i][2 - i] for i in range(3)])

        for line in lines:
            player_count = line.count(player)
            empty_count = line.count(self.EMPTY_CELL)

            if player_count == 2 and empty_count == 1:
                score += 10

            elif player_count == 1 and empty_count == 2:
                score += 1

        return score

    def evaluate_board(self, board):
        """
        Evaluate board position using difficulty-based weights.

        Calculates a numerical score for the current board position from the
        computer's perspective. Uses different evaluation weights based on
        difficulty level to create varying AI strength.

        Args:
            board (UltimateTicTacToeBoard): Board position to evaluate

        Returns:
            int: Position evaluation score
                 Positive values favor the computer
                 Negative values favor the human
                 Zero indicates neutral/draw position
        """
        import random

        grand_winner = board.check_grand_win()
        if grand_winner == self.computer_player:
            return self.weights["grand_win"]
        if grand_winner == self.human_player:
            return -self.weights["grand_win"]
        if grand_winner == self.TIE_CELL:
            return 0

        score = 0

        # Grand board evaluation with difficulty-based weights
        score += (
            self._count_lines(board.grand_board, self.computer_player)
            * self.weights["grand_line_two"]
        )
        score -= (
            self._count_lines(board.grand_board, self.human_player)
            * self.weights["grand_line_two"]
        )

        # Small board evaluation
        for br in range(3):
            for bc in range(3):
                status = board.grand_board[br][bc]

                if status == self.computer_player:
                    score += self.weights["small_board_win"]
                elif status == self.human_player:
                    score -= self.weights["small_board_win"]
                elif status == self.EMPTY_CELL:
                    sub_score = (
                        self._count_lines(board.boards[br][bc], self.computer_player)
                        * self.weights["small_line_two"]
                    )
                    sub_score -= (
                        self._count_lines(board.boards[br][bc], self.human_player)
                        * self.weights["small_line_two"]
                    )
                    score += sub_score

        # Center control bonus
        if board.grand_board[1][1] == self.computer_player:
            score += self.weights["center_bonus"]
        elif board.grand_board[1][1] == self.human_player:
            score -= self.weights["center_bonus"]

        # Add randomness for easier difficulties
        if self.weights["randomness"] > 0:
            randomness_factor = random.uniform(
                -self.weights["randomness"], self.weights["randomness"]
            )
            score += score * randomness_factor

        return score

    def minimax(self, board, depth, is_maximizing, alpha, beta):
        """
        Minimax algorithm with alpha-beta pruning for optimal move calculation.

        Recursively evaluates all possible game positions to find the optimal
        move for the current player. Uses alpha-beta pruning to eliminate
        branches that cannot improve the final result, significantly improving
        efficiency.

        Args:
            board (UltimateTicTacToeBoard): Current board position
            depth (int): Remaining search depth (decreases with recursion)
            is_maximizing (bool): True if maximizing player (computer), False if minimizing (human)
            alpha (float): Best value the maximizing player can guarantee
            beta (float): Best value the minimizing player can guarantee

        Returns:
            int: The evaluation score for the current board position
                 Positive values favor the computer
                 Negative values favor the human
        """
        grand_winner = board.check_grand_win()
        if grand_winner is not None:
            base_score = self.evaluate_board(board)
            if base_score > 0:
                return base_score - depth
            if base_score < 0:
                return base_score + depth
            return base_score

        if depth == 0:
            return self.evaluate_board(board)

        legal_moves = board.get_legal_moves()
        if not legal_moves:
            return 0

        if is_maximizing:
            max_eval = float("-inf")
            for move in legal_moves:
                new_board = board.deep_copy()
                new_board.make_move(*move)

                eval_score = self.minimax(new_board, depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float("inf")
            for move in legal_moves:
                new_board = board.deep_copy()
                new_board.make_move(*move)

                eval_score = self.minimax(new_board, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    def get_best_move(self, depth=None):
        """
        Find the optimal move for the computer using minimax algorithm.

        Evaluates all legal moves using the minimax algorithm with alpha-beta
        pruning to find the move that yields the best position for the computer.
        Uses difficulty-based search depth for varying AI strength.

        Args:
            depth (int, optional): Search depth override. If None, uses difficulty-based depth

        Returns:
            tuple or None: (board_r, board_c, cell_r, cell_c) coordinates of best move,
                          or None if no legal moves available
        """
        if depth is None:
            depth = self.search_depth

        best_score = float("-inf")
        best_move = None

        if self.current_player != self.computer_player:
            return best_move

        legal_moves = self.get_legal_moves()

        if not legal_moves:
            return best_move

        for move in legal_moves:
            new_board = self.deep_copy()
            new_board.make_move(*move)
            if new_board.check_grand_win() == self.computer_player:
                return move

        for move in legal_moves:
            new_board = self.deep_copy()
            new_board.make_move(*move)

            score = self.minimax(
                new_board, depth - 1, False, float("-inf"), float("inf")
            )

            if score > best_score:
                best_score = score
                best_move = move

        return best_move


class UltimateTicTacToeGUI:
    """
    Graphical user interface for Ultimate Tic-Tac-Toe game.

    Provides a complete tkinter-based interface for playing Ultimate Tic-Tac-Toe
    against an AI opponent. Includes start screen with marker and difficulty
    selection, dynamic game board visualization, and game state management.

    Attributes:
        master (tk.Tk): Root tkinter window
        ai_depth (int): Default AI search depth (overridden by difficulty)
        game (UltimateTicTacToeBoard): Current game instance
        selected_difficulty (str): Chosen difficulty level
        buttons (dict): Dictionary of game board buttons
        sub_board_frames (dict): Dictionary of small board frames
        status_label (tk.Label): Game status display
        main_frame (tk.Frame): Main game board container
        choice_frame (tk.Frame): Start screen container
        reset_button (tk.Button): New game button
        selection_label (tk.Label): Selection status display
    """

    def __init__(self, master):
        self.master = master
        self.master.title("Ultimate Tic-Tac-Toe (Human vs. AI)")

        self.ai_depth = 4
        self.game = None
        self.selected_difficulty = "hard"

        self.buttons = {}
        self.sub_board_frames = {}
        self.status_label = None
        self.main_frame = None
        self.choice_frame = None
        self.reset_button = None

        self._start_screen()

    def _clear_master_widgets(self):
        """
        Remove all widgets from the master window.

        Clears the tkinter window by destroying all child widgets.
        Used when transitioning between different screens (start screen,
        game screen, etc.).
        """
        for widget in self.master.winfo_children():
            widget.destroy()

    def _start_screen(self):
        """
        Display the game start screen with marker and difficulty selection.

        Creates the initial interface where players choose their marker (X or O)
        and select difficulty level (Easy, Medium, Hard). Includes visual
        feedback for selections and intuitive color-coded buttons.
        """
        self._clear_master_widgets()

        self.choice_frame = tk.Frame(self.master, padx=50, pady=50, bg="#EEEEEE")
        self.choice_frame.pack(expand=True)

        # Title
        tk.Label(
            self.choice_frame,
            text="Ultimate Tic-Tac-Toe",
            font=("Arial", 24, "bold"),
            bg="#EEEEEE",
            fg="#333333",
        ).pack(pady=10)

        # Player marker selection
        tk.Label(
            self.choice_frame,
            text="Choose your marker:",
            font=("Arial", 18, "bold"),
            bg="#EEEEEE",
            fg="#333333",
        ).pack(pady=(20, 10))

        marker_frame = tk.Frame(self.choice_frame, bg="#EEEEEE")
        marker_frame.pack(pady=10)

        button_font = ("Arial", 16, "bold")

        btn_x = tk.Button(
            marker_frame,
            text="Play as X",
            command=lambda: self._select_marker(UltimateTicTacToeBoard.PLAYER_X),
            font=button_font,
            bg="#FF5733",
            fg="black",
            width=12,
            height=2,
            relief=tk.RAISED,
            bd=4,
        )
        btn_x.pack(side=tk.LEFT, padx=5)

        btn_o = tk.Button(
            marker_frame,
            text="Play as O",
            command=lambda: self._select_marker(UltimateTicTacToeBoard.PLAYER_O),
            font=button_font,
            bg="#33A07A",
            fg="black",
            width=12,
            height=2,
            relief=tk.RAISED,
            bd=4,
        )
        btn_o.pack(side=tk.LEFT, padx=5)

        # Difficulty selection
        tk.Label(
            self.choice_frame,
            text="Choose difficulty:",
            font=("Arial", 18, "bold"),
            bg="#EEEEEE",
            fg="#333333",
        ).pack(pady=(30, 10))

        difficulty_frame = tk.Frame(self.choice_frame, bg="#EEEEEE")
        difficulty_frame.pack(pady=10)

        difficulties = [
            ("Easy", "easy", "#4CAF50"),
            ("Medium", "medium", "#FF9800"),
            ("Hard", "hard", "#F44336"),
        ]

        for text, value, color in difficulties:
            btn = tk.Button(
                difficulty_frame,
                text=text,
                command=lambda v=value: self._select_difficulty(v),
                font=("Arial", 14, "bold"),
                bg=color,
                fg="black",
                width=10,
                height=2,
                relief=tk.RAISED,
                bd=3,
            )
            btn.pack(side=tk.LEFT, padx=5)

        # Current selections display
        self.selection_label = tk.Label(
            self.choice_frame,
            text=f"Selected: Marker = Not chosen, Difficulty = {self.selected_difficulty.title()}",
            font=("Arial", 12),
            bg="#EEEEEE",
            fg="#666666",
        )
        self.selection_label.pack(pady=(20, 10))

    def _select_marker(self, marker):
        """
        Handle player marker selection and start the game.

        Called when player chooses X or O marker. Immediately starts
        a new game with the selected marker and current difficulty setting.

        Args:
            marker (str): Chosen player marker ('X' or 'O')
        """
        self.selected_marker = marker
        self._setup_game(marker, self.selected_difficulty)

    def _select_difficulty(self, difficulty):
        """
        Handle difficulty level selection.

        Updates the selected difficulty and refreshes the selection display
        to show the current choice. Player must still choose a marker to
        start the game.

        Args:
            difficulty (str): Chosen difficulty level ('easy', 'medium', 'hard')
        """
        self.selected_difficulty = difficulty
        self.selection_label.config(
            text=f"Selected: Marker = Not chosen, Difficulty = {difficulty.title()}"
        )

    def _setup_game(self, human_marker, difficulty="hard"):
        """
        Initialize and set up a new game with specified parameters.

        Creates a new game instance, sets up the UI elements, and prepares
        the game board for play. If the human player is O, triggers the
        AI to make the first move.

        Args:
            human_marker (str): Player's chosen marker ('X' or 'O')
            difficulty (str): AI difficulty level ('easy', 'medium', 'hard')
        """
        self._clear_master_widgets()

        self.game = UltimateTicTacToeBoard(
            human_marker=human_marker, difficulty=difficulty
        )
        self.buttons = {}
        self.sub_board_frames = {}

        # Status label with difficulty indicator
        self.status_label = tk.Label(
            self.master,
            text=f"Difficulty: {difficulty.title()}",
            font=("Arial", 14, "bold"),
        )
        self.status_label.pack(pady=10)

        self.main_frame = tk.Frame(self.master, bd=5, relief=tk.RIDGE, bg="#333333")
        self.main_frame.pack(padx=10, pady=10)

        self._create_board_ui()

        self.reset_button = tk.Button(
            self.master,
            text="New Game (Choose Side)",
            command=self._start_screen,
            font=("Arial", 12),
            bg="#FF5733",
            fg="black",
            relief=tk.RAISED,
            bd=3,
        )
        self.reset_button.pack(pady=10)

        self._update_ui_state()

        if self.game.human_player == UltimateTicTacToeBoard.PLAYER_O:
            self.master.after(500, self.make_ai_move)

    def _create_board_ui(self):
        """
        Create the visual game board interface.

        Constructs the 3x3 grid of small board frames, each containing
        a 3x3 grid of clickable buttons. Sets up the visual layout and
        configures button callbacks for user interaction.
        """
        for br in range(3):
            for bc in range(3):

                frame = tk.Frame(
                    self.main_frame,
                    bd=4,
                    relief=tk.RAISED,
                    bg="#CCCCCC",
                    width=150,
                    height=150,
                )
                frame.grid(row=br, column=bc, padx=5, pady=5)
                self.sub_board_frames[(br, bc)] = frame

                self.buttons[(br, bc)] = {}

                for cr in range(3):
                    for cc in range(3):

                        command_func = partial(self.on_button_click, br, bc, cr, cc)

                        btn = tk.Button(
                            frame,
                            text=self.game.EMPTY_CELL,
                            font=("Arial", 18, "bold"),
                            width=4,
                            height=2,
                            command=command_func,
                            bg="white",
                            fg="#333333",
                            relief=tk.FLAT,
                            bd=1,
                        )
                        btn.grid(row=cr, column=cc, padx=1, pady=1, sticky="nsew")
                        self.buttons[(br, bc)][(cr, cc)] = btn

                frame.grid_rowconfigure((0, 1, 2), weight=1)
                frame.grid_columnconfigure((0, 1, 2), weight=1)

    def _update_ui_state(self, game_end=False):
        """
        Update the visual state of the game interface.

        Refreshes all UI elements to reflect the current game state including
        button states, colors, board highlights, and status messages. Handles
        visual feedback for legal moves, completed boards, and game end conditions.

        Args:
            game_end (bool): Whether the game has ended (disables all buttons)
        """

        required_br, required_bc = self.game.next_board_coords or (None, None)
        legal_moves = self.game.get_legal_moves()

        grand_winner = self.game.check_grand_win()
        game_is_over = grand_winner is not None or game_end

        for br in range(3):
            for bc in range(3):
                frame = self.sub_board_frames[(br, bc)]
                sub_board_status = self.game.grand_board[br][bc]

                is_required = required_br == br and required_bc == bc

                if sub_board_status != self.game.EMPTY_CELL:
                    frame.config(bg="#333333", relief=tk.SUNKEN)
                    self._show_small_board_winner(br, bc, sub_board_status)
                    continue

                elif is_required:

                    frame.config(bg="#ADD8E6", relief=tk.RAISED)
                else:

                    frame.config(bg="#FFFFFF", relief=tk.RAISED)

                for cr in range(3):
                    for cc in range(3):
                        btn = self.buttons[(br, bc)][(cr, cc)]
                        cell_value = self.game.boards[br][bc][cr][cc]
                        btn.config(text=cell_value)

                        if game_is_over:
                            btn.config(state=tk.DISABLED, bg="lightgray")
                            continue

                        is_legal = (br, bc, cr, cc) in legal_moves

                        if cell_value != self.game.EMPTY_CELL:

                            btn.config(
                                state=tk.DISABLED,
                                bg="lightgray",
                                fg="red" if cell_value == "X" else "green",
                            )
                        elif not is_legal:

                            btn.config(state=tk.DISABLED, bg="#F0F0F0")
                        else:

                            btn.config(
                                state=tk.NORMAL,
                                fg=(
                                    "red"
                                    if self.game.current_player == "X"
                                    else "green"
                                ),
                            )

                            if is_required:
                                btn.config(bg="#C0E0FF")
                            else:
                                btn.config(bg="white")

        # Initialize variables for winner display
        winner_text = ""
        color = "black"

        if grand_winner == self.game.PLAYER_X:
            winner_text = (
                f"X Wins! ({'You' if self.game.human_player == 'X' else 'AI'})"
            )
            color = "red"
        elif grand_winner == self.game.PLAYER_O:
            winner_text = (
                f"O Wins! ({'You' if self.game.human_player == 'O' else 'AI'})"
            )
            color = "green"
        elif grand_winner == self.game.TIE_CELL:
            winner_text = "Tie"
            color = "blue"

        if grand_winner is not None:
            self.status_label.config(
                text=f"GAME OVER: {winner_text} (Difficulty: {self.game.difficulty.title()})",
                fg=color,
            )
        else:
            current_player = self.game.current_player
            player_role = "Your" if current_player == self.game.human_player else "AI"
            self.status_label.config(
                text=f"{player_role} Turn: {current_player} (Difficulty: {self.game.difficulty.title()})",
                fg="red" if current_player == "X" else "green",
            )

    def _show_small_board_winner(self, br, bc, winner_char):
        """
        Display the winner of a completed small board.

        Replaces the small board's buttons with a large winner symbol
        when the board is won or tied. Uses color coding to distinguish
        between different outcomes.

        Args:
            br (int): Board row coordinate (0-2)
            bc (int): Board column coordinate (0-2)
            winner_char (str): Winner symbol ('X', 'O', or 'T' for tie)
        """
        frame = self.sub_board_frames[(br, bc)]

        for widget in frame.winfo_children():
            widget.destroy()

        if winner_char == self.game.PLAYER_X:
            text = "X"
            color = "red"
        elif winner_char == self.game.PLAYER_O:
            text = "O"
            color = "green"
        else:
            text = "T"
            color = "blue"

        winner_label = tk.Label(
            frame, text=text, font=("Arial", 40, "bold"), bg="#333333", fg=color
        )
        winner_label.place(
            relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=1.0, relheight=1.0
        )

    def on_button_click(self, br, bc, cr, cc):
        """
        Handle human player button clicks on the game board.

        Processes user input when clicking on a game board button.
        Validates the move, updates the game state, refreshes the UI,
        and triggers the AI opponent's response if the game continues.

        Args:
            br (int): Small board row coordinate (0-2)
            bc (int): Small board column coordinate (0-2)
            cr (int): Cell row within small board (0-2)
            cc (int): Cell column within small board (0-2)
        """

        self.game.make_move(br, bc, cr, cc)

        self._update_ui_state()

        if self.game.check_grand_win() is not None:
            self._update_ui_state(game_end=True)
            return

        self.master.after(500, self.make_ai_move)

    def make_ai_move(self):
        """
        Execute the AI opponent's move using difficulty-based strategy.

        Calculates and executes the optimal move for the AI player using
        the minimax algorithm with difficulty-appropriate search depth
        and evaluation weights. Updates the UI and checks for game end.
        """
        if self.game.current_player != self.game.computer_player:
            return

        self.master.update()

        ai_move = self.game.get_best_move()

        if ai_move:
            self.game.make_move(*ai_move)

            self._update_ui_state()

            if self.game.check_grand_win() is not None:
                self._update_ui_state(game_end=True)
        else:
            self._update_ui_state(game_end=True)


if __name__ == "__main__":
    root = tk.Tk()
    game_gui = UltimateTicTacToeGUI(root)
    root.mainloop()
