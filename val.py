import curses
import modules as chb
import time
import random

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
    # playerB = chb.Agent(board, loadmodel=True, path='./NETB.pt', eval=True)
    playerB = chb.randagent(board)

    # Loop
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
            break

if __name__ == "__main__":
    random.seed(time.time())
    main()
    win.getstr()
    terminateCrs()
