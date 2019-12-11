import random
import curses


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
    for i, pos in enumerate(q):
        if pos < 0 or pos > 224:
            continue
        if s[pos] != lastone:
            countwin = s[pos]
        else:
            countwin += s[pos]
        lastone = s[pos]
        if countwin == 5:
            for j in q[i-4:i+1]:
                display(win, j, True)
            return True
        elif countwin == -5:
            for j in q[i-4:i+1]:
                display(win, j, False)
            return False
    return None


class board(object):
    def __init__(self, win):
        displayinfo(win, 7, 34, '▶ black ●')
        displayinfo(win, 10, 34, '  white ◯')
        self.status = [0 for _ in range(225)]
        self.turn = True    # True for black, False for white
        self.win = win
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
            print("Draw.")
            return True

        winplayer = self.checkWin(pos)

        if winplayer == None:
            return False

        if winplayer:
            displayinfo(self.win, 0, 6, "Black player wins!")
        else:
            displayinfo(self.win, 0, 6, "White player wins!")
        return True

    def put(self, pos):
        '''
        if type(player) != bool:
            print("Type of player should be a bool.")
            exit(-1)

        if player != self.turn:
            if player:
                print("It should be on the turn of white but black plays.")
            else:
                print("It should be on the turn of black but white plays.")
            exit(-1)
        '''

        getPos(pos)     # check if position is valid

        if self.status[pos] != 0:
            print("There is already a chessman at the position.")
            exit(-1)

        if self.countsteps % 2 == 0:
            self.status[pos] = 1
            display(self.win, pos, True)
            displayinfo(self.win, 7, 34, '▶')
            displayinfo(self.win, 10, 34, ' ')
        else:
            self.status[pos] = -1
            display(self.win, pos, False)
            displayinfo(self.win, 7, 34, ' ')
            displayinfo(self.win, 10, 34, '▶')

        self.steps.append(pos)
        self.countsteps += 1
        if self.gameover(pos):
            # deal with gameover situation
            pass
            return False
        else:
            return True


class agent(object):
    def __init__(self, chessboard):
        self.board = chessboard

    def policy(self):
        return randpolicy(self)


def randpolicy(AGENT):
    while True:
        out = random.randint(0, 224)
        if out in AGENT.board.steps:
            continue
        else:
            return out
