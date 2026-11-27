"""One test per row of testdata/TestData.xls, sheet "Execution".

The rows are read when pytest starts, so adding a row in Excel adds a test
(no code change). Each test is named after its TestCaseName, e.g.
test_execution[TC01_Execution_Premium].
"""

import pytest

from acturis import config, flows
from acturis.excel_reader import read_rows

ROWS = read_rows(config.TESTDATA_FILE, config.TESTDATA_SHEET)


@pytest.mark.parametrize("row", ROWS, ids=[row["TestCaseName"] for row in ROWS])
def test_execution(row, logged_in):
    flows.run_test_case(row)
