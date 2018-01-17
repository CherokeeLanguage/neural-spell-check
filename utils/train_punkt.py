import sys
import nltk
import codecs
import cPickle as pickle
from nltk import word_tokenize


def train_punkt_tokenizer(text, tokenizer_file_name, verbose=False):
    texts = u'\n'.join(text)
    punkt_tok = nltk.tokenize.punkt.PunktTrainer()
    punkt_tok.train(texts, verbose=verbose)
    model = nltk.tokenize.PunktSentenceTokenizer(punkt_tok.get_params())
    with open(tokenizer_file_name, mode='wb') as fout:
        pickle.dump(model, fout, protocol=pickle.HIGHEST_PROTOCOL)


def main():
    stdin = codecs.getreader('utf8')(sys.stdin)
    train_punkt_tokenizer(stdin.readlines(), sys.argv[1], True)


if __name__ == '__main__':
    main()

