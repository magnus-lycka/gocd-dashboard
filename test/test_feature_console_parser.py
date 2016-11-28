import unittest
from unittest.mock import MagicMock

from gocddash.console_parsers import junit_report_parser

_junit_report = (True, """<table class="section-table" cellpadding="2" cellspacing="0" border="0" width="98%">
<div class="tests">
<p>Tests run:
                    <span class="tests_total_count">13</span>
                    , Failures:
                    <span class="tests_failed_count">1</span>
                    , Not run:
                    <span class="tests_ignored_count">0</span>
                    , Time:
                    <span class="tests_total_duration">.000</span>
                    seconds.
                </p>
</div>
<tr>
<td class="section-data">Failure</td><td class="section-data">FruitCompany123</td>
</tr>
<tr>
<td colspan="2"></td>
</tr>
<tr>
<td class="sectionheader" colspan="2">
                        Unit Test Failure and Error Details (1)
                    </td>
</tr>
<tr>
<td class="section-data">Test:</td><td class="section-data">FruitCompany123</td>
</tr>
<tr>
<td class="section-data">Type:</td><td class="section-data">Failure</td>
</tr>
<tr>""")


class TestConsoleFetcher(unittest.TestCase):
    def test_po_webtest(self):
        go_client = junit_report_parser.go_client

        class Stub:
            pass
        junit_report_parser.go_client = Stub
        junit_report_parser.go_client.request_junit_report = MagicMock(return_value=_junit_report)
        parser = junit_report_parser.JunitConsoleParser("test-interface", 1872, 1, "defaultStage", 'defaultJob')

        output_list = parser.parse_info()

        junit_report_parser.go_client = go_client
        error_list = [('Failure', 'FruitCompany123')]
        self.assertEqual(output_list, error_list)
