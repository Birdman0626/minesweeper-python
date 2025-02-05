import tkinter as tk
from game import Game
from block import Block
from tkinter import messagebox

class Visualizer:
    def __init__(self, game:Game, allow_click = False):
        self.game = game
        self.has_start = False
        self.__root = tk.Tk('Game')
        self.__labels:list[list[tk.Label]] = []
        block_frame = tk.Frame(self.__root)
        info_frame = tk.Frame(self.__root)
        
        for x in range(self.game.width):
            l = []
            for y in range(self.game.height):
                lbl = tk.Label(
                    block_frame,text='', bg='gray', 
                    width=3, height=1,
                    borderwidth=1, relief='solid'
                )
                if allow_click: 
                    lbl.bind('<Button-1>', lambda event, x_=x, y_=y: self.__on_button_1(event, x_, y_))
                    lbl.bind('<Button-3>', lambda event, x_=x, y_=y: self.__on_button_3(event, x_, y_))
                    lbl.bind('<Double-Button-1>',lambda _, x_=x, y_=y: self.__on_double_button_1(x_, y_))
                lbl.grid(column=x, row=y)
                l.append(lbl)
            self.__labels.append(l)
            
        self.__mine_left = tk.Label(
            info_frame, 
            text=f'剩余雷数: {self.game.mine_number}\n{self.game.efficient_click}'
        )
        self.__mine_left.pack()
        info_frame.pack()
        block_frame.pack()

    def start(self):
        self.has_start = True
        self.__root.mainloop()

    def __on_button_1(self, event, x, y):
        if event.state & 0x0080==0:
            self.game.record(0, x, y)
            changed = self.game.open_one(x, y)
            self.update(0, changed)
        else:
            self.game.record(1, x, y)
            changed = self.game.open_group(x, y)
            self.update(1, changed)

    def __on_button_3(self, event, x, y):
        if event.state & 0x0100==0:
            self.game.record(2, x, y)
            changed = self.game.mark_one(x, y)
            self.update(2, changed)
        else:
            self.game.record(1, x, y)
            changed = self.game.open_group(x, y)
            self.update(1, changed)
    
    def __on_double_button_1(self, x, y):
        self.game.record(1, x, y)
        changed = self.game.open_group(x, y)
        self.update(1, changed)

    def update(self, cmd:int, changed:list[tuple[Block, int, int]]):
        self.game.update_efficient(cmd, changed)
        for _, cx, cy in changed:
            # print(f'{cx}, {cy}')
            self.__update_one(cx, cy)
        self.__mine_left.config(
            text=f"剩余雷数: {self.game.mine_number}\n"
            f"{self.game.efficient_click}"
        )
        # 游戏结局显示
        if self.game.state == Game.State.SUCCESS:
            messagebox.showinfo('游戏结束', '你成功了')
        elif self.game.state == Game.State.FAILED:
            messagebox.showinfo('游戏结束', '你失败了')
            for block,x,y in self.game.iter_block_with_pos(
                lambda b:b.value==Block.MINE
            ):
                block.state = Block.State.OPENED
                self.__update_one(x, y)

    def __update_one(self, x:int, y:int):
        blk = self.game.block(x, y)
        lbl = self.__labels[x][y]
        if blk.state == Block.State.HIDDEN:
            lbl.config(
                text='', bg='gray', 
                image=None
            )
        elif blk.state == Block.State.MARKED:
            # self.__label.config(
            #     text='', bg='gray', 
            #     image=Block.__FLAG_IMG
            # )
            lbl.config(
                text='🚩', bg='gray',
                image=None
            )
        elif blk.state == Block.State.QUES:
            lbl.config(
                text='?', bg='gray',
                image=None
            )
        elif blk.state == Block.State.OPENED:
            if blk.value == Block.MINE:
                # self.__label.config(
                #     text='', bg='white',
                #     image=Block.__MINE_IMG
                # )
                lbl.config(
                    text='💣', bg='white',
                    image=None
                )
            elif blk.value == 0:
                lbl.config(
                    text='', bg='white',
                    image=None
                )
            else:
                lbl.config(
                    text=str(blk.value), bg='white',
                    fg=blk.color,
                    image=None
                )
        
