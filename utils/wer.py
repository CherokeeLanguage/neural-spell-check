# encoding: utf-8
"""Voice data utilities and related stuff"""

from __future__ import unicode_literals, division, print_function

import collections
import argparse

class TranscriptionErrorType(object):
    """Enumeration of 4 possible errors: correct (no error), substitution, insertion and deletion."""
    values = ('correct', 'substitution', 'insertion', 'deletion')
    correct, substitution, insertion, deletion = values

class FileFormat(object):
    """Enumeration of trasncription file formats"""
    values = ('tsv', 'parentheses', 'space', 'tsv4')
    tsv = parentheses = space = tsv4 = values

# These namedtuples are used to pass results around between the functions
WERResult = collections.namedtuple('WERResult', ['score', 'errors'])
UtteranceResult = collections.namedtuple('UtteranceResult', ['reference', 'hypothesis', 'wer'])
FileResults = collections.namedtuple('FileResults', ['score', 'utterances'])


NUMBER_CONVERSIONS = {
    '1': 'one',
    '2': 'two',
    '3': 'three',
    '4': 'four',
    '5': 'five',
    '6': 'six',
    '7': 'seven',
    '8': 'eight',
    '9': 'nine',
    '10': 'ten',
    '11': 'eleven',
    '12': 'twelve',
    '13': 'thirteen',
    '14': 'fourteen',
    '15': 'fifteen',
    '16': 'sixteen',
    '17': 'seventeen',
    '18': 'eighteen',
    '19': 'nineteen',
    '20': 'twenty',
    '21': 'twenty one',
    '22': 'twenty two',
    '23': 'twenty three',
    '24': 'twenty four',
    '25': 'twenty five',
    '26': 'twenty six',
    '27': 'twenty seven',
    '28': 'twenty eight',
    '29': 'twenty nine',
    '30': 'thirty',
    '31': 'thirty one',
    '1st': 'first',
    '2nd': 'second',
    '3rd': 'third',
    '4th': 'fourth',
    '5th': 'fifth',
    '6th': 'sixth',
    '7th': 'seventh',
    '8th': 'eighth',
    '9th': 'ninth',
    '10th': 'tenth',
    '11th': 'eleventh',
    '12th': 'twelfth',
    '13th': 'thirteenth',
    '14th': 'fourteenth',
    '15th': 'fifteenth',
    '16th': 'sixteenth',
    '17th': 'seventeenth',
    '18th': 'eighteenth',
    '19th': 'nineteenth',
    '20th': 'twentieth',
    '21st': 'twenty first',
    '22nd': 'twenty second',
    '23rd': 'twenty third',
    '24th': 'twenty fourth',
    '25th': 'twenty fifth',
    '26th': 'twenty sixth',
    '27th': 'twenty seventh',
    '28th': 'twenty eighth',
    '29th': 'twenty ninth',
    '30th': 'thirtieth',
    '31st': 'thirty first',
    '2014': 'two thousand fourteen',
}

EQUIV_NUMBERS = (
    set([u'four', u'fourth']),
    set([u'five', u'fifth']),
    set([u'sixth', u'six']),
    set([u'seventh', u'seven']),
    set([u'eight', u'eighth']),
    set([u'ninth', u'nine']),
    set([u'ten', u'tenth']),
    set([u'eleven', u'eleventh']),
    set([u'twelve', u'twelfth']),
    set([u'thirteenth', u'thirteen']),
    set([u'fourteen', u'fourteenth']),
    set([u'fifteenth', u'fifteen']),
    set([u'sixteenth', u'sixteen']),
    set([u'seventeen', u'seventeenth']),
    set([u'eighteenth', u'eighteen']),
    set([u'nineteenth', u'nineteen']),
    set([u'twenty', u'twentieth']),
    set([u'thirtieth', u'thirty']),
)

