import curses
import modules as chb
import time

# ● ◯
alterupdate = True

def main():
    board = chb.Board()
    playerA = chb.Agent(board)
    playerB = chb.Agent(board, mode='B')
    # playerB = chb.randagent(board)

    # Loop
    i = 0
    countwin = 0
    runstep = 0
    while True:
        # Judge whose turn
        player = playerA if board.turn else playerB
        # policy determine
        step = player.policy()
        runstep += 1

        # put chessman
        if board.put(step):
            if not board.turn:
                # print("update A")
                playerA.update()
            else:
                # print("update B")
                playerB.update()
            continue
        else:
            i += 1
            if not board.turn:
                countwin += 1
            print("\rStep|Winrate|Run %d|%.2f%%|%d" % (i, float(countwin)/i*100, runstep), end='')
            board.reset()
            playerA.reset()
            playerB.reset()
            runstep = 0

        if i % 10 == 0:
            playerA.save('./NETA.pt')
            playerB.save('./NETB.pt')
        if i == 1000:
            break
    print("")


if __name__ == "__main__":
    main()
