import sys
import random
import unicodedata
import OpenNMTTokenizer

def vw_format(line, vw_word_tokenize):
    return " ".join(vw_word_tokenize(line.encode('utf-8'))).replace("|", "PIPE").replace(":", "COLON")

def prepare_predict_string(tokenizer, s):
    return ' | {0}'.format(vw_format(s, tokenizer.tokenize))

def main():
    tok = OpenNMTTokenizer.Tokenizer(mode="aggressive", case_feature=True)

    for l in sys.stdin:
        snt = l.decode('utf-8').strip(u'\n')
        line = prepare_predict_string(tok, snt)
        sys.stdout.write(line)
        sys.stdout.write(u"\n")


if __name__ == '__main__':
    main()


