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

class ClearCaseFindTestCases(TestCase):
    """
    Base TestCase class, sets up known to work 'cleartool find' data
    """
    @classmethod
    def setUpClass(cls):
        cls.path = "V:\\scm\\scripts"
        cls.branch = "v12.2"
        cls.since_date = datetime.date(2016,3,17)
    
class DataCollectorTestCases(ClearCaseFindTestCases):
    def test_days_ago_converted_to_date(self):
        ref_date = datetime.date(2016,3,24)
        for day in range(0,5):
            self.assertEqual(str(ref_date.day-day),cc_checkin_trend.get_date_before_some_date(ref_date,day).strftime("%d"))
    def test_checkin_list_has_correct_len(self):
        expected_len = 4
        times_list = cc_checkin_trend.get_checkin_times(self.path,self.branch,self.since_date)
        self.assertEqual(len(times_list),expected_len)
    def test_checkin_list_is_valid_timestamps(self):
        cc_timestamp_regex = "\d\d\d\d\-\d\d\-\d\dT\d\d\:\d\d\:\d\d"
        times_list = cc_checkin_trend.get_checkin_times(self.path,self.branch,self.since_date)
        for timestamp in times_list:
            self.assertTrue(re.match(cc_timestamp_regex,timestamp))
        
if __name__ == '__main__':
    unittest.main()
