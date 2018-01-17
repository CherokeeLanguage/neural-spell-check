# encoding: utf-8
from booking_mtlib.parallelize import multiprocess
import regex
import sys
from collections import defaultdict

class ReTokenizer(object):
    ANY_WORD = ur'[\p{L}\p{M}■]+'
    NAMED_ENTITY = ur'＃[\p{L}\p{M}\p{N}：]+'
    NUMBER = ur'[\p{N}]+'
    SPACE = ur'[\p{Z}]+'
    REST = ur'[^\p{Z}\p{L}\p{M}\p{N}：■＃]'
    TOKENIZER_RE = regex.compile(ur'(?V1p)' + u'|'.join((ANY_WORD, NAMED_ENTITY, SPACE, NUMBER, REST)))
    SPACE_RE = regex.compile(ur'(?V1p)^[\p{Z}]+$')
    JOINER = u'￭'
    JOINER_RE = regex.compile(ur'(?V1p) ￭ ')
    
    @classmethod
    def tokenize(cls, sentence):
        tokens = []
        token_is_space = True
        for w_it in cls.TOKENIZER_RE.finditer(sentence):
            w = sentence[w_it.start():w_it.end()]
            cur_token_is_space = True if cls.SPACE_RE.match(w) else False
            if not token_is_space and not cur_token_is_space:
                tokens.append(cls.JOINER)
            token_is_space = cur_token_is_space
            if not cur_token_is_space:
                tokens.append(w)
        return tokens

    @classmethod
    def detokenize(cls, tokens):
        words = u' '.join(tokens)
        return cls.JOINER_RE.sub(u'', words)

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word): 
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))

def print_all_edits(word):
    all_edits = set()
    for e in tuple(edits2(word)) + tuple(edits1(word)):
        if e in all_words:
            word_graph[w].add(e)

def main():
    words = set()
    for l in sys.stdin:
        words.add(l.strip('\n').decode('utf-8'))

    def print_all_edits(word):
        all_edits = set()
        for e in tuple(edits2(word)) + tuple(edits1(word)):
            if e in words:
                all_edits.add(e)
        return u"\t".join((word, ",".join(all_edits))).encode('utf-8')
                
    for l in multiprocess(print_all_edits, words, 24):
        print l

if __name__ == "__main__":
    main()
