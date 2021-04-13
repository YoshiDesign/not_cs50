import nltk
import sys
import os
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """

    corp = dict()

    for name in os.listdir('corpus'):

        with open("corpus" + os.sep + name, 'r') as doc :
            corp[name] = doc.read()

    return corp


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """

    # Unable to acquire 'stopwords' without these snippets due to my python config
    # import ssl
    # ssl._create_default_https_context = ssl._create_unverified_context
    # nltk.download('stopwords')

    stops = nltk.corpus.stopwords.words("english")

    all_words = list()
    cleaned_words = list()

    all_words = nltk.word_tokenize(document)

    for word in all_words:
        word = word.strip()
        word = word.lower()

        if word in stops \
            or not word \
            or word in string.punctuation \
            or word.strip("=") != word:
            continue
        else:
            cleaned_words.append(word)

    return cleaned_words


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    uniques = []
    _idf = {}

    for doc in documents.values():
        for word in doc:
            if word not in uniques:
                # Add word to words already computed
                uniques.append(word)

    for word in uniques:
        # Begin with a count of 1 (Laplace smoothing)
        docs_containing_word = 0
        for doc in documents.values():

            if word in doc:
                # print(f"Found {word} {doc.count(word)} times in all docs.")
                docs_containing_word += 1

        _idf[word] = math.log(len(documents.keys()) / docs_containing_word)

    return _idf


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """

    _dict = {}
    _idfs = idfs.copy()
        
    # Restructure our data to make it easier to work with
    for word in query:
        for f in files:
            try:
                check = _dict[f]
            except KeyError:
                _dict[f] = {}

            if word in files[f]:
                # +1 for laplace smoothing
                _dict[f][word] = (_idfs[word] * ( files[f].count(word) + 1 ) )

    # Sum of all file's tf-idf's
    sum_files = {}
    for f in _dict:

        try:
            check = sum_files[f]
        except KeyError:
            sum_files[f] = 0

        sum_files[f] = sum(_dict[f].values())
    
    top_files = []

    stop = 0

    while len(top_files) < n:

        top = ""
        g = 0.0

        # If all of theh file idfs are 0 - the selection is arbitrary
        if sum(sum_files.values()) == 0:
            _next = list(sum_files.keys())[0]
            top_files.append(_next)
            del sum_files[_next]
            continue
        
        for k, v in sum_files.items():
            
            if float(v) > float(g):
                g = v
                top = k
                
        top_files.append(top)
        del sum_files[top]

    # print(f"Top Files:\n\t{top_files}")
    return top_files


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    scored_sentences = {}
    for word in query:
        # print(f"Searching for {word}")
        for k, v in sentences.items():

            # Ignore headings
            if k.strip("=") != k:
                continue

            if word.lower() in v:
                
                try:
                    check = scored_sentences[k]
                except:
                    scored_sentences[k] = 0

                scored_sentences[k] += idfs[word]

    # print(scored_sentences)
    # exit()

    # print(f"Scored Sentences:\n\t{scored_sentences}")
    final_result = []
    while len(final_result) < n:
        top = ""
        g = 0.0
        s = False

        for k, v in scored_sentences.items():

            if float(v) >= float(g):

                # Query term density calculation
                if float(v) == float(g):

                    old_s_set = set(top.split(" "))
                    new_s_set = set(k.split(" "))
                    q_set = set(query)

                    # similarities between words in question and our query words
                    inter_new = float(len(new_s_set & q_set) / len(k))
                    inter_old = float(len(old_s_set & q_set) / len(top))

                    if inter_new < inter_old:
                        continue

                g = v
                top = k

        if top:
            final_result.append(top)
            del scored_sentences[top]
        else:
            final_result.append("Not enough context for additional results.")
            return final_result
        
    return final_result

if __name__ == "__main__":
    main()
