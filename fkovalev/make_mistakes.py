
import sys
import regex
import random
import traceback

ANY_CAPITAL = regex.compile('\p{Lu}')
CHARS = list(u"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ, .")
DICT = None

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
    if rnd < 0.33:
        words, rnd1 = get_random_word(line, 1)
        rnd2 = random.randint(0, len(words[rnd1]) - 1)
        words[rnd1] = u''.join((words[rnd1][:rnd2-1], words[rnd1][rnd2:]))
        return u' '.join(words)
    # random swap
    if max(map(len, line.split(u' '))) >= 2 and rnd < 0.66:
        words, rnd1 = get_random_word(line, 2)
        rnd2 = random.randint(0, len(words[rnd1]) - 2)
        words[rnd1] = u''.join((words[rnd1][:rnd2-1], words[rnd1][rnd2+1], words[rnd1][rnd2], words[rnd1][rnd2+1:]))
    # random add
    words, rnd1 = get_random_word(line, 1)
    rnd2 = random.randint(0, len(words[rnd1]) - 1)
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
