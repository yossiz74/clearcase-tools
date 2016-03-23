import argparse, subprocess, os

MIN_DAYS = 1
MAX_DAYS = 7

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
        help='trend length in days (' + str(MIN_DAYS) + "-" + str(MAX_DAYS) + ')'
    )

    return parser

def valid_branch(branch,vob):
    retcode = subprocess.call(["cleartool", "lstype","-s", "brtype:" + branch + "@\\" + vob])
    return (retcode==0)

def valid_days(days):
    return ((days >= MIN_DAYS) and (days <= MAX_DAYS)) 

def valid_path(path):
    return os.path.isdir(path);

def get_vob_of_path(path):
    return "Unknown"
    
def validate_args(args):
    if not valid_path(args.path):
        print "Invalid path \'" + args.path+ "\'\n"
        raise SystemExit
    vob=get_vob_of_path(args.path)
    if not valid_branch(args.branch,vob):
        print "Unknown branch type \'" + args.branch + "\'\n"
        raise SystemExit
    if not valid_days(args.days):
        print "Invalid number of days \'" + args.path+ "\', must be between "  + str(MIN_DAYS) + "-" + str(MAX_DAYS) + "\n"
        raise SystemExit
    return;

def main():
    parser = create_parser()
    args = parser.parse_args()
    validate_args(args)
    print "Computing check-in trend in branch \'" + args.branch + "\' for " + str(args.days) + " days under " + args.path + "\n"

if __name__ == '__main__':
    main()
    