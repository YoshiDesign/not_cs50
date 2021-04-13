from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    # A is either a knight or a knave
    Or(AKnight, AKnave),
    # A cannot be both a knight and a knave. This would imply that A is a knave
    Implication(Not(And(AKnave, AKnight)), AKnave), 
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    # A and B are either a Knight or a Knave
    Or(AKnight, AKnave), Or(BKnight, BKnave),

    # A cannot be a Knight claiming to be a Knave. 
    # This could be written in a myriad of ways. 

    # If A and B were indeed both Knaves, we would
    # know 2 things:
    # - Knights would not make this claim.
    # - B is not what A makes claim to it being.
    Implication(And(AKnave, BKnave), Not(BKnave)),
    Implication(Not(And(AKnave,BKnave)), AKnave)

)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    # A and B are either a Knight or a Knave
    Or(AKnight, AKnave), Or(BKnight, BKnave),

    # If A makes the claim that they are both the same
    # then it must be true that we could imply, that
    # B, were it a Knave, will contradict A's claim
    Implication(
        AKnight, 
        Implication(BKnave, Not(AKnight))
    ),

    # From this understanding, we infer that A is a
    # knave if and only if B is a knight
    Biconditional(AKnave, BKnight)

)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(

    # Base Logic
    Or(AKnight, AKnave), Or(BKnight, BKnave), Or(CKnight, CKnave),
    # Each cannot be both - I won't be implementing logic that would suggest this though
    Not(And(AKnave, AKnight)),
    Not(And(BKnave, BKnight)),
    Not(And(CKnave, CKnight)),

    # A makes no claim of any identity other than its own
    # If any should claim:
    #   "A said --(anything that isn't A referring to itself)--", they must be lying.

    # Therefore, if B is a knave, A might be a knight
    Implication(BKnave, AKnight),

    # And if B is a knight, C might be a knave
    Implication(BKnight, CKnave),

    # But A makes no claim about B. 
    # Since this is true, B would be lying if it claimed
    # that A made any remarks towards its identity.
    And(Or(BKnave, BKnight), Implication(AKnight, BKnave)),

    # C is a knight if and only if B is a Knave. 
    # B reported that C is a knave,
    # this however does not support the falsehood of the overall assertion that C is a knight
    And(CKnight, Implication(CKnave, BKnight), Biconditional(CKnight, BKnave))

)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
