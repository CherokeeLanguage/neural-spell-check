# coding: utf-8
import sys
import regex
import random
import traceback
from collections import defaultdict

ANY_CAPITAL = regex.compile('\p{Lu}')
CHARS = list(u"abcdefghijklmnopqrstuvwxyz  ")
DICT = None

class ReTokenizer(object):
    ANY_WORD = ur'[\p{L}\p{M}]+'
    ANY_WORD_RE = regex.compile(ur'(?V1p)' + ANY_WORD + '$')
    NUMBER = ur'[\p{N}]+'
    NUMBER_RE = regex.compile(ur'(?V1p)' + NUMBER + '$')
    SPACE = ur'[\p{Z}]+'
    REST = ur'[^\p{Z}\p{L}\p{M}\p{N}]'
    TOKENIZER_RE = regex.compile(ur'(?V1p)' + u'|'.join((ANY_WORD, SPACE, NUMBER, REST)))
    SPACE_RE = regex.compile(ur'(?V1p)^' + SPACE + '$')
    JOINER = u'￭'
    JOINER_RE = regex.compile(ur'(?V1p)[ ]*￭[ ]*')
    
    @classmethod
    def tokenize(cls, sentence):
        tokens = []
        token_types = []
        token_is_space = True
        for w_it in cls.TOKENIZER_RE.finditer(sentence):
            w = sentence[w_it.start():w_it.end()]
            cur_token_is_space = True if cls.SPACE_RE.match(w) else False
            if not token_is_space and not cur_token_is_space:
                tokens.append(cls.JOINER)
                token_types.append('J')
            token_is_space = cur_token_is_space
            if not cur_token_is_space:
                tokens.append(w)
                if cls.ANY_WORD_RE.match(w):
                    token_types.append('W')
                elif cls.NUMBER_RE.match(w):
                    token_types.append('N')
                else:
                    token_types.append('R')
        return tokens, token_types

    @classmethod
    def detokenize(cls, tokens):
        words = u' '.join(tokens)
        return cls.JOINER_RE.sub(u'', words)

def words_analyse(line, frequent_words, possible_replacment):
    tokens, token_types = ReTokenizer.tokenize(line)
    words, words2, possible, frequent, joiner, nojoiner, commas, dots = [], [], [], [], [], [], [], []
    lst_jnr = True
    for i, (w, t) in enumerate(zip(tokens, token_types)):
        if w == u',':
            commas.append(i)
        if w == u'.':
            dots.append(i)
        if t != 'J' and not lst_jnr:
            nojoiner.append(i)
        if t == 'J':
            joiner.append(i)
            lst_jnr = True
        else:
            lst_jnr = False
        if t == 'W':
            words.append(i)
            if len(w) >= 2:
                words2.append(i)
            if w.lower() in frequent_words:
                frequent.append(i)
            if w.lower() in possible_replacment:
                possible.append(i)
    return tokens, token_types, words, words2, possible, frequent, joiner, nojoiner, commas, dots


def random_typo(word):
    rnd = random.random()
    # random delete
    if len(word) >= 2 and rnd < 0.25:
        rnd2 = random.randint(0, len(word) - 1)
        return u''.join((word[:rnd2-1], word[rnd2:]))
    # random swap
    if len(word) >= 2 and rnd < 0.5:
        rnd2 = random.randint(0, len(word) - 2)
        return u''.join((word[:rnd2-1], word[rnd2+1], word[rnd2], word[rnd2+1:]))
    # random substitute
    if rnd < 0.75:
        rndchr = random.choice(CHARS)
        rnd2 = random.randint(0, len(word))
        return u''.join((word[:rnd2-1], rndchr, word[rnd2:]))
    # random add
    rnd2 = random.randint(0, len(word))
    rndchr = random.choice(CHARS)
    return u''.join((word[:rnd2], rndchr, word[rnd2:]))


def random_lowercase(line):
    capitals = list(ANY_CAPITAL.finditer(line))
    one_capital = random.choice(capitals)
    return u''.join((line[:one_capital.start()], one_capital.group().lower(), line[one_capital.start()+1:]))

def random_joiner_etc(tokens, joiner, nojoiner, commas, dots):
    rnd = random.random()
    # random delete
    if commas and rnd < 0.15:
        c_i = random.choice(commas)
        tokens.pop(c_i)
        return tokens
    if dots and rnd < 0.3:
        d_i = random.choice(dots)
        tokens.pop(d_i)
        return tokens
    if nojoiner and rnd < 0.45:
        j_i = random.choice(nojoiner)
        tokens.insert(j_i, ReTokenizer.JOINER)
        return tokens
    if joiner and rnd < 0.6:
        j_i = random.choice(joiner)
        tokens.pop(j_i)
        return tokens
    if rnd < 0.8:
        i = random.choice(range(len(tokens)))
        tokens[i:i] = [ReTokenizer.JOINER, u',']
        return tokens
    i = random.choice(range(len(tokens)))
    tokens[i:i] = [ReTokenizer.JOINER, u'.']
    return tokens

def add_noise_to_string(line, frequent_words, possible_replacment):
    tokens, token_types, words, words2, possible, frequent, joiner, nojoiner, commas, dots = words_analyse(line, frequent_words, possible_replacment)
    if not frequent:
        return None
    original = line
    if ANY_CAPITAL.search(line) and random.random() < 0.1:
        line = random_lowercase(line)
    if possible and random.random() < 0.3:
        w_i = random.choice(possible)
        tokens[w_i] = random.choice(possible_replacment[tokens[w_i].lower()])
    if random.random() < 0.1:
        w_i = random.choice(words)
        tokens[w_i] = random_typo(tokens[w_i])
    if random.random() < 0.4:
        tokens = random_joiner_etc(tokens, joiner, nojoiner, commas, dots)
    return u'\t'.join((original, ReTokenizer.detokenize(tokens)))



def main():
    all_possible_replaces = defaultdict(list)
    f = open('all_possible_replaces.txt')
    for l in f:
        w, s = l.strip('\n').decode('utf-8').split(u'\t')
        for ws in s.split(u','):
            all_possible_replaces[w].append(ws)
    words = set()
    f = open('words.txt')
    for l in f:
        w = l.strip('\n').decode('utf-8')
        words.add(w)

    for l in sys.stdin:
        snt = l.decode('utf-8').strip(u'\n')
        res = add_noise_to_string(snt, words, all_possible_replaces)
        if res:
            sys.stdout.write(res.encode('utf-8'))
            sys.stdout.write("\n")


if __name__ == '__main__':
    main()
