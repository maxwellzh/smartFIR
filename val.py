import curses
import modules as chb
import time
import random

aifirst = True

# ● ◯

stdscr = curses.initscr()
curses.cbreak()
stdscr.keypad(True)
curses.noecho()

win = curses.newwin(17, 44, 1, 0)


def terminateCrs():
    global stdscr
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()
    stdscr = None
    return


def display(pos, player):
    global win
    showstr = '●' if player else '◯'
    x, y = chb.getPos(pos)
    win.addstr(x, 2 * y, showstr)
    win.refresh()


def main():
    board = chb.Board(win)
    playerA = chb.Agent(board, loadmodel=True, path='./NETA.pt', eval=True)
    playerB = chb.Agent(board, loadmodel=True, path='./NETB.pt', eval=True)
    # playerB = chb.randagent(board)

    # Loop
    countwin = 0
    i = 0
    while True:
        # Judge whose turn
        player = playerA if board.turn else playerB
        # policy determine
        step = player.policy()
        # put chessman
        if board.put(step):
            time.sleep(0.1)
            continue
        else:
            i += 1
            if not board.turn:
                countwin += 1
            board.reset()
            win.addstr(1, 4, ('Round:%4d AI:%4.2f%%' % (i, countwin/i*100)))
            win.refresh()
        if i == 10:
            break

    '''
    while True:
        # Judge whose turn
        player = playerA if board.turn else playerB
        win.addstr(1, 0, str(type(player)))
        win.refresh()
        # policy determine
        step = player.policy()
        # put chessman
        if board.put(step):
            time.sleep(0.3)
            continue
        else:
            break
    '''


if __name__ == "__main__":
    random.seed(time.time())
    main()
    win.getstr()
    terminateCrs()
