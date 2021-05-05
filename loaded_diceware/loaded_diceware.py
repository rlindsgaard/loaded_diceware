"""Main module."""
from argparse import ArgumentParser
import getpass
import hashlib
import pyperclip
import sys

# TODO: Obtain wordlists from eff.org and compare with hash
# on first use.
builtin_wordlists = {
    'long': {
        'dice': 5,
        'source': 'eff_large_wordlist.txt',
    },
    'short': {
        'dice': 4,
        'source': 'eff_short_wordlist_1.txt',
    },
    'short-prefix': {
        'dice': 4,
        'source': 'eff_short_wordlist_2_0.txt',
    }
}
MASTER_SALT = b'correct horse battery staple'


def main(opts):
    seed_generator = initialise_seed(opts.domain.encode())
    container = DiceContainer()

    wordlist_config = builtin_wordlists[opts.wordlist]

    for _ in range(wordlist_config['dice']):
        seed = seed_generator.digest()
        seed_generator.update(seed)

        die = WeightedDie(seed, 'sha512_256')
        container.add(die)

    wordlist = Wordlist(wordlist_config['source'])

    words = [
        wordlist.from_roll(container.roll())
        for _ in range(opts.words)
    ]

    passphrase = ' '.join(words)

    try:
        pyperclip.copy(passphrase)
        print('Passphrase copied to clipboard')
    except pyperclip.PyperclipException:
        print('Could not copy passphrase to clipboard')
        query = input('Print to terminal? (type "yes") ')
        if query != 'yes':
            sys.exit(1)
        print(passphrase)


def initialise_seed(domain):
    # TODO: Store/obtain seed from file
    # TODO^2: Store it in memory in background process
    seed = getpass.getpass('Master: ').encode()

    salt = hashlib.pbkdf2_hmac(
        'sha256',
        seed,
        MASTER_SALT,
        100000,
    )
    salt = hashlib.new('sha512_256')
    salt.update(seed)

    password = getpass.getpass('Password: ').encode()

    genesis_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password,
        salt.digest(),
        100000,
    )

    seed_generator = SeedGenerator(genesis_hash)
    seed_generator.update(domain)

    return seed_generator


class SeedGenerator(object):
    def __init__(self, seed):
        self.generator = hashlib.new('sha512_256')
        self.generator.update(seed)

    def update(self, bs):
        self.generator.update(bs)

    def digest(self):
        d = self.generator.digest()
        self.update(d)
        return d


class Wordlist(object):
    def __init__(self, filename):
        self.wordlist = {}
        self.read_file(filename)

    def read_file(self, filename):
        with open(filename, mode='r') as f:
            for line in f:
                key, word = line.split()
                self.wordlist[key] = word

    def from_roll(self, roll):
        roll_str = ''.join(map(str, roll))
        return self.wordlist[roll_str]


class DiceContainer(object):
    def __init__(self, dice=None):
        self.dice = dice or []

    def add(self, die):
        self.dice.append(die)

    def roll(self):
        for die in self.dice:
            die.roll()
        return self.eyes()

    def eyes(self):
        return [
            d.eyes()
            for d in self.dice
        ]


class WeightedDie(object):
    def __init__(self, seed, hashing_algorithm):
        cipher = hashlib.new(hashing_algorithm)
        cipher.update(seed)
        self.cipher = cipher

    def roll(self):
        self.cipher.update(self.cipher.digest())
        return self.eyes()

    def eyes(self):
        intdigest = int.from_bytes(self.cipher.digest(), 'big')
        return (intdigest % 6) + 1


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-d', '--domain',
        type=str,
        help='Context for passphrase',
        required=True,
    )
    parser.add_argument(
        '-w', '--words',
        type=int,
        default=6,
        help='Number of words the passphrase consists of.',
    )
    parser.add_argument(
        '--wordlist',
        choices=builtin_wordlists.keys(),
        default='long',
    )
    parser.add_argument(
        '-p', '--print',
        action='store_true',
        default=False,
    )
    main(parser.parse_args())
