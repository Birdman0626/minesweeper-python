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
        for x in range(self.game.width):
            l = []
            for y in range(self.game.height):
                lbl = tk.Label(
                    self.__root,text='', bg='gray', 
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

    def start(self):
        self.has_start = True
        self.__root.mainloop()

    def __on_button_1(self, event, x, y):
        l = len(self.game.record)
        if event.state & 0x0080==0:
            self.game.open_one(x, y)
        else:
            self.game.open_group(x, y)
        self.update(l)

    def __on_button_3(self, event, x, y):
        l = len(self.game.record)
        if event.state & 0x0100==0:
            self.game.mark_one(x, y)
        else:
            self.game.open_group(x, y)
        self.update(l)
    
    def __on_double_button_1(self, x, y):
        l = len(self.game.record)
        self.game.open_group(x, y)
        self.update(l)

    def update(self, old_record_len:int):
        if self.game.state == Game.State.SUCCESS:
            messagebox.showinfo('游戏结束', '你成功了')
        elif self.game.state == Game.State.FAILED:
            messagebox.showinfo('游戏结束', '你失败了')
            for block,x,y in self.game.iter_block_with_pos(
                lambda b:b.value==Block.MINE
            ):
                block.state = Block.State.OPENED
                self.__update_one(x, y)
        for cmd, cx, cy in self.game.record[old_record_len:]:
            # print(f'\n{cmd}, {cx}, {cy}')
            if cmd == 0 or cmd == 2:
                self.__update_one(cx, cy)

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
                text='旗', bg='gray',
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
                    text='雷', bg='white',
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
        
