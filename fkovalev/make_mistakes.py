
import sys
import regex
import random
import traceback

ANY_CAPITAL = regex.compile('\p{Lu}')
CHARS = list(u"abcdefghijklmnopqrstuvwxyz")
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
    JOINER_RE = regex.compile(ur'(?V1p) ￭ ')
    
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


def get_random_word(line, min_size=1):
    words = line.split(u' ')
    counter = 0
    while True:
        # counter += 1
        # if counter > 100:
        #     # print line
        #     traceback.print_stack(sys.stderr)
        rnd = random.randint(0, len(words) - 1)
        if len(words[rnd]) >= min_size:
            break
    return words, rnd


def random_concat(line):
    words = line.split(u' ')
    rnd = random.randint(0, len(words) - 2)
    words[rnd:rnd+2] = [words[rnd] + words[rnd+1]]
    return u' '.join(words)

def random_split(line):
    words, rnd1 = get_random_word(line, 2)
    rnd2 = random.randint(1, len(words[rnd1]) - 1)
    words[rnd1] = u' '.join((words[rnd1][:rnd2], words[rnd1][rnd2:]))
    return u' '.join(words)

def random_lowercase(line):
    capitals = list(ANY_CAPITAL.finditer(line))
    one_capital = random.choice(capitals)
    return u''.join((line[:one_capital.start()], one_capital.group().lower(), line[one_capital.start()+1:]))

def random_double_char(line):
    words, rnd1 = get_random_word(line, 1)
    rnd2 = random.randint(0, len(words[rnd1]) - 1)
    words[rnd1] = u''.join((words[rnd1][:rnd2], words[rnd1][rnd2], words[rnd1][rnd2:]))
    return u' '.join(words)

def random_typo(line):
    rnd = random.random()
    # random delete
    if rnd < 0.25:
        words, rnd1 = get_random_word(line, 1)
        rnd2 = random.randint(0, len(words[rnd1]) - 1)
        words[rnd1] = u''.join((words[rnd1][:rnd2-1], words[rnd1][rnd2:]))
        return u' '.join(words)
    # random swap
    if max(map(len, line.split(u' '))) >= 2 and rnd < 0.5:
        words, rnd1 = get_random_word(line, 2)
        rnd2 = random.randint(0, len(words[rnd1]) - 2)
        words[rnd1] = u''.join((words[rnd1][:rnd2-1], words[rnd1][rnd2+1], words[rnd1][rnd2], words[rnd1][rnd2+1:]))
    # random substitute
    if rnd < 0.75:
        rndchr = random.choice(CHARS)
        words, rnd1 = get_random_word(line, 1)
        rnd2 = random.randint(0, len(words[rnd1]))
        words[rnd1] = u''.join((words[rnd1][:rnd2-1], rndchr, words[rnd1][rnd2:]))
        return u' '.join(words)
    # random add
    words, rnd1 = get_random_word(line, 1)
    rnd2 = random.randint(0, len(words[rnd1]))
    rndchr = random.choice(CHARS)
    words[rnd1] = u''.join((words[rnd1][:rnd2], rndchr, words[rnd1][rnd2:]))
    return u' '.join(words)

def random_legal_word(line):
    global DICT
    if DICT is None:
        DICT = set(line.strip() for line in open('/usr/share/dict/words'))
    words, rnd = get_random_word(line, 2)
    word = words[rnd]
    possible_errors = DICT & edits1(word, CHARS)
    if possible_errors:
        words[rnd] = random.choice(list(possible_errors))
    return u' '.join(words)


def edits1(word, alphabet):
    s = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes    = [a + b[1:] for a, b in s if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in s if len(b)>1]
    replaces   = [a + c + b[1:] for a, b in s for c in alphabet if b]
    inserts    = [a + c + b     for a, b in s for c in alphabet]
    return set(deletes + transposes + replaces + inserts)


def add_noise_to_string(line):
    no_mistakes = True
    if ANY_CAPITAL.search(line) and random.random() < 0.3:
        line = random_lowercase(line)
        no_mistakes = False
    if max(map(len, line.split(u' '))) >= 2 and random.random() < 0.1:
        line = random_split(line)
        no_mistakes = False
    if len(line.split(u' ')) > 1 and random.random() < 0.2:
        line = random_concat(line)
        no_mistakes = False
    if random.random() < 0.2:
        line = random_double_char(line)
        no_mistakes = False
    if max(map(len, line.split(u' '))) >= 2 and random.random() < 0.1:
        line = random_legal_word(line)
        no_mistakes = False
    if no_mistakes or random.random() < 0.3:
        line = random_typo(line)
        no_mistakes = False
    return line


def random_segment_line(line):
    result = []
    splt = random.randint(15, 70)
    while len(line) > splt + 15:
        result.append(line[:splt])
        line = line[splt:]
        splt = random.randint(15, 70)
    result.append(line)
    return result

def main():
    for l in sys.stdin:
        snt = l.decode('utf-8').strip(u'\n')
        res = []
        for seg in random_segment_line(snt):
            res.append(add_noise_to_string(seg))
        line = u''.join(res).encode('utf-8')
        # sys.stdout.write("\t".join((l, line)))
        sys.stdout.write(line)
        sys.stdout.write(u"\n")


if __name__ == '__main__':
    main()
