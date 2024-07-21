import argparse
from controller import Controller


def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--imports', type=str, nargs='+', help='finance files', required=True)
    parser.add_argument('-x', '--export', type=str, help='path to export folder', required=True)
    parser.add_argument('-s', '--start_date', type=str, help='path to export folder', required=False)
    parser.add_argument('-e', '--end_date', type=str, help='path to export folder', required=False)
    return parser.parse_args()


if __name__ == "__main__":
    args = args_parser()
    Controller(args.start_date, args.end_date, *args.imports).export(args.export)
