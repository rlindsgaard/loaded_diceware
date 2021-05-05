"""Console script for loaded_diceware."""
import argparse
import getpass
import sys


def main():
    """Console script for loaded_diceware."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        title='init',
        help='Initialise',
    )
    parser.add_argument(
        '-d',
        '--domain',
    )
    parser.add_argument('_', nargs='*')
    args = parser.parse_args()

    seed = getpass(prompt='Seed:')
    password = getpass('Password: ')

    print("Arguments: " + str(args._))
    print("Replace this message by putting your code into "
          "loaded_diceware.cli.main")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
