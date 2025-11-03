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
    Docstring
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
        Docstring

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
        Docstring
        """
        for row in board:
            if self.EMPTY_CELL in row:
                return False
        return True

    def deep_copy(self):
        """
        Docstring
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
        Docstring
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
        Docstring

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
        Docstring

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
        Docstring

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
        Docstring
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
        Easy mode uses suboptimal weights, Hard mode uses optimal weights.
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
        Docstring

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
        Get best move using difficulty-based search depth.
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
    Docstring
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
        Docstring

        """
        for widget in self.master.winfo_children():
            widget.destroy()

    def _start_screen(self):
        """
        Show start screen with player marker and difficulty selection.
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
        Handle marker selection and start game.
        """
        self.selected_marker = marker
        self._setup_game(marker, self.selected_difficulty)

    def _select_difficulty(self, difficulty):
        """
        Handle difficulty selection.
        """
        self.selected_difficulty = difficulty
        self.selection_label.config(
            text=f"Selected: Marker = Not chosen, Difficulty = {difficulty.title()}"
        )

    def _setup_game(self, human_marker, difficulty="hard"):
        """
        Set up game with selected marker and difficulty.
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
        Docstring

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
        Docstring
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
        Docstring
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
        Docstring
        """

        self.game.make_move(br, bc, cr, cc)

        self._update_ui_state()

        if self.game.check_grand_win() is not None:
            self._update_ui_state(game_end=True)
            return

        self.master.after(500, self.make_ai_move)

    def make_ai_move(self):
        """
        Make AI move using difficulty-based strategy.
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
