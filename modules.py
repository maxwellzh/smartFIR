import random
import curses
import math
import itertools
import torch
from torch import select
import torchvision
import torch.nn as nn
import torch.nn.functional as F


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, 5, 1, padding=0)
        self.bn1 = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 32, 3, 1)
        self.bn2 = nn.BatchNorm2d(32)
        self.maxpool = nn.MaxPool2d(3, 2, 1)
        self.lstm = nn.LSTM(800, 512, 3, batch_first=True, dropout=0.2)
        self.fc1 = nn.Linear(512, 225)

    def forward(self, x, h_agent, c_agent):
        x = torch.tensor(x).view(1, 1, 15, 15).float()
        x = self.conv1(x)
        x = F.relu(x)
        x = self.bn1(x)
        x = self.conv2(x)
        x = F.relu(x)
        x = self.bn2(x)
        x = self.maxpool(x)
        x = torch.flatten(x, 1)
        # print(x.size())
        if h_agent is None:
            x, (h, c) = self.lstm(torch.unsqueeze(x, 0))
        else:
            x, (h, c) = self.lstm(torch.unsqueeze(x, 0), (h_agent, c_agent))

        x = self.fc1(torch.flatten(x[0], 1))
        output = F.softmax(x, dim=1)
        return output, h.detach(), c.detach()