EQUIV_SPELLING = (
    set(["o'hare", "ohare"]),
    set(["lets", "let's"]),
    set(["don't", "dont"]),
    set(["didn't", "didnt"]),
    set(["doesn't", "doesnt"]),
    set(["what's", "whats"]),
    set(["that's", "thats"]),
    set(["it's", "its"]),
    set(["n", "and"]),
    set(["ok", "okay"]),
    set(["st", "st.", "saint"]),
    set(["o'clock", "oclock"]),
    set(["allegany", "allegheny"]),
    set(["through", "thru"]),
)

EQUIV_MISC = ({'the', 'a'}, {'hotel', 'hotels'}, {'night', 'nights'})

EQUIV_ALL = EQUIV_NUMBERS + EQUIV_SPELLING + EQUIV_MISC

IGNORABLES = {'[noise]'} # words to be completely removed from the ASRt transcription and ignored in WER calculation


class TranscriptionError(object):
    """An error in transcription, with information about the words in error and the type. Error can be 'correct'"""

    def __init__(self, type_, position, ref_word, hyp_word):
        self.ref = ref_word
        self.hyp = hyp_word
        self.position = position
        self.type_ = type_

    def __repr__(self):
        return b'TranscriptionError({}, {}, {}, {})'.format(*[repr(x) for x in [self.type_, self.position, self.ref, self.hyp]])

    def __unicode__(self):
        return "{}-{}({},{})".format(self.position, self.type_, self.ref, self.hyp)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __eq__(self, other):
        """Define an equality test"""
        if isinstance(other, type(self)):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        """Define a non-equality test"""
        if isinstance(other, type(self)):
            return not self.__eq__(other)
        return NotImplemented

    def __hash__(self):
        """Override the default hash behavior (that returns the id or the object)"""
        return hash(tuple(sorted(self.__dict__.items())))

    def to_text(self):
        """Convert the error to two strings, one which goes to the ref sentence and one to the hypothesis sentence.

        Correct pairs will return (ref, hyp), while deletion will be (ref, '----'), insertions are ('++++', hyp) and substitution
        is represented by (#ref#, #hyp#) (surrounded by hashes). all pairs will have equal length (pad by spaces if needed).

        """
        if self.type_ == TranscriptionErrorType.correct:
            fmt = '{{:<{}}}'.format(max(len(self.ref), len(self.hyp)))
            return (fmt.format(self.ref), fmt.format(self.hyp))
        elif self.type_ == TranscriptionErrorType.substitution:
            fmt = '#{{:<{}}}#'.format(max(len(self.ref), len(self.hyp)))
            return (fmt.format(self.ref), fmt.format(self.hyp))
        elif self.type_ == TranscriptionErrorType.insertion:
            return ('+' * len(self.hyp), self.hyp)
        else:
            return (self.ref, '-' * len(self.ref))


def format_errors(errors):
    """Format a list of TranscriptionErrors to 2 strings with two to_text() representations of the sentences"""
    if not errors:
        return '///EMPTY///', '///EMPTY///'
    ref, hyp = zip(*[err.to_text() for err in errors])
    return " ".join(ref), " ".join(hyp)


