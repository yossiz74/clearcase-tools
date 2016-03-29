import argparse, subprocess, os
import datetime, time
import math
import collections

MIN_DAYS = 1
MAX_DAYS = 7
DEFAULT_INTERVAL = 60
ADMIN_VOB = 'admin' # TODO: figure out from environment or command line argument
HISTOGRAM_CHAR = '*'

def create_parser():
    parser = argparse.ArgumentParser(
        description='Display ClearCase check-ins trend for specific branch'
    )

    # path in view
    parser.add_argument(
        'path', type=str, nargs='+',
        help='path in a view'
    )

    # branch
    parser.add_argument(
        '-b', '--branch', type=str, required=True,
        help='global branch name'
    )

    # days ago
    parser.add_argument(
        '-d', '--days', type=int, required=True,
        help='trend length in days (' + str(MIN_DAYS) + "-" + str(MAX_DAYS) + ')'
    )

    # interval in minutes (optional)
    parser.add_argument(
        '-i', '--interval', type=int, required=False, default=DEFAULT_INTERVAL,
        help='interval in minutes (default: ' + str(DEFAULT_INTERVAL) + ')'
    )

    parser.add_argument(
        '--csv', action='store_true', required=False,
        help='Write the results as comma separated values.'
    )

    return parser

def valid_branch(branch,vob):
    retcode = subprocess.call(["cleartool", "lstype","-s", "brtype:" + branch + "@\\" + vob], stdout=subprocess.PIPE)
    return (retcode==0)

def valid_days(days):
    return ((days >= MIN_DAYS) and (days <= MAX_DAYS)) 

def valid_interval(interval):
    return (interval >= 1)

def valid_path(path):
    if os.path.isdir(path):
        desc = subprocess.check_output(["cleartool", "desc","-s",path], shell=False)
        return ('@@' in desc)
    else:
        return False

def get_vob_of_path(path):
    return "admin"

def validate_args(args):
    for p in args.path:
        if not valid_path(p):
            print "Invalid path \'" + p + "\'\n"
            raise SystemExit
    if not valid_branch(args.branch,ADMIN_VOB):
        print "Unknown global branch type \'" + args.branch + "\'\n"
        raise SystemExit
    if not valid_days(args.days):
        print "Invalid number of days \'" + str(args.days) + "\', must be between "  + str(MIN_DAYS) + "-" + str(MAX_DAYS) + "\n"
        raise SystemExit
    return

#def get_date_before_today(num_days_ago):
#    return get_date_before_some_date(datetime.datetime.now(), num_days_ago)

def get_date_before_some_date(reference_date, num_days_ago):
    return (reference_date - datetime.timedelta(days=num_days_ago))

def cctime_to_datetime(cctime):
    # ClearCase time format: %Y-%m-%dT%H:%M:%S+<timezone hour:minute>
    # TODO: consider the time zone, for now we remove it
    base_cctime = cctime[:-6]
    ts = time.strptime(base_cctime,"%Y-%m-%dT%H:%M:%S")
    return datetime.datetime(ts.tm_year,ts.tm_mon,ts.tm_mday,ts.tm_hour,ts.tm_min,ts.tm_sec)
    

def get_checkin_times(path, branch, since_date, upto_date):
    if not isinstance(path,basestring):
        raise TypeError
    upto_not_including_date = upto_date + datetime.timedelta(days=1)
    query = 'brtype(' + branch + ')&&created_since(' + since_date.strftime("%d-%b-%Y") + ')&&!created_since(' + upto_not_including_date.strftime("%d-%b-%Y") + ')'
    out = subprocess.check_output(["cleartool","find",path,"-version",query,"-exec","cleartool desc -fmt %d\\n \"%CLEARCASE_XPN%\""],shell=False,stderr=subprocess.PIPE)
    return filter(None, out.split('\r\n'))

# compute the checkins per interval, and return an dictionary of starttime->amount, ignoring empty intervals
def compute_trend_data(results,interval):
    trend_data = collections.defaultdict(int)
    for checkin_time in results:
        adjusted_time = checkin_time
        if interval==60*24:
            adjusted_time = datetime.datetime(checkin_time.year,checkin_time.month,checkin_time.day,0,0,0)  
        elif interval<=60:
            adjusted_time = datetime.datetime(checkin_time.year,checkin_time.month,checkin_time.day,checkin_time.hour,int(math.floor(checkin_time.minute/interval)*interval),0)  
        else:
            raise NotImplementedError
        trend_data[adjusted_time] += 1
    return trend_data

def perdelta(start, end, delta):
    # see http://stackoverflow.com/questions/10688006/generate-a-list-of-datetimes-between-an-interval-in-python
    curr = start
    while curr < end:
        yield curr
        curr += delta

def result_to_text(timestamp,count):
    line = str(timestamp)
    if count > 0:
        line = line + ' ' + HISTOGRAM_CHAR*count
    return line

def result_to_csv(timestamp,count):
    date_only = datetime.date(timestamp.year,timestamp.month,timestamp.day)
    time_only = datetime.time(timestamp.hour,timestamp.minute,timestamp.second)
    line = str(date_only) + ',' + str(time_only) + ',' + str(count)
    return line

def create_text_histogram(data_points,from_date,to_date,interval):
    lines = []
    for result in perdelta(from_date,to_date + datetime.timedelta(days=1),datetime.timedelta(minutes=interval)):
        if result in data_points.keys():
            lines.append(result_to_text(result,data_points[result]))
        else:
            lines.append(result_to_text(result,0))
    return lines

def create_csv_histogram(data_points,from_date,to_date,interval):
    lines = []
    for result in perdelta(from_date,to_date + datetime.timedelta(days=1),datetime.timedelta(minutes=interval)):
        if result in data_points.keys():
            lines.append(result_to_csv(result,data_points[result]))
        else:
            lines.append(result_to_csv(result,0))
    return lines

def main():
    parser = create_parser()
    args = parser.parse_args()
    validate_args(args)
    if not args.csv:
        print "Collecting ClearCase historical data, please wait..."
    now_date = datetime.datetime.now()
    now_date = now_date.replace(hour=0, minute=0, second=0, microsecond=0)
    from_date = get_date_before_some_date(now_date,args.days)
    to_date = now_date
    combined_checkin_times = []
    for p in args.path:
        cc_times = get_checkin_times(p,args.branch,from_date,to_date)
        checkin_times = [cctime_to_datetime(x) for x in cc_times]
        combined_checkin_times.extend(checkin_times)
    data_points = compute_trend_data(combined_checkin_times,args.interval)
    if len(data_points) > 0:
        if args.csv:
            print "date,time,count"
            lines = create_csv_histogram(data_points,from_date,to_date,args.interval)
            for line in lines:
                print line
        else:
            #print "Check-in Trend in branch \'" + args.branch + "\' for " + str(args.days) + " days under " + args.path + " at " + str(args.interval) + " minutes interval:\n"
            lines = create_text_histogram(data_points,from_date,to_date,args.interval)
            for line in lines:
                print line
            total_checkins = len(combined_checkin_times)
            max_checkins_in_interval = max(data_points.values())
            print "\nTotal " + str(total_checkins) + " check-ins, at most " + str(max_checkins_in_interval) + " check-ins per interval.\n"
    else:
        print "No check-ins found."

if __name__ == '__main__':
    main()
    