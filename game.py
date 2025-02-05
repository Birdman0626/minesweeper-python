from enum import Enum
from block import Block, torch
import random

class Game:

    class State(Enum):
        PREPARE = 0
        GAMING = 1
        SUCCESS = 2
        FAILED = 3
    
    def __init__(self, width:int, height:int, mine_number:int = 0, auto_open = False):
        self.state = Game.State.PREPARE
        self.record:list[tuple[int, int, int]] = []
        self.width = width
        self.height = height
        self.mine_number = mine_number
        self.__auto_open = auto_open

        self.__blocks = [[
            Block()
            for y in range(height)
        ] for x in range(width) ]
    
    def __8_neightbours(self, x:int, y:int):
        return [
            (i, j)
            for i in range(x-1, x+2)
            if 0<=i<self.width
            for j in range(y-1, y+2)
            if 0<=j<self.height
        ]
    
    def iter_block(self, filter = None):
        for l in self.__blocks:
            for block in l:
                if (filter is None) or filter(block):
                    yield block
    def iter_block_with_pos(self, filter = None):
        for x in range(self.width):
            for y in range(self.height):
                block = self.__blocks[x][y]
                if (filter is None) or filter(block):
                    yield block, x, y

    def block(self, x, y):
        return self.__blocks[x][y]

    def __init_mines(self, x, y):
        assert self.state == Game.State.PREPARE
        for _ in range(self.mine_number):
            while True:
                rx = random.randint(0, self.width-1)
                ry = random.randint(0, self.height-1)
                block = self.__blocks[rx][ry]
                if block.value != Block.MINE and (x,y)!=(rx,ry):# mine and not here
                    block.value = Block.MINE
                    break
        for block, x, y in self.iter_block_with_pos(
            lambda b: b.value!=Block.MINE
        ): # 遍历所有非雷区
            assert block.value==0, "@author block init value != 0"
            block.value = sum([
                int(self.__blocks[nx][ny].value==Block.MINE)
                for nx, ny in self.__8_neightbours(x,y)
            ])
        self.state = Game.State.GAMING

    def __game_over(self, end_state:State):
        if self.state != Game.State.GAMING:
            return
        if end_state == Game.State.FAILED:
            print('你失败了')
        elif end_state == Game.State.SUCCESS:
            print('你成功了')
        else:
            raise RuntimeError("@Author 怎么Game over还能传进来别的")
        self.state = end_state

    def open_one(self, x:int, y:int):
        # 没初始化先初始化
        if self.state==Game.State.PREPARE:
            self.__init_mines(x, y)
        # 检查无需打开的情况
        if self.state != Game.State.GAMING:
            return
        block = self.__blocks[x][y]
        if block.state!=Block.State.HIDDEN:
            return
        # 打开
        block.state = Block.State.OPENED
        if block.value == 0: # void
            self.open_void(x, y)
        elif block.value == Block.MINE: # mine
            self.__game_over(Game.State.FAILED)
            return
        self.record.append((0, x, y))
        if self.__auto_open:
            self.open_group(x, y)
        # 判断胜利
        for block in self.iter_block(lambda b:b.value!=Block.MINE):
            # 遍历所有非雷区
            if block.state != Block.State.OPENED:
                return
        self.__game_over(Game.State.SUCCESS)

    def open_group(self, x:int, y:int):
        if self.state!=Game.State.GAMING:
            return
        block = self.__blocks[x][y]
        if block.state!=Block.State.OPENED: # 只能双击自动打开已打开的
            return
        marked_cnt = sum([
            int(self.__blocks[nx][ny].state == Block.State.MARKED)
            for nx,ny in self.__8_neightbours(x, y)
        ])
        if marked_cnt < block.value:
            return # 没标记到个数不能打开
        # self.record.append((1, x, y))
        for nx, ny in self.__8_neightbours(x, y):
            block = self.__blocks[nx][ny]
            if block.value!=Block.MINE and block.state==block.State.HIDDEN:
                # 不是雷、没打开：打开它
                self.open_one(nx, ny)
            elif block.value!=Block.MINE and block.state==block.State.MARKED:
                # 不是雷、标记了：误标、炸之
                self.__game_over(Game.State.FAILED)

    def open_void(self, x:int, y:int):
        if self.state!=Game.State.GAMING:
            return
        for nx, ny in self.__8_neightbours(x, y):
            block = self.__blocks[nx][ny]
            if block.value!=Block.MINE and block.state==block.State.HIDDEN:
                # 不是雷、没打开：打开之
                self.open_one(nx, ny)
   
    def mark_one(self, x:int, y:int):
        if self.state!=Game.State.GAMING:
            return 
        block = self.__blocks[x][y]
        self.record.append((2, x, y))
        match block.state:
            case Block.State.OPENED:
                return
            case Block.State.HIDDEN:
                block.state = Block.State.MARKED
                self.mine_number -= 1
            case Block.State.MARKED:
                block.state = Block.State.QUES
                self.mine_number += 1
            case Block.State.QUES:
                block.state = Block.State.HIDDEN
        if self.__auto_open:
            for nx, ny in self.__8_neightbours(x, y):
                self.open_group(nx, ny)



    def tensorize(self, state_emb=None, value_emb=None):
        return torch.cat([
            m.tensorize(state_emb, value_emb)
            for m in self.iter_block()
        ], dim=0)

    def act(self, action:torch.Tensor, visualizer = None):
        '''
        通过one-hot向量来控制
        
        Param:
        ----
            action(Tensor): one-hot向量+坐标拼在一起的行动向量。
            [单击, 双击, 右击, x, y]
        '''
        click_key = torch.argmax(action[0:3])
        x, y = int(action[3]), int(action[4])
        l = len(self.record)
        if click_key == 0:
            self.open_one(x, y)
        elif click_key == 1:
            self.open_group(x, y)
        elif click_key == 2:
            self.mark_one(x, y)
        if visualizer:
            visualizer.update(l)

    
    def log_into(self, log_file):
        assert self.state == Game.State.FAILED or self.state == Game.State.SUCCESS
        with open(log_file, 'w+') as f:
            # 地图信息
            f.write(f'{self.width} {self.height}\n')
            for y in range(self.height):
                l = ' '.join([
                    f'{self.__blocks[x][y].value}'
                    for x in range(self.width)
                ])
                f.write(l+'\n')
            # 操作信息
            f.write('0\n' if self.state==Game.State.SUCCESS else '1\n')
            for action, x, y in self.record:
                f.write(f'{action} {x} {y}\n')

    @staticmethod
    def load_from_file(file_path, auto_open = False):
        with open(file_path, 'r') as f:
            # 加载地图信息
            width, height = [int(i) for i in f.readline().strip().split(' ')]
            game = Game(width, height, 0, auto_open=auto_open)
            for y in range(height):
                l = [int(i) for i in f.readline().strip().split(' ')]
                assert len(l) == width
                for x, v in enumerate(l):
                    game.__blocks[x][y].value = v
                    if v == Block.MINE:
                        game.mine_number += 1
            # 加载记录结局
            end_game_state = (
                Game.State.SUCCESS 
                if f.readline().strip()=='0' 
                else Game.State.FAILED
            )
            # 加载操作过程
            record:list[torch.Tensor] = []
            for l in f.readlines():
                cmd, x, y = [int(i) for i in l.strip().split()]
                t = torch.tensor([0,0,0,0,0])
                t[int(cmd)] = 1
                t[-2:] = torch.tensor([x, y])
                record.append(t)
        return game, end_game_state, record
