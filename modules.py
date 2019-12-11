import random
import curses
import torch
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
        self.fc1 = nn.Linear(5 * 5 * 32, 225)

    def forward(self, x):
        x = torch.tensor(x).view(1, 1, 15, 15).float()
        x = self.conv1(x)
        x = F.relu(x)
        x = self.bn1(x)
        x = self.conv2(x)
        x = F.relu(x)
        x = self.bn2(x)
        x = self.maxpool(x)
        x = self.fc1(torch.flatten(x, 1))
        output = F.log_softmax(x, dim=1)
        return output


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


class board(object):
    def __init__(self, win=None):
        if win != None:
            displayinfo(win, 7, 34, '▶ black ●')
            displayinfo(win, 11, 34, '  white ◯')
        self.status = [0 for _ in range(225)]
        self.turn = True    # True for black, False for white
        self.win = win
        self.steps = []
        self.countsteps = 0

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


class agent(object):
    def __init__(self, chessboard, loadmodel=False, path=None, eval=False):
        self.board = chessboard
        self.model = None
        if loadmodel:
            self.model = torch.load(path)
        else:
            self.model = Net()
        if eval:
            self.model.eval()
        self.x = None
        self.free = []
        self.optimizer = torch.optim.Adam(self.model.parameters())
        #self.model.eval()

    def policy(self):
        return nnpolicy(self)

    def update(self):
        self.optimizer.zero_grad()
        out = self.model.forward(self.x)
        loss = F.nll_loss(out, torch.tensor([self.board.steps[-1]]))
        loss.backward()
        self.optimizer.step()

    def save(self, path):
        torch.save(self.model, path)


class simpleagent(object):
    def __init__(self, chessboard):
        self.board = chessboard

    def policy(self):
        return serialpolicy(self)


def randpolicy(Agent):
    while True:
        out = random.randint(0, 224)
        if out in Agent.board.steps:
            continue
        else:
            return out


def nnpolicy(Agent):
    Agent.x = Agent.board.status
    Agent.free = [int(x) for x in range(225) if x not in Agent.board.steps]
    out = Agent.model.forward(Agent.x)
    return Agent.free[torch.argmax(out[0][Agent.free])]


def serialpolicy(Agent):
    out = 0
    for i in range(225):
        if i not in Agent.board.steps:
            out = i
            break
    return out
