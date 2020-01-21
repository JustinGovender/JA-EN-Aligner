import sys, fileinput, re, codecs

class Refiner:
    def __init__(self, fn):
        self.regexs = read_regex(fn)

    def convert_text(self, input_text):
        output_text = []
        for line in input_text:
            if line.strip() != "":
                for r in self.regexs:
                    line = re.sub(r'%s' % r[0], r[1], line.strip())
                output_text.append(line)
        return output_text


def read_regex(fn):
    regexs = []

    f = open(fn, 'r')

    for line in f:
        if not line.startswith("#"):
            tokens = line.split('\t')

            if len(tokens) == 1:
                tokens += [' ']

            tokens[0] = tokens[0][:-1] if tokens[0].endswith('\n') else tokens[0]
            tokens[1] = tokens[1][:-1] if tokens[1].endswith('\n') else tokens[1]

            regexs += [(tokens[0], tokens[1])]

    f.close()

    return regexs


if __name__ == "__main__":
    fn = sys.argv[1]
    _refiner = Refiner()
    regexs = read_regex(fn)

    for line in sys.stdin:
        if line.strip() != "":
            for r in regexs:
                line = re.sub(r'%s' % r[0], r[1], line.strip())

            sys.stdout.write(line + "\n")
        else:
            sys.stdout.write('\n')