from visualize import Visualizer
from game import Game
import torch
from threading import Thread
from solver import Solver
import time



def to_record(difficulty):
    difficulty_set = [
        (9, 9, 10),
        (16, 16, 40),
        (30, 16, 99),
    ]
    game = Game(*difficulty_set[difficulty], auto_open=True, seed=1919810)
    visualizer = Visualizer(game, True)
    visualizer.start()
    game.log_into('./log.txt')

def input_loop(game:Game, visualizer:Visualizer, solver: Solver = None):
    print('[单击, 双击, 右击]')
    while (
        visualizer.has_start and 
        (game.state not in (Game.State.SUCCESS, Game.State.FAILED))
    ):
        cmd = input('你的操作代码: ')
        if cmd == '*':
            break
        x = int(input('x: '))
        y = int(input('y: '))
        t = torch.tensor([0,0,0,0,0])
        t[int(cmd)] = 1
        t[-2:] = torch.tensor([x, y])
        changes = game.act(t, visualizer)
        if solver: 
            while True:
                time.sleep(0.5)
                ret_ops = solver.run(changes)
                if ret_ops is None: break
                

def by_cmd(x):
    #game, end_state, record = Game.load_from_file('./log.txt')
    difficulty_set = [
        (9, 9, 10),
        (16, 16, 40),
        (30, 16, 99),
    ]
    game = Game(*difficulty_set[x], auto_open=True, seed=1919810)
    visualizer = Visualizer(game, False)
    solver = Solver(game, visualizer)
    t = Thread(target=input_loop, args = (game, visualizer, solver))
    t.start()
    visualizer.start()


by_cmd(2)
#to_record(0)


