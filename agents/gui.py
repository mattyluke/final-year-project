import tkinter as tk
from tkinter import messagebox
import math
import threading
from game_engine import Board
from mcts import mcts

EMPTY = 0
RED = 1
BLACK = 2
DIRECTIONS = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]

HEX_SIZE = 50
W, H = 600, 600

def axial_to_pixel(q, r):
    x = HEX_SIZE * 1.5 * q
    y = HEX_SIZE * math.sqrt(3) * (r + q / 2)
    return x + W // 2, y + H // 2

def hex_points(cx, cy, size=HEX_SIZE - 3):
    pts = []
    for k in range(6):
        a = math.pi / 180 * (60 * k)
        pts += [cx + size * math.cos(a), cy + size * math.sin(a)]
    return pts

class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Nonaga")
        self.board = Board()
        self.selected_token = None
        self.selected_disc = None
        self.phase = "token"

        self.label = tk.Label(root, text="Your turn — click a red piece", font=("Arial", 12))
        self.label.pack()

        self.canvas = tk.Canvas(root, width=W, height=H, bg="white")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)

        self.draw()

    def draw(self):
        self.canvas.delete("all")
        b = self.board

        for coord in b.candidates:
            cx, cy = axial_to_pixel(*coord)
            self.canvas.create_polygon(hex_points(cx, cy), fill="#ddd", outline="#aaa")

        for idx, coord in enumerate(b.coords):
            cx, cy = axial_to_pixel(*coord)
            movable = idx in b.movable_discs and idx != b.last_moved_disc
            selected = self.selected_disc == idx
            fill = "yellow" if selected else ("lightblue" if movable else "lightgray")
            self.canvas.create_polygon(hex_points(cx, cy), fill=fill, outline="gray", width=2)

            token = b.board[idx]
            if token != EMPTY:
                col = "red" if token == RED else "black"
                r = HEX_SIZE * 0.35
                outline = "yellow" if self.selected_token == idx else col
                self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=col, outline=outline, width=3)

    def set_status(self, msg):
        self.label.config(text=msg)

    def on_click(self, event):
        x, y = event.x, event.y
        disc = self.find_disc(x, y)
        cand = self.find_candidate(x, y)

        if self.phase == "token":
            if disc is not None and self.board.board[disc] == RED:
                self.selected_token = disc
                self.set_status("Token selected — click an adjacent hex to slide towards")
                self.draw()
            elif self.selected_token is not None and disc is not None:
                self.try_token_move(disc)

        elif self.phase == "disc":
            if disc is not None and disc in self.board.movable_discs and disc != self.board.last_moved_disc:
                self.selected_disc = disc
                self.set_status("Disc selected — click a grey candidate hex")
                self.draw()
            elif self.selected_disc is not None and cand is not None:
                self.board.move_disc(self.selected_disc, cand)
                self.selected_disc = None
                self.phase = "token"
                self.draw()
                self.set_status("AI thinking...")
                self.root.after(50, self.ai_turn)

    def find_disc(self, x, y):
        for idx, coord in enumerate(self.board.coords):
            cx, cy = axial_to_pixel(*coord)
            if math.hypot(x - cx, y - cy) < HEX_SIZE * 0.9:
                return idx
        return None

    def find_candidate(self, x, y):
        for coord in self.board.candidates:
            cx, cy = axial_to_pixel(*coord)
            if math.hypot(x - cx, y - cy) < HEX_SIZE * 0.9:
                return coord
        return None

    def try_token_move(self, clicked_disc):
        b = self.board
        fx, fy = b.coords[self.selected_token]
        tx, ty = b.coords[clicked_disc]
        dx, dy = tx - fx, ty - fy
        best_dir = min(range(6), key=lambda d: abs(DIRECTIONS[d][0] - dx) + abs(DIRECTIONS[d][1] - dy))

        result = b.move_token(self.selected_token, best_dir)
        if not result:
            self.set_status("Can't move there, try again")
            return

        self.selected_token = None
        self.phase = "disc"
        self.set_status("Token moved — now select a lightblue disc to move")
        self.draw()

        if b.check_win(RED):
            self.draw()
            messagebox.showinfo("Game Over", "You win!")
            self.reset()

    def ai_turn(self):
        def run():
            move = mcts(self.board, BLACK, iterations=300)
            self.root.after(0, lambda: self.apply_ai(move))
        threading.Thread(target=run, daemon=True).start()

    def apply_ai(self, move):
        if move is None:
            self.set_status("AI has no moves — stalemate")
            return
        print(move)
        token_move, disc_move = move
        _, ti, DIR = token_move
        self.board.move_token(ti, DIR)
        _, di, coord = disc_move
        self.board.move_disc(di, coord)
        self.draw()
        if self.board.check_win(BLACK):
            messagebox.showinfo("Game Over", "AI wins!")
            self.reset()
            return
        self.phase = "token"
        self.set_status("Your turn — click a red piece")

    def reset(self):
        self.board = Board()
        self.selected_token = None
        self.selected_disc = None
        self.phase = "token"
        self.set_status("Your turn — click a red piece")
        self.draw()

root = tk.Tk()
GUI(root)
root.mainloop()