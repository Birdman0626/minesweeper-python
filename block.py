from enum import Enum
from torch.nn import functional as F
import torch

NUMBER_COLOR = [
    "",
    "#0000ff",
    "#008000",
    "#ff0000",
    "#000080",
    "#800000",
    "#008080",
    "#000000",
    "#808080"
]


class Block:
    class State(Enum):
        HIDDEN = 0
        MARKED = 1
        QUES = 2
        OPENED = 3
    MINE = 9

    def __init__(self, value:int = None):
        self.value = value or 0 # value can be 1~9, None/0(void), 10(mine)
        self.state = self.State.HIDDEN
        self.__has_set_eff = False # 每个block，有且只有一次有效操作

    def is_eff_op(self):
        '''
        判断是否是有效操作

        Returns:
        ----
            flag(bool): 
            - True代表本次操作确实有效；
            - False代表设置失败
        '''
        # 如果已经设置过了，那任何对这个格子state产生改变的操作就不应该再有效了
        if self.__has_set_eff:
            return False
        # 如果没有设置过，判断一下是否确实处于有效状态
        self.__has_set_eff = (
            self.value != Block.MINE and 
            self.state == Block.State.OPENED
        ) or (
            self.value == Block.MINE and 
            self.state == Block.State.MARKED
        ) #是雷标了/非雷开了，都算有效，这个表达式就是True，直接赋给成员用来表示记录过了
        return self.__has_set_eff

    def tensorize(self, state_emb = None, value_emb = None):
        # two emb: State + value
        s_emb = (
            state_emb(self.state) if state_emb
            else F.one_hot(self.state, 4)
        )
        v_emb = (
            value_emb(self.value) if value_emb
            else F.one_hot(self.value, 10)
        )
        return torch.cat((s_emb, v_emb), dim=0)

    @property
    def color(self):
        return NUMBER_COLOR[self.value]
    