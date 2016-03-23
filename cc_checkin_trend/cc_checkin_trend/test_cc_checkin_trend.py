from unittest import TestCase
from cc_checkin_trend import create_parser

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

if __name__ == '__main__':
    unittest.main()