def wer(ref_sentence, hyp_sentence, conversions=None, equiv_classes=tuple()):
    """Calculate Word Error Rate with Levenshtein Distance.

    Complexity is O(nm) in time and space, and uses sets of errors so we can analyze the results later.

    Arguments:
        ref_sentence: unicode sentence, the correct transcriptions
        hyp_sentence: unicode sentence, proposed transcription
        conversions: mapping of src-word => dest-word, applied on the hypotheses
        equiv_classes: list of sets of equivalent words (treated as not error)

    Returns: WERResult

    """
    T = TranscriptionErrorType # pylint: disable=invalid-name
    ref = [word for word in ref_sentence.strip().lower().split() if word not in IGNORABLES]
    hyp = [word for word in hyp_sentence.strip().lower().split() if word not in IGNORABLES]
    if conversions:
        temp = []
        for word in hyp:
            word = conversions.get(word, word)
            temp.extend(word.split())
        hyp = temp
    # Special case where the reference sentence is empty, return insertions errors (if hypothesis isn't empty) or correct (if it is)
    if not len(ref):
        if not len(hyp): # both empty
            return WERResult(0, [])
        else:
            return WERResult(len(hyp), tuple(TranscriptionError(T.insertion, 0, None, word) for word in hyp))
    # Each cell holds None (uncomputed), or a tuple of known errors till this position (starts from 0) - not including the position
    # i is always the position/index to the reference word, while j is an index/position of the hypothesis word
    err = [[None] * (len(hyp) + 1) for _ in range(len(ref) + 1)]
    err[0][0] = tuple()
    if len(ref):
        err[1][0] = tuple()
    if len(hyp):
        err[0][1] = tuple()
    for i in range(1, len(err)):
        err[i][0] = err[i-1][0] + (TranscriptionError(T.deletion, i-1, ref[i-1], None),)
    for j in range(1, len(err[0])):
        err[0][j] = err[0][j-1] + (TranscriptionError(T.insertion, j-1, None, hyp[j-1]),)

    for i in range(1, len(err)):
        for j in range(1, len(err[0])):
            if ref[i-1] == hyp[j-1] or any({ref[i-1], hyp[j-1]} <= equiv for equiv in equiv_classes):
                err[i][j] = err[i-1][j-1] + (TranscriptionError(T.correct, i-1, ref[i-1], hyp[j-1]),)
            else:
                deletion = (err[i-1][j], TranscriptionError(T.deletion, i-1, ref[i-1], None))
                insertion = (err[i][j-1], TranscriptionError(T.insertion, 0, None, hyp[j-1]))
                substitution = (err[i-1][j-1], TranscriptionError(T.substitution, i-1, ref[i-1], hyp[j-1]))
                best = sorted([substitution, insertion, deletion], key=lambda errs: sum(x.type_ != T.correct for x in errs[0]))[0]
                err[i][j] = best[0] + (best[1],)

    score = sum(x.type_ != T.correct for x in err[len(ref)][len(hyp)]) / len(ref)
    return WERResult(score, err[len(ref)][len(hyp)])


def _wer_many(ref_sentences, asr_sentences, conversions=None, equiv_classes=tuple(), nbest=False):
    """Run WER for each pair of sentences, and in addition, calculates the total WER.

    Returns the (total WER, list of UtteranceResult). For parameters, see wer() function.

    """
    if nbest:
        # running wer() for each ASR hypothesis, then taking the minimal WER are discard all others
        single_results = [sorted(wer(ref, asr, conversions, equiv_classes) for asr in asrs)[0]
                          for ref, asrs in zip(ref_sentences, asr_sentences)]
    else:
        single_results = [wer(ref, asr, conversions, equiv_classes) for ref, asr in zip(ref_sentences, asr_sentences)]
    # Undoing the division to get the total number of errors
    scores = [result.score for result in single_results]
    total_wer = [(score, len(ref.strip().split())) for score, ref in zip(scores, ref_sentences)]
    total_wer = sum(score * length for score, length in total_wer) / sum(lengths for _, lengths in total_wer)
    return total_wer, single_results


def read_transcriptions(fil, format_, encoding='utf-8', nbest=False):
    """Read transcriptions from a file with the specified format and encoding and return MUUID => transcription dictionary.

    Possible formats are from FileFormat. if `fil` is a string, assume its a filename and try to open it, otherwise assume file
    object.

    if `nbest` is True, assume there can be several transcriptions per MUUID, and return a dictionary of
    MUUID => list of transcriptions, in the order they appear in the file. If `nbest` is False, return MUUID => first transcription
    appearing in the file (the file can contain multiple transcriptions).

    """

    def read_paren_transcriptions(lines):
        """Read the parentheses-formatted transcriptions in the format TRANSCRIPTION ... (MUUID1). Return list of (MUUID, text)."""
        # if a file failed transcription, then only its MUUID in parenthesis is on the line - check for it
        data = [line.rsplit(' ', 1) if ' ' in line else ('', line) for line in lines]
        return [(muuid[1:-1], text) for text, muuid in data]

    def read_tsv_transcriptions(lines):
        """Read tab-separated transcriptions and return a list of (MUUID, transcription)"""
        return [line.split('\t') for line in lines]

    def read_spaced_transcriptions(lines):
        """Read space-separated transcriptions (MUUID TEXT) and return list of (MUUID, transcription)"""
        return [line.split(" ", 1) for line in lines]

    extractors = {FileFormat.parentheses: read_paren_transcriptions,
                  FileFormat.tsv: read_tsv_transcriptions,
                  FileFormat.space: read_spaced_transcriptions}
    if isinstance(fil, basestring):
        fil = open(fil, 'rU')
    data = extractors[format_](line for line in fil.read().decode(encoding).splitlines() if line.strip())
    if nbest:
        out = collections.defaultdict(list)
        for muuid, text in data:
            out[muuid].append(text)
        return dict(out)
    else:
        return dict(reversed(data)) # Reverse the data so the first transcription will overwrite the others, and we get only firsts