def getPos(pos):
    if pos < 0 or pos > 224:
        print("getPos() error. Invalid input.")
        exit(-1)
    return (int(pos//15), int(pos % 15))


def indexPos(x, y):
    if x < 0 or x > 14 or y < 0 or y > 14:
        return -1
        #print("indexPos() error. Invalid input (%d, %d)" % (x, y))
        #exit(-1)
    return int(x * 15 + y)


def displayinfo(win, row, col, info):
    win.addstr(row, col, info)
    win.refresh()
    return


def display(win, pos, black, color=None):
    showstr = '●' if black else '◯'
    row, col = getPos(pos)
    if color != None:
        win.addstr(row + 2, 2 * col + 1, showstr, color)
    else:
        win.addstr(row + 2, 2 * col + 1, showstr)
    win.refresh()
    return


def checkrow(q, s, win):
    countwin = 0
    lastone = 0
    for pos in q:
        if pos < 0 or pos > 224:
            continue
        if s[pos] != lastone:
            countwin = s[pos]
        else:
            countwin += s[pos]
        lastone = s[pos]
        if countwin == 5:
            return True
        elif countwin == -5:
            return False
    return None


class Board(object):
    def __init__(self, win=None):
        if win != None:
            displayinfo(win, 7, 34, '▶ black ●')
            displayinfo(win, 11, 34, '  white ◯')
        self.status = [0 for _ in range(225)]
        self.turn = True    # True for black, False for white
        self.win = win
        self.steps = []
        self.countsteps = 0

    def showboard(self):
        print("")
        for row in range(15):
            for col in range(15):
                if self.status[row*15+col] == 1:
                    print("◯ ", end='')
                elif self.status[row*15+col] == -1:
                    print("● ", end='')
                else:
                    print("  ", end='')
            print("\r")

    def reset(self):
        if self.win != None:
            self.win.clear()
            displayinfo(self.win, 7, 34, '▶ black ●')
            displayinfo(self.win, 11, 34, '  white ◯')
        self.status = [0 for _ in range(225)]
        self.turn = True    # True for black, False for white
        self.steps = []
        self.countsteps = 0

    def checkWin(self, pos):
        x = int(pos//15)
        y = int(pos % 15)
        if x not in range(15) or y not in range(15):
            print("Position of chessman invalid.")
            exit(-1)

        # Four directions of probale win
        Q = []
        Q.append([indexPos(x + i, y) for i in range(-4, 5)])
        Q.append([indexPos(x, y + i) for i in range(-4, 5)])
        Q.append([indexPos(x + i, y + i) for i in range(-4, 5)])
        Q.append([indexPos(x + i, y - i) for i in range(-4, 5)])
        for q in Q:
            r = checkrow(q, self.status, self.win)
            if r != None:
                return r
        return None

    def gameover(self, pos):
        if self.countsteps == 225:
            if self.win != None:
                displayinfo(self.win, 0, 13, "Draw")
            else:
                print('Draw')
            return True

        winplayer = self.checkWin(pos)

        if winplayer == None:
            return False

        if self.win != None:
            if winplayer:
                displayinfo(self.win, 0, 6, "Black player wins!")
            else:
                displayinfo(self.win, 0, 6, "White player wins!")

        return True

    def put(self, pos):
        getPos(pos)     # check if position is valid

        if self.status[pos] != 0:
            print("There is already a chessman at the position.")
            exit(-1)

        if self.win != None:
            displayinfo(self.win, 9, 36, ('[%2d,%2d]' %
                                          (getPos(pos)[0], getPos(pos)[1])))
        self.turn = not self.turn
        self.steps.append(pos)
        self.countsteps += 1

        if self.countsteps % 2 == 0:
            self.status[pos] = -1
            if self.win != None:
                display(self.win, pos, False)
                displayinfo(self.win, 7, 34, '▶')
                displayinfo(self.win, 11, 34, ' ')
        else:
            self.status[pos] = 1
            if self.win != None:
                display(self.win, pos, True)
                displayinfo(self.win, 7, 34, ' ')
                displayinfo(self.win, 11, 34, '▶')

        if self.gameover(pos):
            # deal with gameover situation
            pass
            return False
        else:
            return True


class Agent(object):
    def __init__(self, chessboard, loadmodel=False, path=None, eval=False):
        self.board = chessboard
        self.model = None
        if loadmodel:
            self.model = torch.load(path)
        else:
            self.model = Net()
        if eval:
            self.model.eval()
        self.optimizer = torch.optim.Adam(self.model.parameters())
        self.lastvalue = None
        self.step = None
        self.h = None
        self.c = None
        #self.model.eval()

    def policy(self):
        return nnpolicy(self)

    def update(self):
        # if enemy_step is None:
        #     enemy_step = 112
        # loss = F.nll_loss(self.step, torch.tensor([enemy_step]))
        # loss = F.cross_entropy(self.step, ValuesJudge(self.board))
        # loss.backward()
        # self.optimizer.step()
        # self.optimizer.zero_grad()
        pass

    def reset(self):
        self.lastvalue = None
        self.h = None
        self.c = None

    def save(self, path):
        torch.save(self.model, path)


class randagent(object):
    def __init__(self, chessboard):
        self.board = chessboard

    def policy(self):
        return randpolicy(self)


def showValue(board: Board, value: torch.Tensor):
    board.showboard()
    status = board.status
    vals = "·:+?*@"
    value = value.tolist()[0]
    value = [int(x*6) for x in value]
    # print(value[:10])
    for row in range(15):
        for col in range(15):
            print(vals[value[row*15+col]]+' ', end='')
        print("\r")


def randpolicy(agent):
    while True:
        out = random.randint(0, 224)
        if out in agent.board.steps:
            continue
        else:
            return out


def nnpolicy(agent: Agent):
    # 当前可落子区域
    free = [int(x) for x in range(225) if x not in agent.board.steps]
    agent.step, agent.h, agent.c = agent.model.forward(
        agent.board.status, agent.h, agent.c)

    agent.lastvalue = ValuesJudge(agent.board, agent.lastvalue)
    loss = F.mse_loss(agent.step, agent.lastvalue)
    loss.backward()
    agent.optimizer.step()
    agent.optimizer.zero_grad()

    return free[torch.argmax(agent.step[0][free])]


def ValuesJudge(board: Board, lastscore=None):
    if lastscore is not None:
        Range = []
        for step in board.steps[-2:]:
            row, col = step//15, step-15*(step//15)
            Range += list(itertools.product(list(range(row-4, row+5)),
                                            list(range(col-4, col+5))))

        Range = list(dict.fromkeys(Range))
        Range = [(x, y) for (x, y) in Range if (
            x < 15 and x > -1 and y < 15 and y > -1)]

    else:
        Range = [(idx//15, idx-15*(idx//15)) for idx in range(225)]
    # initial score all set to 0
    score = torch.zeros([15, 15])

    # pad board to 23*23
    status = torch.Tensor(board.status).view(15, 15).float()
    status = F.pad(status, (4, 4, 4, 4))
    # print(status.size())

    for row, col in Range:

        if status[row][col] != 0:
            # occupied set to -inf
            score[row][col] = -torch.tensor(float('inf'))
            continue
        score[row][col] += torch.sum(status[row:row+9, col:col+9])

        count_line = 0
        for i in range(1, 5):
            if status[row+4-i][col+4] == 1:
                count_line += 1
            else:
                break
        for i in range(1, 5):
            if status[row+4+i][col+4] == 1:
                count_line += 1
            else:
                break
        if count_line >= 4:
            score[row][col] = torch.tensor(float('inf'))
            break
        elif count_line > 0:
            score[row][col] += -math.log(1/float(count_line)-1/5)

        count_line = 0
        for i in range(1, 5):
            if status[row+4-i][col+4-i] == 1:
                count_line += 1
            else:
                break
        for i in range(1, 5):
            if status[row+4+i][col+4+i] == 1:
                count_line += 1
            else:
                break
        if count_line >= 4:
            score[row][col] = torch.tensor(float('inf'))
            break
        elif count_line > 0:
            score[row][col] += -math.log(1/float(count_line)-1/5)

        count_line = 0
        for i in range(1, 5):
            if status[row+4][col+4-i] == 1:
                count_line += 1
            else:
                break
        for i in range(1, 5):
            if status[row+4][col+4+i] == 1:
                count_line += 1
            else:
                break
        if count_line >= 4:
            score[row][col] = torch.tensor(float('inf'))
            break
        elif count_line > 0:
            score[row][col] += -math.log(1/float(count_line)-1/5)

        count_line = 0
        for i in range(1, 5):
            if status[row+4+i][col+4-i] == 1:
                count_line += 1
            else:
                break
        for i in range(1, 5):
            if status[row+4-i][col+4+i] == 1:
                count_line += 1
            else:
                break
        if count_line >= 4:
            score[row][col] = torch.tensor(float('inf'))
            break
        elif count_line > 0:
            score[row][col] += -math.log(1/float(count_line)-1/5)

        # for enemy chess
        count_line = 0
        for i in range(1, 5):
            if status[row+4-i][col+4] == -1:
                count_line += 1
            else:
                break
        for i in range(1, 5):
            if status[row+4+i][col+4] == -1:
                count_line += 1
            else:
                break
        if count_line >= 4:
            score[row][col] = torch.tensor(float('inf'))
            break
        elif count_line > 0:
            score[row][col] += -math.log(1/float(count_line)-1/5)

        count_line = 0
        for i in range(1, 5):
            if status[row+4-i][col+4-i] == -1:
                count_line += 1
            else:
                break
        for i in range(1, 5):
            if status[row+4+i][col+4+i] == -1:
                count_line += 1
            else:
                break
        if count_line >= 4:
            score[row][col] = torch.tensor(float('inf'))
            break
        elif count_line > 0:
            score[row][col] += -math.log(1/float(count_line)-1/5)

        count_line = 0
        for i in range(1, 5):
            if status[row+4][col+4-i] == -1:
                count_line += 1
            else:
                break
        for i in range(1, 5):
            if status[row+4][col+4+i] == -1:
                count_line += 1
            else:
                break
        if count_line >= 4:
            score[row][col] = torch.tensor(float('inf'))
            break
        elif count_line > 0:
            score[row][col] += -math.log(1/float(count_line)-1/5)

        count_line = 0
        for i in range(1, 5):
            if status[row+4+i][col+4-i] == -1:
                count_line += 1
            else:
                break
        for i in range(1, 5):
            if status[row+4-i][col+4+i] == -1:
                count_line += 1
            else:
                break
        if count_line >= 4:
            score[row][col] = torch.tensor(float('inf'))
            break
        elif count_line > 0:
            score[row][col] += -math.log(1/float(count_line)-1/5)

    return F.softmax(score.view(1, -1), dim=0)
