#! /usr/bin/env/python3.6
import math
import tictactoe as ttt
X = "X"
O = "O"
EMPTY = None
def main():


    brd = [
        [O,O,EMPTY],
        [EMPTY,EMPTY,EMPTY],
        [EMPTY,EMPTY,EMPTY]
    ]

    # print(f"Turn: {ttt.player(brd)}")

    # print("Testing Utility")
    # # print(ttt.utility(brd))

    print(ttt.player(brd))



if __name__ == "__main__":
    main()