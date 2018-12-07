from collections import defaultdict
import random
import sys


class PCFG(object):
    def __init__(self):
        self._rules = defaultdict(list)
        self._sums = defaultdict(float)

    def add_rule(self, lhs, rhs, weight):
        assert(isinstance(lhs, str))
        assert(isinstance(rhs, list))
        self._rules[lhs].append((rhs, weight))
        self._sums[lhs] += weight

    @classmethod
    def from_file(cls, filename):
        grammar = PCFG()
        with open(filename) as fh:
            for line in fh:
                line = line.split("#")[0].strip()
                if not line:
                    continue
                w, l, r = line.split(None, 2)
                r = r.split()
                w = float(w)
                grammar.add_rule(l,r,w)
        return grammar

    def is_terminal(self, symbol): return symbol not in self._rules

    def gen(self, symbol):
        if self.is_terminal(symbol): return symbol
        else:
            expansion = self.random_expansion(symbol)
            return " ".join(self.gen(s) for s in expansion)

    def gen_parse(self, symbol):
        if self.is_terminal(symbol): return symbol
        else:
            expansion = self.random_expansion(symbol)
            return "(" + symbol + " " + " ".join(self.gen_parse(s) for s in expansion) + ")"

    def random_sent(self):
        return self.gen("ROOT")

    def random_parse(self):
        return self.gen_parse("ROOT")

    def random_expansion(self, symbol):
        """
        Generates a random RHS for symbol, in proportion to the weights.
        """
        p = random.random() * self._sums[symbol]
        for r,w in self._rules[symbol]:
            p = p - w
            if p < 0: return r
        return r


def get_flags():
    n = 1
    should_parse = False
    if len(sys.argv) > 2:
        if len(sys.argv) > 3 and sys.argv[2] == '-n':
            n = int(sys.argv[3])
        elif sys.argv[2] == '-t':
            should_parse = True
    if len(sys.argv) > 4:
        if sys.argv[3] == '-n':
            n = int(sys.argv[4])
        elif len(sys.argv) > 3:
            if sys.argv[4] == '-t':
                should_parse = True

    return (n, should_parse)


if __name__ == '__main__':
    n, should_parse = get_flags()
    pcfg = PCFG.from_file(sys.argv[1])
    if should_parse:
        for i in range(n):
            print pcfg.random_parse()
    else:
        for i in range(n):
            print pcfg.random_sent()


