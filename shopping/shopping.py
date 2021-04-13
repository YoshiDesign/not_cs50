import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """

    evidence, labels = [], []
    floats  = [1,3,5,6,7,8,9]
    ints    = [0,2,4,11,12,13,14]
    mos     = [ \
        "Jan", "Feb", "Mar",  \
        "Apr", "May", "June", \
        "Jul", "Aug", "Sep",  \
        "Oct", "Nov", "Dec"   \
    ]

    with open(filename) as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            e,l = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 0
            if i > 0:
                for j, item in enumerate(row):
                 
                    if j in floats:
                        e[j] = float(item)

                    # Month
                    elif item in mos:
                        e[j] = mos.index(item)
                    
                    # Weekend
                    elif j == 16:
                        if item == "TRUE":
                            e[j] = 1
                        elif item == "FALSE":
                            e[j] = 0

                    # Visitor Type
                    elif j == 15:
                        if item == "Returning_Visitor":
                            e[j] = 1
                        else:
                            e[j] = 0
                        
                    elif j in ints:
                        e[j] = int(item)

                l = 1 if row[-1] == "TRUE" else 0
                evidence.append(e.copy())
                labels.append(l)

    return tuple((evidence, labels))

def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """

    neighbors = KNeighborsClassifier(n_neighbors=1)
    return neighbors.fit(evidence, labels)


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """

    t = 0
    f = 0
    actual_true = 0
    actual_false = 0
    miss = 0

    for n in labels:
        if n == 0:
            actual_false += 1
        if n == 1:
            actual_true += 1

    for x, y in zip(labels, predictions):
        if x == y:
            if x == 0: # Accurate Positive
                f += 1
            if x == 1: # Accurate Negative 
                t += 1
        elif x != y:   # Inacurate Prediction
            miss += 1

    # print(f"Accurately guessed {t} / {actual_true} true\nAccurately guessed {f} / {actual_false} false")
    sensitivity = t / (actual_true)
    specificity = f / (actual_false)

    return tuple((sensitivity, specificity))

if __name__ == "__main__":
    main()
