import argparse, subprocess, os
import datetime, time

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

    # TODO interval in minutes (optional)

    return parser

def valid_branch(branch,vob):
    retcode = subprocess.call(["cleartool", "lstype","-s", "brtype:" + branch + "@\\" + vob], stdout=subprocess.PIPE)
    return (retcode==0)

def valid_days(days):
    return ((days >= MIN_DAYS) and (days <= MAX_DAYS)) 

def valid_path(path):
    if os.path.isdir(path):
        retcode = subprocess.call(["cleartool", "ls",path], stdout=subprocess.PIPE)
        return (retcode==0)
    else:
        return False;

def get_vob_of_path(path):
    return "admin"

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
    return

def get_date_before_today(num_days_ago):
    return get_date_before_some_date(datetime.datetime.now(), num_days_ago)

def get_date_before_some_date(reference_date, num_days_ago):
    return (reference_date - datetime.timedelta(days=num_days_ago))

def cctime_to_datetime(cctime):
    # ClearCase time format: %Y-%m-%dT%H:%M:%S+<timezone hour:minute>
    # TODO: consider the time zone
    ts = time.strptime(cctime,"%Y-%m-%dT%H:%M:%S+02:00")
    return datetime.datetime(ts.tm_year,ts.tm_mon,ts.tm_mday,ts.tm_hour,ts.tm_min,ts.tm_sec)
    

def get_checkin_times(path, branch, since_date, upto_date):
    upto_not_including_date = upto_date + datetime.timedelta(days=1)
    query = 'brtype(' + branch + ')&&created_since(' + since_date.strftime("%d-%b-%Y") + ')&&!created_since(' + upto_not_including_date.strftime("%d-%b-%Y") + ')'
    #out = subprocess.check_output(["cleartool","find",path,"-version",query,"-print"],shell=False)
    out = subprocess.check_output(["cleartool","find",path,"-version",query,"-exec","cleartool desc -fmt %d\\n %CLEARCASE_XPN%"],shell=False)
    timestamps = filter(None, out.split('\r\n'))
    return [cctime_to_datetime(x) for x in timestamps]

def main():
    parser = create_parser()
    args = parser.parse_args()
    validate_args(args)
    print "Check-in Trend in branch \'" + args.branch + "\' for " + str(args.days) + " days under " + args.path + "\n"
    times_list = get_checkin_times(args.path,args.branch,get_date_before_today(args.days),datetime.datetime.now())
    print "Data points:\n" + str(times_list)

if __name__ == '__main__':
    main()
    