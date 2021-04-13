import os
import random
import re
import sys
import math

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor, tModel=None):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # Initialize our transition model if one is not provided
    if not tModel:
        tModel = sampling_tModel(corpus)

    # List all available pages in the corpus
    page_list = list(corpus.keys())

    # Pages from the current page
    available_pages = corpus[page]

    if len(corpus[page]) == 0:
        # The page we are on has 0 links
        # Each page now has equal probability. Current page inclusive
        equal_probs = float( (1 / len(corpus.keys())) )
        for k in list(tModel.keys()):
            tModel[k] += equal_probs
        return tModel

    elif random.random() <= 1 - damping_factor:
        # Visit a random page instead
        # print("Damp...")
        page = page_list[random.randint(0, len(page_list) - 1)]
        # print(f"RP:\t {page}")
    else:
        # Visiting a linked-to page
        page = random.sample(available_pages, 1)[0]
        # print(f"VP:\t {page}")


    tModel[page] += 1
    return tModel



def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Choose a random page to visit first
    page = list( corpus.keys() )[random.randint(0, len( corpus.keys() ) -1 )]
    sample = None
    previous_sample = None
    new_page = None
    
    for i in range(n):
        # print("------------------------------")
        if sample == None:

            # Initialize our sampling
            sample = transition_model(corpus, page, damping_factor, None)

            # Find the page we first visited
            for k in sample:
                if sample[k] > 0:
                    new_page = k

        else:
            if new_page == None:
                print("Improbability Alert")
                raise Exception

            previous_sample = sample.copy()
            sample = transition_model(corpus, new_page, damping_factor, sample)

            # Assert that these 2 dicts always have the same keys
            if list(previous_sample.keys()) != list(sample.keys()):
                print("Improbability Alert")
                raise AssertionError

            # Update the page we're looking at
            for k in list(previous_sample.keys()):
 
                if previous_sample[k] < sample[k]:
                    new_page = k

    for s in sample:
        prob = float(sample[s] / n)
        sample[s] = prob
    
    return sample


def iterate_pagerank(corpus, damping_factor, ranks=None, page=None, x=0):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # print("\n---------------------------------------------------------------------------------------------\n")
    x+=1

    # Start with uniform distribution
    if ranks == None:
        ranks = {}
        for p in corpus:
            ranks[p] = float(1 / len(corpus.keys()))

    # Start w/ a random page
    if page == None:
        page = list(corpus.keys())[random.randint(0, len(corpus.keys())-1)]
        # print(f"Start with page {page}")

    next_page = None

    # Retrieve a new ranking based on the pages that link to page
    pre_ranks = ranks.copy()

    # print(f"Pre-ranks: {pre_ranks}")

    ranks = iterative_ranking(corpus, page, ranks, damping_factor)

    pos = sum(ranks.values())
    # post_ranks = alpha_checks(ranks.copy(), pos)

    post_ranks = ranks.copy()

    # When the deviation for each PR from its previous PR is <= .001
    # prompt the exit condition
    n = 0
    print("-----------------------------")
    for p in corpus.keys():
        diff = truncate(abs(post_ranks[p] - pre_ranks[p]), 6)
        print(diff)
        # print(abs(post_ranks[p] - pre_ranks[p]) > float(0.001))
        if diff == 0.0 or diff > float(0.0001):
            continue
        else:
            # print("increment N ")
            n += 1

    if n == len(ranks.keys()):
        return ranks

    else:
        
        if random.random() >= (1 - damping_factor):
            next_page = list(corpus.keys())[random.randint(0, len(corpus.keys())-1)]
        else:
            try:
                # print("CHOOSING NEW PAGE")
                next_page = random.sample(corpus[page], 1)[0]

            except ValueError:
                print("Errr")
                exit()

        return iterate_pagerank(corpus, damping_factor, ranks, next_page, x)

def iterative_ranking(corpus, page, ranks, damping_factor):

    # page - The page we chose

    contains_page = []
    new_heuristic = 0

    # To be added to the summation of probabilities of each page(i)
    base_factor = (1 - damping_factor) / len(corpus.keys())

    # Return to uniform probability -- Probably wrong
    ranks[page] = base_factor
    # ranks[page] = 0.0
    # Normalize the base factor relative to the previous entries
    # ranks = alpha_checks(ranks, sum(ranks.values()))

    # Find every page that contains a link to the page we've chosen
    for p in corpus.keys():
        if page in corpus[p] and p != page:
            contains_page.append(p)

    for i in contains_page:
        new_heuristic += float( ranks[i] / len(corpus[i]) )

    ranks[page] = damping_factor * new_heuristic

    ranks = alpha_checks(ranks, sum(ranks.values()))
    return ranks
    # return alpha(ranks)

def alpha_checks(ranks,s):
    """
    Normalize the ranks to a percentage
    """
    cranks = ranks.copy()
    rvals = cranks.values()
    # print(f"Length of rvals: {len(rvals)}")
    for k in ranks:
        # print(f"Calculating {ranks[k]}/{s}")
        cranks[k] = float(ranks[k] / s)

    return cranks

def sampling_tModel(corpus):

    # Initialize our transition model
    tModel = {}
    for k in corpus.keys():
        tModel[k] = float(0)

    return tModel


def truncate(number, decimals=0):

    if decimals == 0:
        return math.trunc(number)

    factor = 10.0 ** decimals
    return math.trunc(number * factor) / factor


if __name__ == "__main__":
    main()
