from unittest import TestCase
import cc_checkin_trend
import datetime
import re
import collections

# Inspired by http://dustinrcollins.com/testing-python-command-line-apps
class CommandLineTestCase(TestCase):
    """
    Base TestCase class, sets up a CLI parser
    """
    @classmethod
    def setUpClass(cls):
        parser = cc_checkin_trend.create_parser()
        cls.parser = parser

class ArgParserTestCases(CommandLineTestCase):
    def test_empty_args(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args([])
    def test_all_mandatory_args(self):
        args = self.parser.parse_args(['\\scm\\scripts', '-b', 'main', '-d', '7'])
        self.assertEqual(args.branch,'main')
        self.assertEqual(args.days,7)
        self.assertEqual(args.path,'\\scm\\scripts')
        self.assertEqual(args.interval,cc_checkin_trend.DEFAULT_INTERVAL)
    def test_optional_args(self):
        args = self.parser.parse_args(['\\scm\\scripts', '-b', 'main', '-d', '7', '-i', '99'])
        self.assertEqual(args.interval,99)
    def test_too_many_paths(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(['\\scm\\scripts', '\\vob1\\src', '-b', 'main', '-d', '7'])
    def test_missing_arg(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(['\\scm\\scripts', '-b', '-d', '7'])

class ArgValidatorTestCases(TestCase):
    def test_branch_existing_in_vob(self):
        vob_tag="vob1" # TODO use cleartool lsvob and pick an active one
        self.assertTrue(cc_checkin_trend.valid_branch('main',vob_tag))
    def test_branch_nonexisting_in_vob(self):
        vob_tag="vob1" # TODO use cleartool lsvob and pick an active one
        self.assertFalse(cc_checkin_trend.valid_branch('FHAFIFUILWQ',vob_tag))
    def test_branch_nonexisting_vob(self):
        vob_tag="uyrfaiofnmal"
        self.assertFalse(cc_checkin_trend.valid_branch('main',vob_tag))
    def test_existing_cc_path(self):
        vob_tag="vob1" # TODO use cleartool lsvob and pick an active one
        view_root="V:" # TODO use cleartool lsview and pick one
        self.assertTrue(cc_checkin_trend.valid_path(view_root + "\\" + vob_tag)) 
    def test_missing_path(self):
        vob_tag="vob1" # TODO use cleartool lsvob and pick an active one
        view_root="V:" # TODO use cleartool lsview and pick one
        self.assertFalse(cc_checkin_trend.valid_path(view_root + "\\" + vob_tag + "\\fpavmdkslreoila")) 
    def test_path_not_in_cc(self):
        self.assertFalse(cc_checkin_trend.valid_path("C:\\Windows"))
    def test_days_in_range(self):
        for day in range(cc_checkin_trend.MIN_DAYS,cc_checkin_trend.MAX_DAYS):
            self.assertTrue(cc_checkin_trend.valid_days(day))
    def test_days_out_of_range(self):
        self.assertFalse(cc_checkin_trend.valid_days(cc_checkin_trend.MIN_DAYS-1))
        self.assertFalse(cc_checkin_trend.valid_days(cc_checkin_trend.MAX_DAYS+1))
    #def test_vob_of_valid_path_in_snapshot(self):
    #    self.assertEqual(get_vob_of_path("V:\\vob1\\scripts","vob1"))
    #    self.assertEqual(get_vob_of_path("F:\\data\\views\\another_view_tag\\vob2\\somedir","vob2"))
    #def test_vob_of_vob_path_in_snapshot(self):
    #    self.assertEqual(get_vob_of_path("V:\\vob3","vob3"))
    #def test_vob_of_valid_path_in_dyn_view(self):
    #    self.assertEqual(get_vob_of_path("\\view\\some_view_tag\\vob4\\resources","vob4"))
    #    self.assertEqual(get_vob_of_path("M:\\some_view_tag\\vob5\\dir1\\dir2","vob5"))
    def test_interval_positive(self):
        interval = 1
        self.assertTrue(cc_checkin_trend.valid_interval(interval))
    def test_interval_non_positive(self):
        interval = 0
        self.assertFalse(cc_checkin_trend.valid_interval(interval))
        interval = -5
        self.assertFalse(cc_checkin_trend.valid_interval(interval))

class FormatConvertorTestCases(TestCase):
    def test_days_ago_converted_to_date(self):
        ref_date = datetime.date(2016,3,24)
        for day in range(0,5):
            self.assertEqual(str(ref_date.day-day),cc_checkin_trend.get_date_before_some_date(ref_date,day).strftime("%d"))
    def test_cctime_to_datetime(self):
        cc_date = "2016-03-18T11:20:24+02:00"
        expected_date = datetime.datetime(2016,3,18,11,20,24) # TODO: add timezone
        got_date = cc_checkin_trend.cctime_to_datetime(cc_date)
        self.assertEqual(got_date,expected_date)

class DataCollectorTestCases(TestCase):
    # TODO test that clearcase error lines are skipped
    # TODO test when one of the children paths contains spaces
    def test_checkin_list_1(self):
        path="V:\\scm\\scripts"
        branch="v12.2"
        since_date=datetime.date(2016,3,17)
        upto_date=datetime.date(2016,3,25)
        expected_list=["2016-03-18T11:20:24+02:00","2016-03-18T11:30:37+02:00","2016-03-20T09:16:04+02:00","2016-03-18T11:20:25+02:00"]
        times_list = cc_checkin_trend.get_checkin_times(path,branch,since_date,upto_date)
        self.assertEqual(times_list,expected_list)
    def test_checkin_list_2(self):
        path="V:\\scm\\scripts"
        branch="main"
        since_date=datetime.date(2016,3,17)
        upto_date=datetime.date(2016,3,25)
        expected_list=[]
        times_list = cc_checkin_trend.get_checkin_times(path,branch,since_date,upto_date)
        self.assertEqual(times_list,expected_list)
    def test_checkin_list_3(self):
        path="V:\\scm\\scripts"
        branch="main"
        since_date=datetime.date(2015,12,1)
        upto_date=datetime.date(2015,12,31)
        expected_list=[
            "2015-12-03T16:00:55+02:00",
            "2015-12-03T16:00:56+02:00",
            "2015-12-20T13:54:26+02:00",
            "2015-12-21T09:09:45+02:00",
            "2015-12-07T13:37:55+02:00",
            "2015-12-22T14:28:31+02:00",
            "2015-12-22T14:28:32+02:00",
            "2015-12-07T13:37:34+02:00",
            "2015-12-07T13:37:36+02:00"]
        times_list = cc_checkin_trend.get_checkin_times(path,branch,since_date,upto_date)
        self.assertEqual(times_list,expected_list)

class TrendComputationTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = [
            datetime.datetime(2015, 12,  3, 16,  0, 55), 
            datetime.datetime(2015, 12,  3, 16,  0, 56), 
            datetime.datetime(2015, 12, 20, 13, 54, 26), 
            datetime.datetime(2015, 12,  7, 13, 37, 55),
            datetime.datetime(2015, 12,  7, 13, 38, 34),
            datetime.datetime(2015, 12,  7,  9,  9,  9)
        ]

class TrendResultsTestCases(TrendComputationTestCase):
    def test_daily_trend(self):
        expected = collections.defaultdict(int)
        expected[datetime.datetime(2015,12, 3,0,0,0)] = 2
        expected[datetime.datetime(2015,12, 7,0,0,0)] = 3
        expected[datetime.datetime(2015,12,20,0,0,0)] = 1
        trend = cc_checkin_trend.compute_trend_data(self.results,24*60)
        self.assertEqual(trend,expected)
    def test_hourly_trend(self):
        expected = collections.defaultdict(int)
        expected[datetime.datetime(2015,12, 3,16,0,0)] = 2
        expected[datetime.datetime(2015,12, 7, 9,0,0)] = 1
        expected[datetime.datetime(2015,12, 7,13,0,0)] = 2
        expected[datetime.datetime(2015,12,20,13,0,0)] = 1
        trend = cc_checkin_trend.compute_trend_data(self.results,60)
        self.assertEqual(trend,expected)
    def test_five_minutes_trend(self):
        expected = collections.defaultdict(int)
        expected[datetime.datetime(2015,12, 3,16, 0,0)] = 2
        expected[datetime.datetime(2015,12, 7, 9, 5,0)] = 1
        expected[datetime.datetime(2015,12, 7,13,35,0)] = 2
        expected[datetime.datetime(2015,12,20,13,50,0)] = 1
        trend = cc_checkin_trend.compute_trend_data(self.results,5)
        self.assertEqual(trend,expected)
    def test_one_minute_trend(self):
        expected = collections.defaultdict(int)
        expected[datetime.datetime(2015,12, 3,16, 0,0)] = 2
        expected[datetime.datetime(2015,12, 7, 9, 9,0)] = 1
        expected[datetime.datetime(2015,12, 7,13,37,0)] = 1
        expected[datetime.datetime(2015,12, 7,13,38,0)] = 1
        expected[datetime.datetime(2015,12,20,13,54,0)] = 1
        trend = cc_checkin_trend.compute_trend_data(self.results,1)
        self.assertEqual(trend,expected)
 
class HistogramTestCases(TestCase):
    def test_positive_result_to_text(self):
        result_time = datetime.datetime(2015,12,3,16, 0,0)
        result_data = 2
        expected_line = "2015-12-03 16:00:00 " + cc_checkin_trend.HISTOGRAM_CHAR + cc_checkin_trend.HISTOGRAM_CHAR
        line = cc_checkin_trend.result_to_text(result_time,result_data)
        self.assertEqual(line,expected_line)
    def test_zero_result_to_text(self):
        result_time = datetime.datetime(2015,12,3,16, 0,0)
        result_data = 0
        expected_line = "2015-12-03 16:00:00"
        line = cc_checkin_trend.result_to_text(result_time,result_data)
        self.assertEqual(line,expected_line)
    def test_text_histogram_hourly(self):
        data_points = collections.defaultdict(int)
        data_points[datetime.datetime(2015,12,3,16, 0,0)] = 2
        data_points[datetime.datetime(2015,12,4, 9, 0,0)] = 1
        data_points[datetime.datetime(2015,12,4,13, 0,0)] = 3
        from_date = datetime.datetime(2015,12,3)
        to_date = datetime.datetime(2015,12,4)
        interval = 60
        lines = cc_checkin_trend.display_text_histogram(data_points,from_date,to_date,interval)
        # make sure there are enough lines
        self.assertEqual(len(lines),2*24)
        # verify each of the data points appear
        expected_line = cc_checkin_trend.result_to_text(datetime.datetime(2015,12,3,16, 0, 0),2)
        self.assertTrue(expected_line in lines)
        expected_line = cc_checkin_trend.result_to_text(datetime.datetime(2015,12,4, 9, 0, 0),1)
        self.assertTrue(expected_line in lines)
        expected_line = cc_checkin_trend.result_to_text(datetime.datetime(2015,12,4,13, 0, 0),3)
        self.assertTrue(expected_line in lines)
        
if __name__ == '__main__':
    unittest.main()
