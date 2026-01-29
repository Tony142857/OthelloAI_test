import tkinter as tk
from tkinter import messagebox, filedialog
import os, json, datetime, threading, time
from board import Board, BLACK, WHITE
from player import HumanPlayer
from ai_greedy import GreedyAI
from ai_minimax import MiniMaxAI
from evaluate import full_eval, base_eval
import numpy as np
from PIL import Image, ImageTk

CELL_SIZE = 52
BOARD_BG = "#e5eadf"
BOARD_LINE = "#bfc5b1"
BOARD_EDGE = "#96b69c"
BUTTON_BG = "#e5edfa"
BUTTON_ACTIVE = "#d3e6fc"
BUTTON_FG = "#253c52"
BUTTON_DIS = "#d6dbd6"
BUTTON_ROUND = "#a8bdd2"
TIP_COLOR = "#7c5cff"
HIGHLIGHT_COLOR = "#4ea4ff"
COLOR_MAP = {BLACK: "#24252c", WHITE: "#f6f7f7"}
UNDO_LIMIT = 5

AI_LEVELS = [
    ("简单（贪心）", "Greedy", {"ai_class": GreedyAI}),
    ("标准（极小极大3层）", "MiniMax-3", {"ai_class": MiniMaxAI, "depth": 3, "eval_fn": base_eval}),
    ("困难（极小极大5层+复杂评估）", "MiniMax-5+", {"ai_class": MiniMaxAI, "depth": 5, "eval_fn": full_eval}),
]

def get_board_score(board):
    b, w = int((board==BLACK).sum()), int((board==WHITE).sum())
    diff = b - w
    if diff > 0:
        tip = f"黑方优势（+{diff}）"
    elif diff < 0:
        tip = f"白方优势（+{abs(diff)}）"
    else:
        tip = "局势均衡（0）"
    return tip

class HoverButton(tk.Button):
    def __init__(self, master, **kw):
        super().__init__(master=master, **kw)
        self.default_bg = self['bg']
        self.default_fg = self['fg']
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
    def on_enter(self, e):
        if self["state"] == tk.NORMAL:
            self['bg'] = BUTTON_ACTIVE
            self['fg'] = "#4268a5"
    def on_leave(self, e):
        self['bg'] = self.default_bg
        self['fg'] = self.default_fg

