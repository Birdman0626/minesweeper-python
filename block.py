from enum import Enum
from torch.nn import functional as F
import torch

NUMBER_COLOR = [
    "","blue","green","red","darkblue",
    "darkred","lightblue","black","gray"
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
    