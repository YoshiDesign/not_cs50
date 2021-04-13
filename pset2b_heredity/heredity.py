import csv
import itertools
import sys
import math

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    joints = []

    # print(f"CONDITIONS: \none_gene: {one_gene}\ntwo_genes: {two_genes}\nhave_trait:{have_trait}")

    for name in people:

        has_mother = None
        has_father = None

        # Determine if this person has parents to account for
        # if name == "Harry": print("HARRY")
        if people[name]['mother']:

            # find out how many genes each parent has
            if people[name]['mother'] in one_gene:
                has_mother = 1
            elif people[name]['mother'] in two_genes:
                has_mother = 2
            else:
                has_mother = 0

            # print(f"Has Mother with: {has_mother}")

        if people[name]['father']:
            if people[name]['father'] in one_gene:
                has_father = 1
            elif people[name]['father'] in two_genes:
                has_father = 2
            else:
                has_father = 0

            # print(f"Has Father with: {has_father}")

        g = 1 if name in one_gene \
        else 2 if name in two_genes \
        else 0

        t = True if name in have_trait else False
        # print(f"g = {g}")
        # print(f"t = {t}")
        # print(f"has_father: {has_father}")
        # print(f"has_mother: {has_father}")

        # Get child probabilities based on conditions
        if has_mother != None and has_father != None:
            # print(f"ChildName: {name}")
            # print(f"{name} has trait : {t}")
            # print(f"{name} has genes : {g}")
            # print(f"{name} has mother gene : {has_mother}")
            # print(f"{name} has father gene : {has_father}")
            p = from_parents(has_mother, has_father, g, t)

        else:
            # print(f"Name: {name}")
            p = PROBS['trait'][g][t] * PROBS['gene'][g]

        # print(f"PROB: {p}")
        joints.append(truncate(p,6))
    
    # Calculate the joint probability
    prod = 1
    for j in joints:
        # Arbitrarily multiplying by 100
        prod = truncate(100 * (j * prod), 4)
    
    # print(joints)
    # print(prod)
    return prod

def truncate(number, decimals=0):

    if decimals == 0:
        return math.trunc(number)

    factor = 10.0 ** decimals
    return math.trunc(number * factor) / factor

def from_parents(mg, fg, g, t):
    """
    mg - Number of genes mother has
    fg - Number of genes father has
    g - number of genes child (this person) has
    t - expresses trait ? 
    """

    from_m = 1 - PROBS['mutation'] if mg == 2 \
        else .5  if mg == 1 \
        else PROBS['mutation']

    from_f = 1 - PROBS['mutation'] if fg == 2 \
        else .5  if fg == 1 \
        else PROBS['mutation']

    not_from_f = 1 - from_f
    not_from_m = 1 - from_m

    # print(f"Prob from_m: {from_m}")
    # print(f"Prob from_f: {from_f}")

    # Formulae for dependent probabilities. Truncated to 6 decimals
    data = {
        # Two from both
        2: truncate(100 * ( (from_f * from_m) ), 4),
        # One from either
        1: truncate(100 * ( (from_f * not_from_m) + (from_m * not_from_f) ), 4),
        # None from both
        0: truncate(100 * ( (not_from_f * not_from_m) ), 4)
    }

    # print(f"P = { truncate((data[g]) * PROBS['trait'][g][t], 4) }")

    # print(f"Formula[{g}] -- {truncate((data[g] * PROBS['trait'][g][t]), 6)}")
    # print(f"from_m : {from_m}")
    # print(f"from_f : {from_f}")
    # print(f"not_from_m : {not_from_m}")
    # print(f"not_from_f : {not_from_f}")

    # The probability that this child has 'g' copies. Expression based on 't'
    return truncate((data[g] * PROBS['trait'][g][t]), 4)
        


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """

    # Note to self --- If I fail this one.
    # I wasn't sure whether or not to update the names given,
    # or both the names given as well as what can be implied.
    # The spec made it sound like we only update the names within
    # the supplied args but I'm also updating based on implication
    # because really, the spec doesn't need to exhaust instructions
    # per example...

    for name in probabilities:
        # print(name)

        # This person has no gene and does not express the trait
        if name not in one_gene and name not in two_genes and name not in have_trait:
            probabilities[name]['gene'][0] += p
            probabilities[name]['trait'][False] += p
            continue

        # If this person has the trait
        if name in have_trait:
            probabilities[name]['trait'][True] += p
            if name not in one_gene and name not in two_genes:
                probabilities[name]['gene'][0] += p
                continue

        # If this person is in one_gene
        if name in one_gene:
            probabilities[name]['gene'][1] += p
            if name not in have_trait:
                probabilities[name]['trait'][False] += p
                continue

        # If this person is in two_genes
        if name in two_genes:
            probabilities[name]['gene'][2] += p
            if name not in have_trait:
                probabilities[name]['trait'][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for name in probabilities:
        for item in probabilities[name]:
            t = sum(probabilities[name][item].values())
            for data in probabilities[name][item]:
                probabilities[name][item][data] = truncate((probabilities[name][item][data] / t), 4)
                

if __name__ == "__main__":
    main()
