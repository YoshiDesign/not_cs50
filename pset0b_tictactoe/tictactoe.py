"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None
score = {
    X : 1,
    O : -1
}

def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    Determine turn based on number of each tile on the board
    """
    tmp_x = 0
    tmp_o = 0
    for i in range(len(board)):
        for j in range(len(board[i])):
            tmp_x = tmp_x + 1 if board[i][j] == X else tmp_x
            tmp_o = tmp_o + 1 if board[i][j] == O else tmp_o

    # Conditionally X's turn
    if tmp_x <= tmp_o:
        return X
    else: # Conditionally Y's turn
        return O

    return None


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """

    if terminal(board):
        return None
    else:
        pass

    possible = set()

    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == EMPTY:
                possible.add(tuple([i,j]))

    return possible


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    cpy_board = copy.deepcopy(board)
    for i in range(len(cpy_board)):
        for j in range(len(cpy_board[i])):
            try:
                if action[0] == i and action[1] == j:
                    cpy_board[i][j] = player(board)

            except:
                raise KeyError("Incorrect Action")

    return cpy_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    u = utility(board)
    if terminal(board):
        return X if u == 1 else O if u == -1 else None

    return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    
    trace = contiguous(board)
    for p in [X,O]:
        if 3 in trace[p]['row']    or  \
            3 in trace[p]['col']   or  \
            3 in trace[p]['diag']:
            return True

    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == EMPTY:
                return False

    # Tie Game
    return True

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """

    trace = contiguous(board)

    for p in [X,O]:
        if 3 in trace[p]['row']    or  \
        3 in trace[p]['col']       or  \
        3 in trace[p]['diag']:

            return 1 if p == X else -1
            
    return 0

def best_move(board):

    if terminal(board):
        return  1 if winner(board) == X        \
                else -1 if winner(board) == O  \
                else 0

    moves = actions(board)
    p = player(board)

    if p == X: # X is maximizing
        best = -10000
        for move in moves:
            curscore = best_move(result(board, move))
            if curscore > best:
                best = curscore

        return max(curscore, best)

    elif p == O: # O is minimizing
        best = 10000
        for move in moves:
            curscore = best_move(result(board, move))
            if curscore < best:
                best = curscore

        return min(curscore, best)

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    wins = winner(board)
    if wins:
        return 1 if player(board) == X else -1 if player(board) == O else None

    moves = actions(board)
    best = None
    beatme = -10000 if player(board) == X else 10000

    while moves:
        move = moves.pop()

        # copy the board with a new move in place
        new_board = result(board, move)

        # If this move results in the AI's victory, return it
        if winner(new_board) == player(board):
            return move

        # Analyze it
        score = best_move(new_board)

        if player(board) == X:
            if score > beatme:
                beatme = score
                best = move

        elif player(board) == O:
            if score < beatme:
                beatme = score
                best = move

    return best


def contiguous(board):
    """
    Player heuristics of the board's current configuration
    """

    # A 3, anywhere, means a win
    trace = {
        "X" : {
            "row" : [0,0,0],    # Rows will only ever span 1 dimension
            "col" : [0,0,0],    # Track columns across all 3 rows
            "diag" : [0,0]      # Diags only have 2 variations
        },

        "O" : {
            "row" : [0,0,0],
            "col" : [0,0,0],
            "diag" : [0,0]
        }
    }

    for p in [X,O]:
        for i in range(len(board)):
            # Reset the row trace value each time

            for j in range(len(board[i])):

                if board[i][j] == EMPTY: continue
                elif board[i][j] == p:

                    # We can always increment rows and columns
                    trace[p]['row'][i] += 1
                    trace[p]['col'][j] += 1
                    # if trace[p]['row'][i] == 3 or trace[p]['col'][j] == 3:
                    #     # print(trace)
                    #     return trace

                    # Diagonal values can only be at specific locations
                    if i == 1 and j == 1:
                        # Center block - add 1 to each diag index
                        trace[p]['diag'] = [  x + 1 for x         \
                                            in trace[p]['diag']   \
                                            if board[i][j] == p \
                                        ]
                    # Score the corners
                    elif i in [0,2] and j in [0,2]:
                        if i == 0 and j == 0 or i == 2 and j == 2:
                            trace[p]['diag'][0] +=        \
                                1 if board[i][j] == p   \
                                else trace[p]['diag'][0]
                        if i == 0 and j == 2 or i == 2 and j == 0:
                            trace[p]['diag'][1] +=        \
                                1 if board[i][j] == p   \
                                else trace[p]['diag'][1]

    return trace