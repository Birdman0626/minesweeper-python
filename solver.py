from block import Block, torch
from game import Game
from visualize import Visualizer

class Solver:
    def __init__(self, game: Game, visualizer: Visualizer = None):
        self.game = game
        self.probed_cells = []
        self.visualizer = visualizer
        
    def make_act(self, click_key, x, y):
        t = torch.tensor([0,0,0,0,0])
        t[int(click_key)] = 1
        t[-2:] = torch.tensor([x, y])
        return t
    
    def count_attr(self, x, y):
        unprobed = 0
        absmines = 0
        for block in self.game.iter_neighbours(x, y, 1):
            if block.state == Block.State.HIDDEN: unprobed += 1
            if block.value == Block.MINE: absmines += 1
            if block.state == Block.State.MARKED: absmines -= 1
        return unprobed, absmines
    
    def count_unshared(self, xp, yp, xq, yq):
        unshared = 0
        for _, x, y in self.game.iter_neighbours_with_pos(xq, yq, 1, lambda b: b.state == Block.State.HIDDEN):
            if (abs(x-xp) >= 2) or (abs(y - yp) >= 2): unshared += 1
        return unshared
            
    def infer_dual(self, xp, yp, xq, yq):
        unprobedp, absminesp = self.count_attr(xp, yp)
        unprobedq, absminesq = self.count_attr(xq, yq)
        unsharedq = self.count_unshared(xp, yp, xq, yq)
        action: int = None
        if(absminesq - absminesp == unsharedq): action = 0
        elif (absminesq - absminesp == unprobedq - unprobedp - unsharedq): action = 2
        if action is not None:
            modified = False
            for _, x, y in self.game.iter_neighbours_with_pos(xp, yp, 1, lambda b: b.state == Block.State.HIDDEN):
                if (abs(x-xq) >= 2) or (abs(y - yq) >= 2):
                    modified = True
                    # if action == 0: 
                    #     self.game.act(self.make_act(action, x, y))
                    # elif action == 1: 
                    #     self.game.act(self.make_act(action, x, y))
                    self.probed_cells.extend(self.game.act(self.make_act(action, x, y), self.visualizer))
            if not modified: action = None
        return action

    def infer(self):
        if self.game.state != Game.State.GAMING: return None
        if len(self.probed_cells) == 0: return None
        
        repush = []
        ret = None
        while len(self.probed_cells) > 0:
            block, xp, yp = self.probed_cells.pop()
            if block.state == Block.State.OPENED or block.state == Block.State.MARKED:
                action = self.infer_dual(xp, yp, -2, -2)
                if action is not None:
                    ret = (action, xp, yp)
                    break
                
                keep = False
                stop = False
                for neighbour_block, x, y in self.game.iter_neighbours_with_pos(xp, yp, 2):
                    if stop: break
                    if neighbour_block.state == Block.State.HIDDEN: keep = True
                    if neighbour_block.state == Block.State.OPENED or neighbour_block.state == Block.State.MARKED:
                        action = self.infer_dual(xp, yp, x, y)
                        if action is not None: 
                            ret = (action, xp, yp)
                            stop = True
                            
                if keep: repush.append((block, xp, yp))
                if stop: break
                
        self.probed_cells.extend(repush)
        return ret   
    
    def run(self, res = None):
        if res: self.probed_cells.extend(res)
        return self.infer()
        
        
         