import curses
import modules as chb
import time

# ● ◯


def main():
    board = chb.board()
    playerA = chb.agent(board)
    playerB = chb.agent(board)
    #playerB = chb.simpleagent(board)

    #playerA = chb.agent(board,loadmodel=True, path='./NETA.pt')
    #playerB = chb.agent(board,loadmodel=True, path='./NETB.pt')

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
            if(board.countsteps % 2 != 0):
                countwin += 1
            print("\rStep|Winrate %d|%.2f%%" % (i, countwin/i*100), end='')
            playerA.update()
            playerB.update()
            board.reset()
        if i % 100 == 0:
            playerA.save('./NETA.pt')
            playerB.save('./NETB.pt')
        if i == 2000:
            break
    print("")


if __name__ == "__main__":
    main()
