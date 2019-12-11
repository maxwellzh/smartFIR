import curses
import modules as chb
import time

# ● ◯
alterupdate = True

def main():
    board = chb.board()
    playerA = chb.agent(board)
    playerB = chb.agent(board)
    #playerB = chb.simpleagent(board)

    #playerA = chb.agent(board, loadmodel=True, path='./NETA.pt')
    #playerB = chb.agent(board, loadmodel=True, path='./NETB.pt')

    # Loop
    i = 0
    countwin = 0
    upPlayer = playerA
    alterRound = 5
    countRound = 0
    winRound = 0
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
            countRound += 1
            if(board.countsteps % 2 != 0):
                countwin += 1
                winRound += 1
            print("\rStep|WRA|WRR=%d|%.2f%%|%.2f%%" % (i, countwin/i*100, winRound/countRound * 100), end='')
            upPlayer.update()
            board.reset()
        if i % alterRound == 0:
            countRound = 0
            winRound = 0
            upPlayer.model.eval()
            upPlayer = playerA if upPlayer == playerB else playerB
            upPlayer.model.train()
        if i == 1000:
            break
    print("")
    playerA.model.train()
    playerB.model.train()
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
            print("\rStep|WRA=%d|%.2f%%" % (i, countwin/i*100), end='')
            playerA.update()
            playerB.update()
            board.reset()
        if i % 100 == 0:
            playerA.save('./NETA.pt')
            playerB.save('./NETB.pt')
        if i == 200000:
            break
    print("")


if __name__ == "__main__":
    main()
