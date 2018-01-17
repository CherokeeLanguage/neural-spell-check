import sys
import random
import unicodedata
import OpenNMTTokenizer

def vw_format(line, vw_word_tokenize):
    return " ".join(vw_word_tokenize(line.encode('utf-8'))).replace("|", "PIPE").replace(":", "COLON")

def prepare_learn_string(tokenizer, label, w, s):
    return '{0} {1} | {2}'.format(label, w, vw_format(s, tokenizer.tokenize))

def prepare_batch(tokenizer, examples):
    random.shuffle(examples)
    if sum(1 for e in examples if e[0] == -1) == 0:
        neg_weigth = 1.0
    else:
        neg_weigth = '{0:0.6f}'.format(len(examples) * 0.5 / sum(1 for e in examples if e[0] == -1))
    if sum(1 for e in examples if e[0] == 1) == 0:
        pos_weigth = 1.0
    else:
        pos_weigth = '{0:0.6f}'.format(len(examples) * 0.5 / sum(1 for e in examples if e[0] == 1))
    for label, s in examples:
        w = pos_weigth if label == 1 else neg_weigth
        yield prepare_learn_string(tokenizer, label, w, s)

def main():
    tok = OpenNMTTokenizer.Tokenizer(mode="aggressive", case_feature=True)
    batch = []

    for l in sys.stdin:
        score, snt = l.decode('utf-8').strip(u'\n').split(u'\t', 1)
    
        batch.append((int(score), snt))
        if len(batch) > 10000:
            for rl in prepare_batch(tok, batch):
                sys.stdout.write(rl)
                sys.stdout.write(u"\n")
            batch = []
            
    if batch:
        for rl in prepare_batch(tok, batch):
            sys.stdout.write(rl)
            sys.stdout.write(u"\n")


if __name__ == '__main__':
    main()


