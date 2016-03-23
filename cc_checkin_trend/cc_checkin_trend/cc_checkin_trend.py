import argparse;

def create_parser():
    parser = argparse.ArgumentParser(
        description='Display ClearCase check-ins trend for specific branch'
    )

    parser.add_argument(
        'path', type=str,
        help='path in a VOB'
    )

    parser.add_argument(
        '-b', '--branch', type=str, required=True,
        help='branch name'
    )

    parser.add_argument(
        '-d', '--days', type=int, required=True,
        help='trend length'
    )

    return parser
    
def main():
    parser = create_parser()
    args = parser.parse_args()
    print "Computing check-in trend in branch " + args.branch + " for " + str(args.days) + " days under " + args.path + "\n"

if __name__ == '__main__':
    main()
    