from unittest import TestCase
from cc_checkin_trend import create_parser, MAX_DAYS, MIN_DAYS, valid_branch, valid_days, valid_path, get_vob_of_path

# Inspired by http://dustinrcollins.com/testing-python-command-line-apps
class CommandLineTestCase(TestCase):
    """
    Base TestCase class, sets up a CLI parser
    """
    @classmethod
    def setUpClass(cls):
        parser = create_parser()
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
        self.assertTrue(valid_branch('main',vob_tag))
    def test_branch_nonexisting_in_vob(self):
        vob_tag="vob1" # TODO use cleartool lsvob and pick an active one
        self.assertFalse(valid_branch('FHAFIFUILWQ',vob_tag))
    def test_branch_nonexisting_vob(self):
        vob_tag="uyrfaiofnmal"
        self.assertFalse(valid_branch('main',vob_tag))
    def test_existing_cc_path(self):
        vob_tag="vob1" # TODO use cleartool lsvob and pick an active one
        view_root="V:" # TODO use cleartool lsview and pick one
        self.assertTrue(valid_path(view_root + "\\" + vob_tag)) 
    def test_missing_path(self):
        vob_tag="vob1" # TODO use cleartool lsvob and pick an active one
        view_root="V:" # TODO use cleartool lsview and pick one
        self.assertFalse(valid_path(view_root + "\\" + vob_tag + "\\fpavmdkslreoila")) 
    #def test_path_not_in_cc(self):
    #    self.assertFalse(valid_path("C:\\Windows"))
    def test_days_in_range(self):
        self.assertTrue(valid_days(MIN_DAYS))
        self.assertTrue(valid_days(MAX_DAYS))
        self.assertTrue(valid_days((MIN_DAYS + MAX_DAYS) / 2))
    def test_days_out_of_range(self):
        self.assertFalse(valid_days(MIN_DAYS-1))
        self.assertFalse(valid_days(MAX_DAYS+1))
    #def test_vob_of_valid_path_in_snapshot(self):
    #    self.assertEqual(get_vob_of_path("V:\\vob1\\scripts","vob1"))
    #    self.assertEqual(get_vob_of_path("F:\\data\\views\\another_view_tag\\vob2\\somedir","vob2"))
    #def test_vob_of_vob_path_in_snapshot(self):
    #    self.assertEqual(get_vob_of_path("V:\\vob3","vob3"))
    #def test_vob_of_valid_path_in_dyn_view(self):
    #    self.assertEqual(get_vob_of_path("\\view\\some_view_tag\\vob4\\resources","vob4"))
    #    self.assertEqual(get_vob_of_path("M:\\some_view_tag\\vob5\\dir1\\dir2","vob5"))
        
if __name__ == '__main__':
    unittest.main()
