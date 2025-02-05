from visualize import Visualizer
from game import Game
import torch
from threading import Thread



def to_record(difficulty):
    difficulty_set = [
        (9, 9, 10),
        (16, 16, 40),
        (30, 16, 99),
    ]
    game = Game(*difficulty_set[difficulty], auto_open=False)
    visualizer = Visualizer(game, True)
    visualizer.start()
    game.log_into('./log.txt')

def input_loop(game:Game, visualizer:Visualizer):
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
        game.act(t, visualizer)

def by_cmd():
    game, end_state, record = Game.load_from_file('./log.txt')
    visualizer = Visualizer(game, False)
    t = Thread(target=input_loop, args = (game, visualizer))
    t.start()
    visualizer.start()


# by_cmd()
to_record(1)


