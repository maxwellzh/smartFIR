
def getPos(pos):
    if pos < 0 or pos > 224:
        print("getPos() error. Invalid input.")
        exit(-1)
    return (int(pos//15), int(pos % 15))


def indexPos(x, y):
    if x < 0 or x > 14 or y < 0 or y > 14:
        print("indexPos() error. Invalid input.")
        exit(-1)
    return int(x * 15 + y)

def display(win, pos, player):
    showstr = '●' if player else '◯'
    x, y = getPos(pos)
    win.addstr(x, 2 * y, showstr)
    win.refresh()


class board(object):
    def __init__(self, win):
        self.status = [0 for _ in range(225)]
        self.turn = True    # True for black, False for white
        self.win = win

    def checkWin(self, pos):
        x = int(pos//15)
        y = int(pos % 15)
        if x not in range(15) or y not in range(15):
            print("Position of chessman invalid.")
            exit(-1)

        # Four directions of probale win
        countwin = 0
        lastone = 0
        for i in range(x-4, x+5):
            if i not in range(15):
                continue
            if self.status[indexPos(i, y)] != lastone:
                countwin = self.status[indexPos(i, y)]
            else:
                countwin += self.status[indexPos(i, y)]
            lastone = i
        if countwin == 5:
            return True
        elif countwin == -5:
            return False

        countwin = 0
        lastone = 0
        for i in range(y-4, y+5):
            if i not in range(15):
                continue
            if self.status[indexPos(x, i)] != lastone:
                countwin = self.status[indexPos(x, i)]
            else:
                countwin += self.status[indexPos(x, i)]
            lastone = i
        if countwin == 5:
            return True
        elif countwin == -5:
            return False

        countwin = 0
        lastone = 0
        for i in range(-4, 5):
            if i not in range(15):
                continue
            if self.status[indexPos(x + i, y + i)] != lastone:
                countwin = self.status[indexPos(x + i, y + i)]
            else:
                countwin += self.status[indexPos(x + i, y + i)]
            lastone = i
        if countwin == 5:
            return True
        elif countwin == -5:
            return False

        countwin = 0
        lastone = 0
        for i in range(-4, 5):
            if i not in range(15):
                continue
            if self.status[indexPos(x + i, y - i)] != lastone:
                countwin = self.status[indexPos(x + i, y - i)]
            else:
                countwin += self.status[indexPos(x + i, y - i)]
            lastone = i
        if countwin == 5:
            return True
        elif countwin == -5:
            return False

        return None

    def gameover(self, pos):
        if 0 not in self.status:
            print("Draw.")
            return True

        winplayer = self.checkWin(pos)

        if winplayer == None:
            return False
        if winplayer:
            print("Black player wins!")
        else:
            print("White player wins!")
        return True

    def put(self, pos, player):
        if type(player) != bool:
            print("Type of player should be a bool.")
            exit(-1)

        if player != self.turn:
            if player:
                print("It should be on the turn of white but black plays.")
            else:
                print("It should be on the turn of black but white plays.")
            exit(-1)

        getPos(pos)     # check if position is valid

        if self.status[pos] != 0:
            print("There is already a chessman at the position.")
            exit(-1)

        if player:
            self.status[pos] = 1
            display(self.win, pos, True)
        else:
            self.status[pos] = -1
            display(self.win, pos, False)

        if self.gameover(pos):
            # deal with gameover situation
            pass
            return False
        else:
            return True
