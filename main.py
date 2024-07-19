import argparse
from controller import Controller


def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--imports', type=str, nargs='+', help='finance files', required=True)
    parser.add_argument('-e', '--export', type=str, help='path to export folder', required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = args_parser()
    Controller(*args.imports).export(args.export)