class MainMenuFrame(tk.Frame):
    def __init__(self, parent, start_callback):
        super().__init__(parent, bg="#f6f8f7")
        self.parent = parent
        tk.Label(self, text="Othello 黑白棋", font=('微软雅黑', 30, "bold"), bg="#f6f8f7", fg="#4268a5").pack(pady=(45, 26))
        btns = []
        btns.append(("人人对战", lambda: start_callback(1)))
        btns.append(("人机对战", lambda: self.pick_human_vs_ai(start_callback)))
        btns.append(("AI互战（双AI难度自选）", lambda: self.pick_ai_vs_ai(start_callback)))
        btns.append(("棋局复盘模式", lambda: self.pick_replay_file(start_callback)))
        btns.append(("退出", parent.destroy))
        btn_frame = tk.Frame(self, bg="#f6f8f7")
        btn_frame.pack(pady=(3,12))
        for i, (txt, cmd) in enumerate(btns):
            HoverButton(btn_frame, text=txt, font=('微软雅黑', 17,"bold"), width=22, height=2,
                         bg=BUTTON_BG, fg=BUTTON_FG,
                         activebackground=BUTTON_ACTIVE, borderwidth=0,
                         relief="flat", command=cmd, highlightthickness=2,
                         highlightbackground=BUTTON_ROUND, highlightcolor=BUTTON_ROUND
                         ).pack(pady=10)
        tk.Label(self, text="Powered by Othello-AI", font=("微软雅黑", 10, "italic"), fg="#aaa", bg="#f6f8f7").pack(side=tk.BOTTOM, pady=16)

    def pick_human_vs_ai(self, callback):
        dlg = tk.Toplevel(self)
        dlg.title("人机对战配置")
        dlg.geometry("480x430")
        dlg.resizable(True, True)
        dlg.configure(bg="#f7faf6")
        tk.Label(dlg, text="请选择你的执棋颜色：", font=('微软雅黑', 17, "bold"), bg="#f7faf6", fg="#4167ab").pack(pady=(24,9), anchor="w", padx=24)
        color_var = tk.StringVar(value="black")
        color_frame = tk.Frame(dlg,bg="#f7faf6")
        color_frame.pack(padx=35, anchor="w")
        HoverButton(color_frame, text="黑棋（●）", font=('微软雅黑', 15), width=10, height=1,
                    bg=BUTTON_BG, fg=BUTTON_FG,relief="groove",
                    command=lambda:color_var.set("black")).pack(side="left", padx=18, pady=6)
        HoverButton(color_frame, text="白棋（○）", font=('微软雅黑', 15), width=10, height=1,
                    bg=BUTTON_BG, fg=BUTTON_FG, relief="groove",
                    command=lambda:color_var.set("white")).pack(side="left", padx=18, pady=6)

        tk.Label(dlg, text="请选择你是先手还是后手：", font=('微软雅黑', 17, "bold"), bg="#f7faf6", fg="#4167ab").pack(pady=(20,10), anchor="w", padx=24)
        order_var = tk.StringVar(value="first")
        order_frame = tk.Frame(dlg,bg="#f7faf6")
        order_frame.pack(padx=35, anchor="w")
        HoverButton(order_frame, text="先手", font=('微软雅黑', 15), width=10, height=1,
                    bg=BUTTON_BG, fg=BUTTON_FG,
                    command=lambda:order_var.set("first")).pack(side="left", padx=18, pady=6)
        HoverButton(order_frame, text="后手", font=('微软雅黑', 15), width=10, height=1,
                    bg=BUTTON_BG, fg=BUTTON_FG,
                    command=lambda:order_var.set("second")).pack(side="left", padx=18, pady=6)

        tk.Label(dlg, text="请选择AI难度：", font=('微软雅黑', 17, "bold"), bg="#f7faf6", fg="#4167ab").pack(pady=(19,11), anchor="w", padx=24)
        ai_var = tk.IntVar(value=1)
        ai_radio_frame = tk.Frame(dlg,bg="#f7faf6")
        ai_radio_frame.pack(anchor="w", padx=35)
        for idx, (desc, key, _) in enumerate(AI_LEVELS):
            tk.Radiobutton(ai_radio_frame, text=desc, variable=ai_var, value=idx,
                           font=('微软雅黑', 15), indicatoron=1, bg="#f7faf6", selectcolor=BUTTON_BG,
                           anchor="w", width=22, padx=11, pady=7).pack(anchor="w", pady=3)
        HoverButton(dlg, text="确定", font=('微软雅黑', 15, "bold"), width=10, bg=BUTTON_BG, fg=BUTTON_FG,
                command=lambda: [callback(("human_vs_ai", color_var.get(), order_var.get(), ai_var.get())), dlg.destroy()]
                ).pack(pady=23)

    def pick_human_vs_ai(self, callback):
        dlg = tk.Toplevel(self)
        dlg.title("人机对战配置")
        dlg.geometry("520x520")
        dlg.resizable(True, True)
        dlg.configure(bg="#f7faf6")
        outer = tk.Frame(dlg, bg="#f7faf6")
        outer.pack(expand=True, fill="both")
        # 内容frame + button框分开
        content = tk.Frame(outer, bg="#f7faf6")
        content.pack(expand=True)
        # 颜色选择
        tk.Label(content, text="请选择你的执棋颜色：", font=('微软雅黑', 17, "bold"),
                 bg="#f7faf6", fg="#4167ab").grid(row=0, column=0, pady=(24, 8), sticky="ew", columnspan=2)
        color_var = tk.StringVar(value="black")
        color_frame = tk.Frame(content, bg="#f7faf6")
        color_frame.grid(row=1, column=0, columnspan=2, pady=(0, 2))
        for k, txt in zip(["black", "white"], ["黑棋（●）", "白棋（○）"]):
            tk.Radiobutton(color_frame, text=txt, variable=color_var, value=k,
                           font=('微软雅黑', 15), indicatoron=1,
                           bg="#f7faf6", selectcolor="#e5edfa", width=12).pack(side="left", padx=20, pady=7)
        # 先/后手
        tk.Label(content, text="请选择你是先手还是后手：", font=('微软雅黑', 17, "bold"),
                 bg="#f7faf6", fg="#4167ab").grid(row=2, column=0, columnspan=2, pady=(16, 8), sticky="ew")
        order_var = tk.StringVar(value="first")
        order_frame = tk.Frame(content, bg="#f7faf6")
        order_frame.grid(row=3, column=0, columnspan=2, pady=(0, 2))
        for k, txt in zip(["first", "second"], ["先手", "后手"]):
            tk.Radiobutton(order_frame, text=txt, variable=order_var, value=k,
                           font=('微软雅黑', 15), indicatoron=1,
                           bg="#f7faf6", selectcolor="#e5edfa", width=12).pack(side="left", padx=20, pady=7)
        # AI难度
        tk.Label(content, text="请选择AI难度：", font=('微软雅黑', 17, "bold"),
                 bg="#f7faf6", fg="#4167ab").grid(row=4, column=0, columnspan=2, pady=(18, 8), sticky="ew")
        ai_var = tk.IntVar(value=1)
        ai_radio_frame = tk.Frame(content, bg="#f7faf6")
        ai_radio_frame.grid(row=5, column=0, columnspan=2)
        for idx, (desc, key, _) in enumerate(AI_LEVELS):
            tk.Radiobutton(ai_radio_frame, text=desc, variable=ai_var, value=idx,
                           font=('微软雅黑', 15), indicatoron=1, width=22,
                           bg="#f7faf6", selectcolor="#e5edfa").pack(anchor="center", pady=3)
        # 确定按钮——新建单独底部Frame，永远在底部居中
        btn_frame = tk.Frame(outer, bg="#f7faf6")
        btn_frame.pack(fill="x", side="bottom", pady=(10, 24))
        tk.Button(btn_frame, text="确定", font=('微软雅黑', 15, "bold"), width=13,
                  bg="#e5edfa", fg="#253c52",
                  command=lambda: [
                      callback(("human_vs_ai", color_var.get(), order_var.get(), ai_var.get())), dlg.destroy()
                  ]).pack(side="top", anchor="center")

    def pick_replay_file(self, start_callback):
        folder = "replays"
        if not os.path.exists(folder):
            os.makedirs(folder)
        fname = filedialog.askopenfilename(title="选择棋谱文件(.json)", initialdir=folder,
                                           filetypes=[("棋局棋谱", "*.json")])
        if fname:
            start_callback(("replay_mode", fname))

    def pick_ai_vs_ai(self, callback):
        dlg = tk.Toplevel(self)
        dlg.title("双AI对战配置")
        dlg.geometry("520x480")
        dlg.resizable(True, True)
        dlg.configure(bg="#f7faf6")
        # 黑方AI难度
        tk.Label(dlg, text="请选择黑方AI难度：", font=('微软雅黑', 15, "bold"), bg="#f7faf6", fg="#4167ab").pack(pady=(24, 8), anchor="w", padx=24)
        black_var = tk.IntVar(value=1)
        black_frame = tk.Frame(dlg, bg="#f7faf6")
        black_frame.pack(anchor="w", padx=35)
        for idx, (desc, key, _) in enumerate(AI_LEVELS):
            tk.Radiobutton(black_frame, text=desc, variable=black_var, value=idx,
                           font=('微软雅黑', 13), indicatoron=True, bg="#f7faf6", selectcolor=BUTTON_BG,
                           anchor="w", width=22, padx=11, pady=5).pack(anchor="w", pady=2)
        # 白方AI难度
        tk.Label(dlg, text="请选择白方AI难度：", font=('微软雅黑', 15, "bold"), bg="#f7faf6", fg="#4167ab").pack(pady=(18, 8), anchor="w", padx=24)
        white_var = tk.IntVar(value=1)
        white_frame = tk.Frame(dlg, bg="#f7faf6")
        white_frame.pack(anchor="w", padx=35)
        for idx, (desc, key, _) in enumerate(AI_LEVELS):
            tk.Radiobutton(white_frame, text=desc, variable=white_var, value=idx,
                           font=('微软雅黑', 13), indicatoron=True, bg="#f7faf6", selectcolor=BUTTON_BG,
                           anchor="w", width=22, padx=11, pady=5).pack(anchor="w", pady=2)
        # 确定按钮
        HoverButton(dlg, text="确定", font=('微软雅黑', 15, "bold"), width=10, bg=BUTTON_BG, fg=BUTTON_FG,
                command=lambda: [callback(("ai_vs_ai", black_var.get(), white_var.get())), dlg.destroy()]
                ).pack(pady=23)