def align_transcriptions(map1, map2, partial=False):
    """Given two mappings of MUUID to transcriptions, return 3 lists: (muuids, trans1, trans2) which are aligned to each other.

    Aligning is making sure that for each index i, trans1[i] and trans2[i] are of the muuid in muuids[i]. muuids which are present
    at only one mapping are removed.

    If `partial` is True, it enables the one MUUID to be the the substring of another to construct a match, so it enables short
    MUUIDs to be mapped to longer one which has more data (session id, user etc.).

    """
    muuids = []
    trans1 = []
    trans2 = []
    for muuid1, tr1 in map1.items():
        if muuid1 in map2:
            muuids.append(muuid1)
            trans1.append(tr1)
            trans2.append(map2[muuid1])
        elif partial:
            matches = [muuid2 for muuid2 in map2 if muuid1 in muuid2 or muuid2 in muuid1]
            if matches:
                assert len(matches) == 1
                muuid2 = matches[0]
                muuids.append(muuid1 if len(muuid1) < len(muuid2) else muuid2) # take the shortest for readability
                trans1.append(tr1)
                trans2.append(map2[muuid2])
    return muuids, trans1, trans2


def get_wer_for_file(ref_file, hyp_file, ref_format=FileFormat.tsv, hyp_format=FileFormat.tsv,
                     equiv_classes=EQUIV_ALL, nbest=False):
    """Return WER and detailed changes for hypothesis transcriptions.

    ref_file: text file with transcriptions at `ref_format` (either filename or file object)
    hyp_file: text file with transcriptions at `hyp_format` (either filename or file object)

    Return (WER (float), dict of MUUID => (ref, hyp, list of TranscriptionErrors)).

    """
    ref_map = read_transcriptions(ref_file, ref_format)
    asr_map = read_transcriptions(hyp_file, hyp_format, nbest=nbest)
    muuids, ref_sentences, asr_sentences = align_transcriptions(ref_map, asr_map, partial=True)
    total_wer, wer_results = _wer_many(ref_sentences, asr_sentences, conversions=NUMBER_CONVERSIONS, equiv_classes=equiv_classes,
                                       nbest=nbest)
    results = {muuid: UtteranceResult(ref, asr, wer_result)
               for muuid, ref, asr, wer_result in zip(muuids, ref_sentences, asr_sentences, wer_results)}
    return FileResults(total_wer, results)


def get_errors_breakdown(file_results, aggregate_substitutions=True):
    """Return a dictionary of TranscriptionErrorType => Counter of error word(s).

    `file_results` is a FileResults object.
    `aggregate_substitutions` makes substitution error counter use only the reference word (if True),
    or to count each (ref, hyp) pair as different error (if False).

    """
    counts = {type_: collections.Counter() for type_ in TranscriptionErrorType.values if type_ != TranscriptionErrorType.correct}
    for utterance in file_results.utterances.itervalues():
        for err in utterance.wer.errors:
            if err.type_ == TranscriptionErrorType.correct:
                continue
            elif err.type_ == TranscriptionErrorType.insertion:
                counts[err.type_][err.hyp] += 1
            elif err.type_ == TranscriptionErrorType.deletion:
                counts[err.type_][err.ref] += 1
            elif err.type_ == TranscriptionErrorType.substitution:
                key = err.ref if aggregate_substitutions else (err.ref, err.hyp)
                counts[err.type_][key] += 1
    return counts


