import curses
import chessboard as chb
import time

# ● ◯

stdscr = curses.initscr()
curses.cbreak()
stdscr.keypad(True)
curses.noecho()

win = curses.newwin(15, 30, 1, 0)


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
    board = chb.board(win)
    board.put(110, True)
    win.getstr()
    terminateCrs()

if __name__ == "__main__":
    main()
