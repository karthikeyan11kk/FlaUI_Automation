# Acturis Assistant automation (pywinauto + pytest)

The same flow as the Robot Framework version, in Python.

```
ActurisPywinauto/
├── acturis/
│   ├── locators.py        ← all locators (from FlaUInspect)
│   ├── flows.py           ← one function ("method") per Yes/No column + the Locate Quote steps
│   ├── app.py             ← launch, log in, UNDERWRITING tab, close
│   ├── ui.py              ← click / set_text / wait helpers on top of pywinauto
│   ├── config.py          ← app path, test data path, timeouts, reads credentials.env
│   └── excel_reader.py    ← reads the rows from .xls / .xlsx
├── testdata/
│   ├── credentials.env    ← user name and password
│   └── TestData.xls       ← test cases, sheet "Execution" (replace with your real file)
├── tests/
│   ├── conftest.py        ← log in once, tidy up after each test, screenshot on failure
│   └── test_execution.py  ← one test per Excel row (generated automatically)
├── tools/
│   └── print_controls.py  ← prints every control with ready-to-copy locator values
├── pytest.ini
├── run_tests.bat
└── requirements.txt
```

## Setup (once)

```
pip install -r requirements.txt
```

1. Put your user name and password in `testdata\credentials.env`. It also holds `ACTURIS_AUTH_CODE=TKCHER`, the code typed into Authorise Refer.
2. Copy your real `TestData.xls` into `testdata\` (sheet `Execution`), then save and close it.

## Run

Close Acturis, then double-click `run_tests.bat`, or:

```
python -m pytest
```

Run one test case only:

```
python -m pytest -k TC01_Execution_Premium
```

The report is in `results\report.html`, and screenshots are in `results\screenshots` (one after Open Quote, one for each failure).
Leave the mouse and keyboard alone while the tests run.

## How a run works

1. Acturis opens and logs in **once** (`acturis` fixture in `conftest.py`).
2. Each Excel row becomes a test named after its TestCaseName. **A new row is a new test**, with no code change.
3. **Execution is the on/off switch.** A row only runs when Execution = Yes.
4. Then, for every other column set to **Yes**, the matching function in `acturis/flows.py` runs, in column order:

| Excel | Runs |
|---|---|
| Quote = Yes **and** AuthorizeQuote = Yes | `locate_and_open_quote_by_insurer_quote_no` (UNDERWRITING tab → Locate Quote → Search On "Insurer Quote No." → type the number → Search → first result → Open Quote), then `authorize_quote` (scroll the Options pane to Authorise Refer → Authorisation Code → Save → Actions: Quote to Broker) |
| Quote = Yes only | `quote_steps` |
| Renewal Invite = Yes | `renewal_invite_steps` → `locate_and_open_policy` (UNDERWRITING tab → Locate Policy → Search On "Insurer Policy No." → type the **Policy Number** → Search → first result → Open Policy) |
| Policy, MTA, Cancellation, Renewal, Renewal Execution | `<column>_steps` (not automated yet) |

Result meanings:
- **SKIPPED: Execution is not Yes**: the row is switched off.
- **SKIPPED: ...no other column is Yes**: Execution is on, but nothing else is selected.
- **SKIPPED: Done: ... Not automated yet: X**: every automated step ran; X still needs its steps
  (replace `not_automated_yet(...)` in that function). A missing step doesn't stop the others.
- **FAILED**: a real problem. The message names the locator that wasn't found.

## From FlaUInspect to a pywinauto locator

```
FlaUInspect:   ListItem "UNDERWRITING" "[PolicyAdmin]"
                  |           |              |
               control_type  title        auto_id

locators.py:   {"auto_id": "[PolicyAdmin]", "control_type": "ListItem"}
```

Each locator is a list of steps from the main window down, for example
`LQ_PANE + [{"auto_id": "...", "control_type": "Edit"}]` means "the Edit inside the Locate Quote pane".

You can also get the values without FlaUInspect: open Acturis on the screen you need, then run

```
python tools/print_controls.py 8
```

and copy the `auto_id` and `control_type` from `results\controls.txt`.

## Robot Framework vs pywinauto

| Robot Framework (FlaUI) | pywinauto |
|---|---|
| `//Edit[@AutomationId='x']` | `{"auto_id": "x", "control_type": "Edit"}` |
| `[@Name='Search']` | `{"title": "Search"}` |
| `starts-with(@Name,'Acturis - UAT')` | `{"title_re": r"^Acturis - UAT"}` |
| `(//DataItem)[1]` | `{"control_type": "DataItem", "found_index": 0}` |
| `Click` | `ui.click(...)` (calls `click_input()`) |
| `Set Text To Textbox` | `ui.set_text(...)` (calls `set_edit_text()`) |
| `Select Combobox Item By Name` | `ui.select_combo_item(...)` (calls `select()`) |
| `Wait Until Keyword Succeeds ... Element Should Exist` | `ui.wait_for(...)` (calls `wait("exists")`) |
| Suite Setup / Suite Teardown | `acturis` fixture (scope="session") |
| Test Teardown | `logged_in` fixture |
| `Skip` | `pytest.skip(...)` |

## Console log and speed

While the tests run, the console shows every step and how long it took to find the element:

```
13:26:01  click   [PolicyAdmin]                                   0.2s
13:26:02  found   [SearchLocateQuote]                             0.4s
13:26:04  click   Open Quote                                      0.3s
```

A large number on one line shows which screen is slow to load or which locator is slow to match.

Elements are found with Windows UI Automation's own search (`FindFirst` with auto_id / title /
control_type conditions) instead of pywinauto's `child_window()`, which fetches every element of a
type and checks each one from Python. Exact `auto_id`, `title` and `control_type` keys are the
fastest; `title_re` and `found_index` have to look through every match, so use them only when needed.

Close FlaUInspect (or move it off Acturis) while the tests run: clicks are real mouse clicks and
land on whatever window is on top. The helpers bring Acturis to the front before each click.

## Check these locators first (marked VERIFY)

The Search button, the first result row and the Open Quote button are found by title / control_type
(they worked on your first run). If one fails, inspect it and switch to its auto_id.

The **Locate Policy** screen wasn't in the screenshots: its locators copy the Locate Quote pattern
(`[SearchLocatePolicy][MainSearchCriteria][SearchOn]`, an **Open Policy** button) and the Search On item
is assumed to be **Insurer Policy No.**. If that item is named differently, the error lists every option
in the drop-down: copy the right one into `SEARCH_ON_POLICY_NUMBER` in `locators.py`.

**Authorise Refer** only appears while the quote is in **Refer** status. If the quote has already been
authorised, the test fails with the window title (which shows the status) and the actions that are
available. Put a referred quote's number in Excel.

## Troubleshooting

- **Clicks do nothing**: if Acturis runs as administrator, run the terminal (or VS Code) as administrator too.
- **"Acturis is already open"**: close it first; the tests start it themselves.
- **"Not found within 30s: ..."**: the message shows the locator. Compare it with FlaUInspect.
