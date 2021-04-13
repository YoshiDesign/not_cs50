import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S ->  NP VP | VP NP | S Conj S | S P S | S NP | S P NP
NP -> N | Det N Adv | Det N | Det AA NP | P N | N Adv | N V | P N
AA -> Adj | Adv | Adj AA
VP -> V | V Adv | V P NP | V NP | P NP V | V P NP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """

    # Unable to acquire 'punkt' without these snippets due to my python config
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
    nltk.download('punkt')

    p = 0
    tokens = nltk.word_tokenize(sentence)
    cleaned = []

    for word in tokens:
        if word.isnumeric():
            continue
        elif len(word) == 1 and not word.isalpha():
            continue

        for letter in word:
            p = 0
            if letter.isalpha():
                p = 1
                break

        if p:
            cleaned.append(word.lower())

    return cleaned

def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    # print(len(tree))
    _npc = []
    npc = []

    # npc.append(dive_tree(tree))
    for i, sub in enumerate(tree.subtrees()):
        # Collect applicable subtrees
        if sub.label() == "NP":
            _npc.append(sub)

    for _tree in _npc:
        parsed = False
        # Filter any NP's that have nested NP's
        for sub in _tree.subtrees(lambda t: t.label() == "NP" and len(t) > 1 and t.height() > 1):
            parsed = True
            npc.append(sub)

        if not parsed:
            for sub in _tree.subtrees(lambda t: t.label() == "NP" and len(t) == 1):
                npc.append(sub)

    # Remove nested NP's which were singular nouns as part of another NP
    for i, p in enumerate(npc):
        for j, q in enumerate(npc):
            if i == 0:
                break
            if len(q) == 1 and j == (i+1):
                if q in p:
                    npc.remove(q)

    return npc

def if_nested(branch):
    for sub in branch.subtrees():
        print(sub)

if __name__ == "__main__":
    main()
