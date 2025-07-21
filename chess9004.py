import tkinter as tk
from tkinter import messagebox
import chess
import chess.engine

# === Setup Stockfish ===
STOCKFISH_PATH = "C:/Users/Dylan Chamberlin/Documents/Chess9000/Stockfish/stockfish/stockfish-windows-x86-64-avx2.exe"  # Make sure it's installed and on PATH

# === Chess Board Logic ===
class ChessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Assistant - White to Win")

        self.board = chess.Board()
        self.canvas = tk.Canvas(root, width=520, height=520)
        self.canvas.pack()
        self.square_size = 65

        self.selected_square = None
        self.piece_ids = {}

        self.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_click)

        self.status = tk.Label(root, text="Your move (White)", font=("Arial", 14))
        self.status.pack()

        self.current_turn = chess.WHITE

    def draw_board(self):
        self.canvas.delete("all")
        colors = ["#EEEED2", "#769656"]
        for row in range(8):
            for col in range(8):
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                color = colors[(row + col) % 2]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

        self.draw_pieces()

    def draw_pieces(self):
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                file = chess.square_file(square)
                rank = 7 - chess.square_rank(square)
                x = file * self.square_size + 32
                y = rank * self.square_size + 32
                label = piece.symbol().upper() if piece.color else piece.symbol().lower()
                self.canvas.create_text(x, y, text=label, font=("Arial", 32), tags=("piece",))

    def on_click(self, event):
        col = event.x // self.square_size
        row = event.y // self.square_size
        square = chess.square(col, 7 - row)

        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == self.current_turn:
                self.selected_square = square
                self.status.config(text=f"Selected {chess.square_name(square)}. Click destination square.")
        else:
            move = chess.Move(self.selected_square, square)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.selected_square = None
                self.current_turn = not self.current_turn
                self.draw_board()
                if self.current_turn == chess.BLACK:
                    self.status.config(text="Black's move (your friend's move)")
                else:
                    self.status.config(text="White's move")
                self.root.after(100, self.show_best_line)
            else:
                self.status.config(text="Illegal move. Try again.")
                self.selected_square = None

    def show_best_line(self):
        if self.board.turn != chess.WHITE:
            return

        info = self.engine.analyse(self.board, chess.engine.Limit(depth=15))
        if "pv" in info:
            plan = info["pv"]
            if plan:
                preview_board = self.board.copy()
                try:
                    line = [preview_board.san(m) for m in plan[:5]]
                    for m in plan[:5]:
                        preview_board.push(m)
                    next_move = plan[0]
                    move_text = f"{chess.square_name(next_move.from_square)} to {chess.square_name(next_move.to_square)}"
                    self.status.config(text=f"Next move: {move_text} | Plan: {' → '.join(line)}")
                    print(f"Next move: {move_text}")
                    print("Plan:")
                    for move in line:
                        print(move)
                except:
                    self.status.config(text="AI suggested illegal or invalid move. Plan not available.")
                    print(f"Next move: {move_text}")
                    print("[Error] Invalid move sequence in AI plan.")
            else:
                self.status.config(text="No clear winning plan.")
                print("[Info] No plan returned by engine.")
        else:
            self.status.config(text="Checkmate may no longer be possible.")
            print("[Info] Engine could not find a plan.")

    def on_closing(self):
        self.engine.quit()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ChessApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
