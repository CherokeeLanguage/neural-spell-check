# coding: utf-8
import sys
import nltk
import cPickle as pickle


def main():
    sent_tokenize = pickle.load(open(sys.argv[1]))
    for l in sys.stdin:
        snts = sent_tokenize.tokenize(l.decode('utf-8').strip(u'\n'))
        for s in snts:
            if s and len(s) > 1:
                print s.encode('utf-8')

if __name__ == '__main__':
    main()
