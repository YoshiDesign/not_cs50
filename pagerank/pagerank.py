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

    no_incoming = len(corpus[page])

    # Add our latest values to the transition model
    for p in tModel:
        # Probability added to each page in case we choose any at random
        tModel[p] += (1-damping_factor) / len(corpus.keys())
        if p in corpus[page] and p != page:
            # Probability with which we select a particular page
            tModel[p] += damping_factor / no_incoming

    return tModel


def sampling_tModel(corpus):

    # Initialize our transition model
    tModel = {}
    for k in corpus.keys():
        tModel[k] = 0

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
    sample = None
    previous_sample = None
    page_list = list(corpus.keys())
    page = page_list[ random.randint(0, len(corpus.keys()) - 1) ]
    final_sample = {}
    for k in corpus:
        final_sample[k] = 0.0

    
    for i in range(n):

        # previous_sample = None if not sample else sample.copy()
        sample = transition_model(corpus, page, damping_factor)

        for k in sample.keys():
            final_sample[k] += sample[k]

        if corpus[page]:
            page = random.sample(corpus[page], 1)[0]
        else:
            page = page_list[ random.randint(0, len(corpus.keys()) - 1) ]

    ss = sum(final_sample.values())

    for s in final_sample:
        prob = final_sample[s] / (ss)
        final_sample[s] = prob
    
    return final_sample

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    base = (1 - damping_factor) / len(corpus.keys()) + damping_factor

    # Initialize our probabilities with equal odds
    ranks = {}
    for p in corpus:
        ranks[p] = float(1 / len(corpus.keys()))

    it = 0
    k = list(corpus.keys())
    while True:

        cn = it % len(k)
        # current page - calculating the probability of visiting
        p = k[cn]
        pre_ranks = ranks.copy()

        new_prob = 0
        # for p in list(corpus.keys()):

        # moved new_prob from ehre to there    

        # The number of links on this page
        # excluding links to itself
        n = len(corpus[p])
        
        # Every page that links to P
        i_pages = set()
        for page in corpus.keys():
            if p in corpus[page]: # and page != p
                i_pages.add(page)

        for i in i_pages:
            duplicate = 0
            if i in corpus[i]:
                duplicate += 1
            new_prob += (ranks[i] / (len(corpus[i]) - duplicate) )

        new_prob = new_prob * damping_factor
        new_prob += base
        ranks[p] = new_prob
        
    
        if lt_thou(pre_ranks, ranks):
            break
        it += 1
    ranks = sum_to_one(ranks)
    return ranks


def lt_thou(pre_ranks, post_ranks):
    """
    Determine if the iteration results meet the
    specification's success conditions
    """
    n = 0
    for p in pre_ranks.keys():
        diff = abs(post_ranks[p] - pre_ranks[p])
        if diff >= float(0.001):
            continue

        else:
            n += 1

    if n == len(pre_ranks.keys()):
        return True
    
    return False

def sum_to_one(ranks):

    new_ranks = ranks.copy()

    for rank in ranks:
        proportion = ranks[rank] / sum(ranks.values())
        new_ranks[rank] = proportion
    
    return new_ranks

if __name__ == "__main__":
    main()
