import argparse


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-q", "--query", default=None, type=str, help="Query String"
    )
    parser.add_argument(
        "-t", "--type", default=None, type=str, help="Query String Type"
    )
    parser.add_argument(
        "-T", "--test", action='store_true',
        help="Skip main logic and load functions, use with python -i flag"
    )
    return parser.parse_args()