class GameFrame(tk.Frame):
    def __init__(self, parent, modeconf, return_menu_callback):
        super().__init__(parent, bg="#f3f4f2")
        self.parent = parent
        self.return_menu_callback = return_menu_callback



        if isinstance(modeconf, tuple) and modeconf[0] == "replay_mode":
            _, fname = modeconf
            with open(fname, "r", encoding="utf-8") as f:
                self.replay_summary = json.load(f)
            self.replay_idx = 0
            self.game_info = "棋局复盘模式"
            self.is_replay_mode = True
            class DummyHumanPlayer: pass
            self.player1 = self.player2 = DummyHumanPlayer()
            self.player_order = [self.player1, self.player2]
            self.board = Board()
            self.apply_replay_idx()
        else:
            self.is_replay_mode = False
            if modeconf == 1:
                self.player1 = HumanPlayer(BLACK)
                self.player2 = HumanPlayer(WHITE)
                self.ai1_name = self.ai2_name = ""
                self.game_info = "人人对战"
                self.player_order = [self.player1, self.player2]
            elif isinstance(modeconf, tuple) and modeconf[0] == "human_vs_ai":
                _, mycolor, myorder, ai_level = modeconf
                ai_conf = AI_LEVELS[ai_level][2]
                ai_name = AI_LEVELS[ai_level][0]
                if mycolor == "black":
                    human = HumanPlayer(BLACK)
                    ai = ai_conf["ai_class"](WHITE, **{k:v for k,v in ai_conf.items() if k not in ["ai_class"]})
                    if myorder == "first":
                        self.player_order = [human, ai]
                        self.game_info = f"你(黑)先手  vs  {ai_name}(白)"
                    else:
                        self.player_order = [ai, human]
                        self.game_info = f"你(黑)后手  vs  {ai_name}(白)"
                else:
                    ai = ai_conf["ai_class"](BLACK, **{k:v for k,v in ai_conf.items() if k not in ["ai_class"]})
                    human = HumanPlayer(WHITE)
                    if myorder == "first":
                        self.player_order = [ai, human]
                        self.game_info = f"{ai_name}(黑)先手  vs  你(白)"
                    else:
                        self.player_order = [human, ai]
                        self.game_info = f"你(白)先手  vs  {ai_name}(黑)"
                self.player1, self.player2 = self.player_order
                self.ai1_name = ""
                self.ai2_name = ai_name
            elif isinstance(modeconf, tuple) and modeconf[0] == "ai_vs_ai":
                _, black_lvl, white_lvl = modeconf
                conf_b, conf_w = AI_LEVELS[black_lvl][2], AI_LEVELS[white_lvl][2]
                self.player1 = conf_b["ai_class"](BLACK, **{k:v for k,v in conf_b.items() if k not in ["ai_class"]})
                self.player2 = conf_w["ai_class"](WHITE, **{k:v for k,v in conf_w.items() if k not in ["ai_class"]})
                self.player_order = [self.player1, self.player2]
                self.ai1_name = AI_LEVELS[black_lvl][0]
                self.ai2_name = AI_LEVELS[white_lvl][0]
                self.game_info = f"黑：{self.ai1_name}  白：{self.ai2_name}"
            else:
                raise ValueError("modeconf wrong")
            self.board = Board()
            self.history = []
            self.recorded_moves = []
            self.paused = False
            self.turn = 0
            self.current_player = self.player_order[0]
            self.save_full_history_snapshot("init", None)

        self.score_label = tk.Label(self, text="", font=("微软雅黑", 13, "bold"),
                                    bg="#dde4f1", fg="#444968", pady=8, borderwidth=0)
        self.score_label.pack(pady=(7,1), fill=tk.X)
        self.status_label = tk.Label(self, text=self.game_info, font=("微软雅黑", 16, "bold"),
                                     bg="#f3f4f2", fg="#18224b")
        self.status_label.pack(pady=(2,10))
        self.btn_frame = tk.Frame(self, bg="#f3f4f2")
        self.btn_frame.pack(pady=(0, 11))
        self.btn_pause = HoverButton(self.btn_frame, text="暂停", font=('微软雅黑', 13, "bold"), width=8, height=1,
                                   bg=BUTTON_BG, fg=BUTTON_FG, command=self.toggle_pause)
        self.btn_undo = HoverButton(self.btn_frame, text="悔棋", font=('微软雅黑', 13, "bold"), width=8, height=1,
                                   bg=BUTTON_BG, fg=BUTTON_FG, command=self.undo)
        self.btn_restart = HoverButton(self.btn_frame, text="重开", font=('微软雅黑', 13, "bold"), width=8, height=1,
                                   bg=BUTTON_BG, fg=BUTTON_FG, command=self.restart)
        self.btn_menu = HoverButton(self.btn_frame, text="菜单", font=('微软雅黑', 13, "bold"), width=8, height=1,
                                   bg=BUTTON_BG, fg=BUTTON_FG, command=self.to_menu)
        self.btn_tip = HoverButton(self.btn_frame, text="AI提示", font=('微软雅黑',13,"bold"), width=8, height=1,
                                 bg=TIP_COLOR, fg="#fff", command=self.ai_tip_move)
        self.btn_pause.grid(row=0, column=0, padx=8)
        self.btn_undo.grid(row=0, column=1, padx=8)
        self.btn_restart.grid(row=0, column=2, padx=8)
        self.btn_menu.grid(row=0, column=3, padx=8)
        self.btn_tip.grid(row=0, column=4, padx=8)
        self.tip_suggest = None

        pad, n = 28, 8
        canvas_wh = n * CELL_SIZE + pad * 2

        # 加载背景图片（缩放适应棋盘区大小）
        try:
            pilimg = Image.open("001.png").resize((canvas_wh, canvas_wh))
            self.bg_img = ImageTk.PhotoImage(pilimg)
        except Exception as ex:
            print("载入棋盘图片出错：", ex)
            self.bg_img = None

        self.canvas = tk.Canvas(self, width=canvas_wh, height=canvas_wh,
                                highlightthickness=0, bd=0)
        self.canvas.pack(pady=8)
        # 在canvas上创建背景图片，id存着后续update_ui不会重复贴
        if self.bg_img:
            self.bg_img_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_img)
        else:
            self.bg_img_id = None
        self.canvas.bind("<Button-1>", self.on_click)

        if getattr(self, "is_replay_mode", False):
            self.replay_btns = tk.Frame(self, bg="#f3f4f2")
            self.replay_btns.pack(pady=8)
            self.btn_prev = HoverButton(self.replay_btns, text="《 上一步", font=("微软雅黑",13), width=9, bg=BUTTON_BG,
                                      fg=BUTTON_FG, command=self.replay_prev)
            self.btn_next = HoverButton(self.replay_btns, text="下一步 》", font=("微软雅黑",13), width=9, bg=BUTTON_BG,
                                      fg=BUTTON_FG, command=self.replay_next)
            self.btn_exit = HoverButton(self.replay_btns, text="退出复盘", font=("微软雅黑",13), width=11, bg=BUTTON_BG,
                                      fg=BUTTON_FG, command=self.to_menu)
            self.btn_prev.pack(side="left", padx=11)
            self.btn_next.pack(side="left", padx=11)
            self.btn_exit.pack(side="left", padx=11)
            self.btn_pause.config(state="disabled")
            self.btn_undo.config(state="disabled")
            self.btn_restart.config(state="disabled")
            self.btn_tip.config(state="disabled")
        self.update_ui()
        if not getattr(self, "is_replay_mode", False):
            self.play_game_threaded()

    def get_info_text(self):
        return self.game_info

    def apply_replay_idx(self):
        snap = self.replay_summary[self.replay_idx]
        board_arr = np.array(snap['board'])
        self.board.board = board_arr
        self.board.size = board_arr.shape[0]

    def update_ui(self):
        self.canvas.delete("all")
        n = self.board.size
        pad = 28
        # 棋盘阴影、边框
        self.round_rectangle(pad-8,pad-8,pad+n*CELL_SIZE+8,pad+n*CELL_SIZE+8, radius=22,
                             fill="#cad7c7", outline="#b3bfa9", width=0)
        self.round_rectangle(
            pad, pad, pad + n * CELL_SIZE, pad + n * CELL_SIZE, radius=20,
            fill="", outline=BOARD_EDGE, width=4)
        # 网格
        for i in range(n + 1):
            self.canvas.create_line(
                pad, pad + i * CELL_SIZE, pad + n * CELL_SIZE, pad + i * CELL_SIZE,
                fill=BOARD_LINE, width=2)
            self.canvas.create_line(
                pad + i * CELL_SIZE, pad, pad + i * CELL_SIZE, pad + n * CELL_SIZE,
                fill=BOARD_LINE, width=2)
        if getattr(self, "is_replay_mode", False):
            self.apply_replay_idx()
        for i in range(n):
            for j in range(n):
                piece = self.board.board[i][j]
                if piece != 0:
                    # 阴影
                    cx = pad + j * CELL_SIZE + CELL_SIZE // 2
                    cy = pad + i * CELL_SIZE + CELL_SIZE // 2
                    self.canvas.create_oval(
                        cx - 19, cy - 19+2, cx + 19, cy + 19+2,
                        fill="#b7bebc" if piece==BLACK else "#f2f5f8", outline="", width=0
                    )
        for i in range(n):
            for j in range(n):
                piece = self.board.board[i][j]
                if piece != 0:
                    self.draw_piece(i, j, piece, pad)
        # 可落子点、AI提示推荐
        moves = []
        if not getattr(self, "is_replay_mode", False):
            cur_color = self.current_player.color
            moves = self.board.get_legal_moves(cur_color)
        for move in moves:
            i, j = move
            cx = pad + j * CELL_SIZE + CELL_SIZE // 2
            cy = pad + i * CELL_SIZE + CELL_SIZE // 2
            r = 13
            self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                outline=HIGHLIGHT_COLOR, width=3, fill="",
                dash=(4, 3))
        # AI高亮
        if self.tip_suggest and not getattr(self, "is_replay_mode", False):
            i, j = self.tip_suggest
            cx = pad + j * CELL_SIZE + CELL_SIZE // 2
            cy = pad + i * CELL_SIZE + CELL_SIZE // 2
            r = 19
            self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                outline=TIP_COLOR, width=4, fill="", dash=(5,1)
            )
        b, w = (self.board.count() if not getattr(self, "is_replay_mode", False)
                else (int((self.board.board==BLACK).sum()), int((self.board.board==WHITE).sum())))
        text = self.get_info_text() + "   "
        text += f"●黑: {b}    ○白: {w}   "
        scoretip = get_board_score(self.board.board)
        self.score_label.config(text="当前局势：" + scoretip)
        if not getattr(self, "is_replay_mode", False):
            if self.board.is_game_over():
                if b > w:
                    text += "黑方胜！"
                elif w > b:
                    text += "白方胜！"
                else:
                    text += "平局！"
                if not hasattr(self, "saved_replay"):
                    self.saved_replay = True
                    fname = self.save_game_history_full()
                    messagebox.showinfo("棋谱已保存", f"已自动保存棋局到:\n{fname}\n可主菜单复盘")
            elif self.paused:
                text += "(已暂停)"
            else:
                cur_color = self.current_player.color
                text += f"当前回合：{'黑●' if cur_color==BLACK else '白○'}"
        else:
            snap = self.replay_summary[self.replay_idx]
            movei = self.replay_idx
            stepinfo = ""
            if movei==0:
                stepinfo = "（开局）"
            else:
                color = snap["color"]
                move = snap["move"]
                if move:
                    cstr = "黑" if color==BLACK else "白"
                    stepinfo = f"  {cstr}落子: ({move[0]+1},{move[1]+1})"
                else:
                    cstr = "黑" if color==BLACK else "白"
                    stepinfo = f"  {cstr}跳过"
            text += f"    步数：{movei+1}/{len(self.replay_summary)}{stepinfo}"
            self.score_label.config(text="当前局势：" + get_board_score(self.board.board))
        self.status_label.config(text=text)
        if hasattr(self, "btn_undo"):
            if getattr(self, "is_replay_mode", False):
                self.btn_undo.config(state="disabled")
            else:
                if len(getattr(self, "history", [])) == 0:
                    self.btn_undo.config(state="disabled")
                else:
                    self.btn_undo.config(state="normal")

    def draw_piece(self, i, j, color, pad):
        cx = pad + j * CELL_SIZE + CELL_SIZE // 2
        cy = pad + i * CELL_SIZE + CELL_SIZE // 2
        r1, r2 = 20, 13
        self.canvas.create_oval(
            cx - r1, cy - r1, cx + r1, cy + r1,
            fill=COLOR_MAP[color], outline="#3c4170", width=2
        )
        if color == BLACK:
            self.canvas.create_oval(cx - r2, cy - r2-2, cx + r2-9, cy + r2-8,
                                   fill="#babdc5", outline="", stipple="gray50")
        else:
            self.canvas.create_oval(cx - r2+3, cy - r2-2, cx + r2+3, cy + r2,
                                   fill="#ffffff", outline="", stipple="gray12")

    def on_click(self, event):
        if getattr(self, "is_replay_mode", False):
            return
        if self.paused or self.board.is_game_over():
            return
        self.tip_suggest = None
        pad = 28
        x = event.y - pad
        y = event.x - pad
        if 0 <= x < 8*CELL_SIZE and 0 <= y < 8*CELL_SIZE:
            i = int(x // CELL_SIZE)
            j = int(y // CELL_SIZE)
            move = (i,j)
            legal_moves = self.board.get_legal_moves(self.current_player.color)
            if move in legal_moves:
                self.save_history()
                self.save_full_history_snapshot(self.current_player.color, move)
                self.board.do_move(move, self.current_player.color)
                self.turn += 1
                self.swap_player()
                self.update_ui()
                self.after(120, self.play_game_threaded)

    def play_game_threaded(self):
        if getattr(self, "is_replay_mode", False):
            return
        if self.paused or self.board.is_game_over():
            self.update_ui()
            return
        if hasattr(self.current_player, 'get_move') and not isinstance(self.current_player, HumanPlayer):
            t = threading.Thread(target=self.ai_move_and_update)
            t.daemon = True
            t.start()

    def ai_move_and_update(self):
        time.sleep(0.12)
        legal_moves = self.board.get_legal_moves(self.current_player.color)
        if not legal_moves:
            self.save_full_history_snapshot(self.current_player.color, None)
            self.turn += 1
            self.swap_player
            self.after(80, self.update_ui)
            self.after(210, self.play_game_threaded)
            return
        self.save_history()
        move = self.current_player.get_move(self.board)
        if move:
            self.save_full_history_snapshot(self.current_player.color, move)
            self.board.do_move(move, self.current_player.color)
        self.turn += 1
        self.swap_player()
        self.after(45, self.update_ui)
        self.after(110, self.play_game_threaded)

    def save_history(self):
        if not hasattr(self, "history"):
            self.history = []
        self.history.append((
            self.board.board.copy(),
            self.turn,
            self.current_player
        ))
        if len(self.history) > UNDO_LIMIT:
            self.history = self.history[-UNDO_LIMIT:]

    def save_full_history_snapshot(self, color, move):
        if not hasattr(self, "recorded_moves"):
            self.recorded_moves = []
        item = {
            "board": self.board.board.tolist(),
            "color": int(color) if color in [BLACK, WHITE] else None,
            "move": list(move) if move is not None else None
        }
        self.recorded_moves.append(item)

    def undo(self):
        if getattr(self, "is_replay_mode", False):
            return
        self.tip_suggest = None
        if not hasattr(self, "history") or not self.history:
            messagebox.showinfo("提示", f"已达到悔棋步数上限（最近最多{UNDO_LIMIT}步）！")
            return
        last_board, self.turn, self.current_player = self.history.pop()
        self.board.board = last_board.copy()
        if hasattr(self, "recorded_moves") and len(self.recorded_moves) > 1:
            self.recorded_moves.pop()
        self.update_ui()

    def restart(self):
        if getattr(self, "is_replay_mode", False):
            return
        ret = messagebox.askyesno("确认", "确定要重新开始吗？")
        if not ret: return
        self.tip_suggest = None
        self.board = Board()
        self.history = []
        self.recorded_moves = []
        self.turn = 0
        self.current_player = self.player_order[0]
        self.save_full_history_snapshot("init", None)
        self.update_ui()
        self.play_game_threaded()

    def toggle_pause(self):
        if getattr(self, "is_replay_mode", False):
            return
        self.paused = not self.paused
        self.update_ui()
        if not self.paused:
            self.play_game_threaded()

    def to_menu(self):
        ret = messagebox.askyesno("提示", "返回菜单将丢失当前棋局。确定返回菜单？")
        if not ret: return
        self.pack_forget()
        self.return_menu_callback()

    def swap_player(self):
        opp = self.player_order[1] if self.current_player == self.player_order[0] else self.player_order[0]
        if self.board.get_legal_moves(opp.color):
            self.current_player = opp

    def round_rectangle(self, x1, y1, x2, y2, radius=15, **kwargs):
        points = [x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius,
            x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2,
            x1, y2, x1, y2-radius, x1, y1+radius, x1, y1]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    def replay_prev(self):
        if self.replay_idx > 0:
            self.replay_idx -= 1
            self.apply_replay_idx()
            self.update_ui()
    def replay_next(self):
        if self.replay_idx < len(self.replay_summary)-1:
            self.replay_idx += 1
            self.apply_replay_idx()
            self.update_ui()

    def save_game_history_full(self):
        folder = "replays"
        if not os.path.exists(folder):
            os.makedirs(folder)
        filetime = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        fname = f"{folder}/replay_{filetime}.json"
        fullmoves = list(self.recorded_moves)
        if not (fullmoves and np.array_equal(self.board.board, np.array(fullmoves[-1]["board"]))):
            fullmoves.append({
                "board": self.board.board.tolist(),
                "color": None,
                "move": None,
            })
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(fullmoves, f)
        return fname

    # ---- AI提示功能 ----
    def ai_tip_move(self):
        if getattr(self, "is_replay_mode", False) or self.board.is_game_over():
            return
        color = self.current_player.color
        legal_moves = self.board.get_legal_moves(color)
        if not legal_moves:
            messagebox.showinfo("AI提示", "当前无可下棋点！")
            return
        tip_ai = MiniMaxAI(color, depth=3, eval_fn=base_eval)
        move = tip_ai.get_move(self.board)
        if move:
            self.tip_suggest = move
            self.update_ui()
        else:
            messagebox.showinfo("AI提示", "无推荐落子！")

class OthelloApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Othello 黑白棋")
        self.geometry("742x830")
        self.resizable(True, True)

        # # 背景图片半透明
        # try:
        #     im = Image.open("001.png").convert("RGBA")
        #     width, height = 742, 830
        #     im = im.resize((width, height))
        #     alpha = 0.28  # 透明度，0.0~1.0，越小越淡
        #     # 透明度处理
        #     alpha_layer = Image.new("L", (width, height), int(255*alpha))
        #     im.putalpha(alpha_layer)
        #     # 半透明白色遮罩，防止花纹影响内容
        #     overlay = Image.new("RGBA", (width, height), (255,255,255,64))
        #     visual = Image.alpha_composite(im, overlay)
        #     self.bg_image = ImageTk.PhotoImage(visual)
        #     self.canvas_bg = tk.Canvas(self, width=width, height=height, highlightthickness=0, bd=0)
        #     self.canvas_bg.pack(fill="both", expand=True)
        #     self.canvas_bg.create_image(0, 0, anchor="nw", image=self.bg_image)
        # except Exception as ex:
        #     print("未能设定图片背景,", ex)
        #
        # # 关键：所有内容添加到这个frame
        # self.main_container = tk.Frame(self.canvas_bg, bg="", highlightthickness=0)
        # self.canvas_bg.create_window(0, 0, anchor="nw", window=self.main_container, width=742, height=830)

        self.main_container = tk.Frame(self, bg="#f7faf6")
        self.main_container.pack(fill="both", expand=True)

        self.menu_frame = None
        self.game_frame = None
        self.show_menu()

    def show_menu(self):
        if self.game_frame:
            self.game_frame.destroy()
            self.game_frame = None
        self.menu_frame = MainMenuFrame(self.main_container, self.start_game)
        self.menu_frame.pack(fill=tk.BOTH, expand=True)

    def start_game(self, modeconf):
        if self.menu_frame:
            self.menu_frame.destroy()
            self.menu_frame = None
        self.game_frame = GameFrame(self.main_container, modeconf, self.show_menu)
        self.game_frame.pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    OthelloApp().mainloop()