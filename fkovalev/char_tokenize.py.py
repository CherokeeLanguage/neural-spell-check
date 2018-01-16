# coding: utf-8
import sys


def main():
    for l in sys.stdin:
        snt = l.decode('utf-8').strip(u'\n').replace(u' ', u'■')
        print u' '.join(snt).encode('utf-8')

if __name__ == '__main__':
    main()