def get_formatted_errors(file_results, full=True):
    """Return strings of formatted results, with 2 lines per log (which was incorrect), sorted by muuid.

    if `full`, output all lines (not only these with errors).

    `file_results` is a FileResults object.

    """
    out = []
    for muuid, utterance in sorted(file_results.utterances.items()): # pylint: disable=unused-variable
        if utterance.wer.score or full:
            line1, line2 = format_errors(utterance.wer.errors) # pylint: disable=unused-variable
            out.append('{muuid} {line1}\n{muuid} {line2}'.format(**locals()))
    return out


def get_3way_diff(file_results1, file_results2):
    """Return two dictionaries of the same structure as the input dictionary, with only the diffed errors between the results"""
    out1 = {}
    out2 = {}
    for muuid, utterance1 in file_results1.utterances.items():
        try:
            utterance2 = file_results2.utterances[muuid]
        except KeyError:
            continue
        if utterance1.wer.score != utterance2.wer.score or utterance1.wer.errors != utterance2.wer.errors:
            out1[muuid] = utterance1
            out2[muuid] = utterance2
    return out1, out2


def get_formatted_3way_errors(prefix_fmt, filename1, utterances1, filename2, utterances2):
    """Return strings of formatted pairs of transcriptions and their errors compared to the reference"""
    out = []
    for muuid, utterance1 in utterances1.items():
        utterance2 = utterances2[muuid]
        score1, score2 = utterance1.wer.score, utterance2.wer.score
        sign = '<' if score1 < score2 else ('>' if score2 < score1 else '=')
        best_answer = filename1 if sign == '<' else (filename2 if sign == '>' else 'both')
        wer_string = '{:.2%} {} {:.2%}'.format(score1, sign, score2)
        error_string = format_errors(utterance1.wer.errors) + format_errors(utterance2.wer.errors)
        # The errors string now have the reference sentence twice (first and third line), we will remove the third line
        # and add the prefix before each one for easy identification
        prefix_fmt = '{{:{length}}}:\t'.format(length=max(len(filename1), len(filename2)))
        prefixes = [prefix_fmt.format('ref'), prefix_fmt.format(filename1), None, prefix_fmt.format(filename2)]
        error_string = [prefix + line for i, (line, prefix) in enumerate(zip(error_string, prefixes)) if i != 2]
        out.append('{muuid}\nwinner: {best_answer} ({wer_string})\n{error_string}'.format(
            muuid=muuid, best_answer=best_answer, wer_string=wer_string, error_string='\n'.join(error_string)))
    return out


def _get_equiv(suppress):
    """Return the appropriate equiv_classes argument from the suppress list"""
    if 'none' in suppress:
        return tuple()
    if 'all' in suppress:
        return EQUIV_ALL
    classes = []
    if 'spelling' in suppress:
        classes += list(EQUIV_SPELLING)
    if 'numbers' in suppress:
        classes += list(EQUIV_NUMBERS)
    if 'misc' in suppress:
        classes += list(EQUIV_MISC)
    return tuple(classes)


def _guess_format(filename):
    """Guess format from filename"""
    line = next(open(filename))
    if '\t' in line or filename.endswith('tsv'):
        if line.count('\t') > 1:
            return FileFormat.tsv4
        else:
            return FileFormat.tsv
    if line.strip().endswith(')'):
        return FileFormat.parentheses
    return FileFormat.space

def _output_results(file_results, outputs):
    """Print the requested `outputs` from `file_results`, with delimiter line if more than one output requested"""
    for i, output in enumerate(outputs):
        if i: # break between different results
            print('\n{}\n'.format('='*80))
        if output == 'score':
            print('{:.2%}'.format(file_results.score))
        if output == 'diff':
            print('\n\n'.join(get_formatted_errors(file_results, full=False)))
        if output == 'full':
            print('\n\n'.join(get_formatted_errors(file_results, full=True)))
        if output == 'breakdown':
            errs = get_errors_breakdown(file_results)
            for errtype in TranscriptionErrorType.values:
                if errtype == TranscriptionErrorType.correct:
                    continue
                print('{} = {}'.format(errtype, sum(errs[errtype].itervalues())))
                for word, count in errs[errtype].most_common():
                    print('\t{}: {}'.format(word, count))
                print()


