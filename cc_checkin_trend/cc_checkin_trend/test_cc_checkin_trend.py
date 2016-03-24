from unittest import TestCase
import cc_checkin_trend
import datetime
import re

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
    def test_all_args(self):
        args = self.parser.parse_args(['\\scm\\scripts', '-b', 'main', '-d', '7'])
        self.assertEqual(args.branch,'main')
        self.assertEqual(args.days,7)
        self.assertEqual(args.path,'\\scm\\scripts')
    def test_too_many_args(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(['\\scm\\scripts', '\\vob1\\mst\\c#', '-b', 'main', '-d', '7'])

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
        expected_list=["2015-12-03T16:00:55+02:00",
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
        
if __name__ == '__main__':
    unittest.main()
