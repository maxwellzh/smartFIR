import curses
import modules as chb
import time

# ● ◯


def main():
    board = chb.board()
    playerA = chb.agent(board)
    playerB = chb.agent(board)
    #playerB = chb.randagent(board)

    # Loop
    i = 0
    countwin = 0
    while True:
        # Judge whose turn
        player = playerA if board.turn else playerB
        # policy determine
        step = player.policy()
        # put chessman
        if board.put(step):
            continue
        else:
            i += 1
            if(board.countsteps % 2 == 0):
                countwin += 1
            print("\rStep|Winrate %d|%.2f%%" % (i, countwin/i*100), end='')
            playerA.update()
            playerB.update()
            board.reset()
        if i % 50 == 0:
            playerA.save('./NETA.pt')
            #playerB.save('./NETB.pt')
        if i == 1000:
            break


if __name__ == "__main__":
    main()