def _output_3way_results(filename1, file_results1, filename2, file_results2, outputs):
    """Print the requested `outputs` from `file_results`, with delimiter line if more than one output requested"""
    prefix_fmt = '{{:{length}}}:\t'.format(length=max(len(filename1), len(filename2)))
    prefix1 = prefix_fmt.format(filename1)
    prefix2 = prefix_fmt.format(filename2)
    for i, output in enumerate(outputs):
        if i: # break between different results
            print('\n{}\n'.format('='*80))
        if output == 'score':
            for prefix, result in zip([prefix1, prefix2], [file_results1, file_results2]):
                print('{}{:.2%}'.format(prefix, result.score))
        if output == 'diff': # in 3-way comparison, we need the difference between the 2 results, not against the reference
            diff1, diff2 = get_3way_diff(file_results1, file_results2)
            print('\n\n'.join(get_formatted_3way_errors(prefix_fmt, filename1, diff1, filename2, diff2)))
        if output == 'full':
            print('\n\n'.join(get_formatted_3way_errors(prefix_fmt, filename1, file_results1.utterances, filename2,
                                                        file_results2.utterances)))
        if output == 'breakdown':
            raise ValueError('breakdown comparison not supported')


def main(args):
    """Calculate WER for a given file and prints output"""
    equiv = _get_equiv(args.suppress)
    ref_format = args.ref_format or _guess_format(args.reference.name)
    hyp_format = args.hyp_format or _guess_format(args.hypothesis.name)
    file_results = get_wer_for_file(args.reference, args.hypothesis, ref_format, hyp_format, equiv, args.nbest)
    if args.hypothesis2:
        args.reference.seek(0)
        hyp2_format = args.hyp2_format or _guess_format(args.hypothesis2.name)
        file_results2 = get_wer_for_file(args.reference, args.hypothesis2, ref_format, hyp2_format, equiv, args.nbest)
        _output_3way_results(args.hypothesis.name, file_results, args.hypothesis2.name, file_results2, args.output)
    else:
        _output_results(file_results, args.output)


def parse_args():
    """Parse and return command line arguments from sys.argv"""
    parser = argparse.ArgumentParser(description='word error rate calculator between files')
    parser.add_argument('reference', type=argparse.FileType('r'), help='reference transcriptions file')
    parser.add_argument('hypothesis', type=argparse.FileType('r'), help='hypothesis transcriptions file')
    parser.add_argument('--ref-format', choices=FileFormat.values,
                        help='reference file format, if not given try to identify from structure and suffix')
    parser.add_argument('--hyp-format', choices=FileFormat.values,
                        help='hypothesis file format, if not given try to identify from structure and suffix')
    parser.add_argument('-s', '--suppress', action='append', default='none', choices=('none', 'spelling', 'numbers', 'misc', 'all'),
                        help='which types of errors to ignore when calculating error rate, default is all')
    parser.add_argument('-o', '--output', action='append', choices=('score', 'full', 'diff', 'breakdown'),
                        help='which kind of output to use, can concatenate more than one (default is score)')
    parser.add_argument('--nbest', action='store_true', help='if multiple hypotheses available to an utterance, use the best one')
    parser.add_argument('--3way', type=argparse.FileType('r'), help='Add another hypothesis file to create a 3-way comparison',
                        dest='hypothesis2')
    parser.add_argument('--3way-format', choices=FileFormat.values, dest='hyp2_format',
                        help='Second hypothesis file format, in case it is supplied')
    args = parser.parse_args()
    if not args.output:
        args.output = ['score']
    if not args.suppress:
        args.suppress = ['all']
    return args


if __name__ == '__main__':
    main(parse_args())
