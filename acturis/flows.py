"""One function ("method") per Yes/No column of the test data sheet.

run_test_case() looks at the test's Excel row. A row only runs when Execution = Yes;
then the function for every other column set to Yes is called, in column order.
Inside any function, read a column with row["Column Name"], e.g. row["Policy Number"].

A step that isn't automated yet doesn't stop the others: they still run, and at the
end the test is marked SKIPPED with the list of steps still to automate.
"""

import pytest

from acturis import app, config, locators, ui


class NotAutomatedYet(Exception):
    """Raised by a step whose clicks haven't been written yet."""


def not_automated_yet(step):
    raise NotAutomatedYet(step)


# ==========================================================================
# Decides what to run from the Excel row
# ==========================================================================
def run_test_case(row):
    name = row["TestCaseName"]

    # Execution is the on/off switch for the whole row
    if not is_yes(row, "Execution"):
        pytest.skip(f"Execution is not Yes for {name}, so it isn't run.")
    if not [column for column, value in row.items() if value == "Yes" and column != "Execution"]:
        pytest.skip(f"Execution is Yes for {name} but no other column is Yes, so there is nothing to run.")

    done, pending = [], []

    def run(step, function):
        try:
            function(row)
            done.append(step)
        except NotAutomatedYet:
            pending.append(step)

    if is_yes(row, "Quote") and is_yes(row, "AuthorizeQuote"):
        run("Quote + AuthorizeQuote", quote_and_authorize)
    elif is_yes(row, "Quote"):
        run("Quote", quote_steps)
    elif is_yes(row, "AuthorizeQuote"):
        pytest.fail(
            f"AuthorizeQuote is Yes but Quote is No for {name}. "
            "Set Quote to Yes to locate and authorize the quote.",
            pytrace=False,
        )

    # The other columns, in the same order as the sheet
    for column, function in [
        ("Policy", policy_steps),
        ("MTA", mta_steps),
        ("Cancellation", cancellation_steps),
        ("Renewal Invite", renewal_invite_steps),
        ("Renewal", renewal_steps),
        ("Renewal Execution", renewal_execution_steps),
    ]:
        if is_yes(row, column):
            run(column, function)

    if pending:
        pytest.skip(
            f"Done: {', '.join(done) or 'nothing'}. "
            f"Not automated yet: {', '.join(pending)} (add their steps in acturis/flows.py)."
        )


def is_yes(row, column):
    if column not in row:
        raise AssertionError(
            f"Column '{column}' not found in the test data sheet. Columns: {', '.join(row)}"
        )
    return row[column] == "Yes"


def require_value(row, column):
    """The column's value, failing clearly if it's empty or NA."""
    value = row.get(column, "")
    if not value or value.upper() == "NA":
        pytest.fail(
            f"{column} is {'empty' if not value else 'NA'} for {row['TestCaseName']} "
            "in the test data sheet. Enter the real value.",
            pytrace=False,
        )
    return value


# ==========================================================================
# Quote (Quote = Yes and AuthorizeQuote = Yes)
# ==========================================================================
def quote_and_authorize(row):
    locate_and_open_quote_by_insurer_quote_no(row)
    authorize_quote(row)


def locate_and_open_quote_by_insurer_quote_no(row):
    insurer_quote_no = require_value(row, "Insurer QuoteNumber")
    name = row["TestCaseName"]

    # 1. UNDERWRITING tab > Locate Quote
    app.open_underwriting_tab()
    ui.click(locators.NAV_LOCATE_QUOTE)
    ui.wait_for(locators.LQ_CMB_SEARCH_ON)

    # 2. Search On: Insurer Quote No.
    ui.select_combo_item(locators.LQ_CMB_SEARCH_ON, locators.SEARCH_ON_INSURER_QUOTE_NO)

    # 3. Type the Insurer Quote No. from Excel and search
    ui.set_text(locators.LQ_TXT_SEARCH_VALUE, insurer_quote_no)
    ui.click(locators.LQ_BTN_SEARCH)

    # 4. Select the first result and open it
    ui.click(locators.LQ_FIRST_RESULT)
    ui.click(locators.LQ_BTN_OPEN_QUOTE)
    ui.screenshot(f"{name}_quote_opened")


def authorize_quote(row):
    """Scroll to Authorise Refer, then enter the code, save, and Quote to Broker."""
    name = row["TestCaseName"]
    code = config.get_authorisation_code()

    # 1. Wait for the quote's Actions list, scroll to Authorise Refer, then click it.
    #    It's only there while the quote is in Refer status, so say clearly if it's missing.
    ui.wait_for(locators.QUOTE_ACTIONS_LIST)
    ui.scroll_into_view(locators.QUOTE_ACT_AUTHORISE_REFER)
    ui.click(locators.QUOTE_ACT_AUTHORISE_REFER)
    ui.wait_for(locators.AR_PANE)

    # 2. Type the authorisation code and Save
    ui.set_text(locators.AR_TXT_AUTH_CODE, code, secret=True)
    ui.click(locators.AR_BTN_SAVE)

    # The pop-up closes once the code is accepted
    try:
        ui.wait_until_gone(locators.AR_PANE)
    except AssertionError:
        raise AssertionError(
            f"The Authorise Refer pop-up is still open after Save for {name}. "
            "Check ACTURIS_AUTH_CODE in credentials.env and any message on the pop-up."
        ) from None
    ui.screenshot(f"{name}_authorised")

    # 3. Actions list > Quote to Broker
    ui.click(locators.QUOTE_ACT_QUOTE_TO_BROKER)
    # TODO: if Quote to Broker opens a pop-up, add its locators and the Save / OK click here.
    ui.screenshot(f"{name}_quoted_to_broker")
    ui.click(locators.QUOTE_TO_BROKER_BTN_NEXT)
    ui.click(locators.QUOTE_TO_BROKER_RATING_NOTES_BTN_NEXT)
    ui.click(locators.QUOTE_TO_BROKER_REPORT_QUESTIONS_BTN_NEXT)
    ui.click(locators.QUOTE_TO_BROKER_MESSAGE_TO_BROKER_BTN_SUBMIT)
    ui.wait_for(locators.QUOTE_TO_BROKER_OPEN_QUOTE)
    ui.click(locators.QUOTE_TO_BROKER_OPEN_QUOTE)
    ui.screenshot(f"{name}_quoted_to_broker_Successfully")

def quote_steps(row):
    # Runs when Quote = Yes and AuthorizeQuote = No.
    not_automated_yet("Quote")


# ==========================================================================
# Policy: shared by Renewal Invite, and later MTA / Cancellation / Renewal
# ==========================================================================
def locate_and_open_policy(row):
    """UNDERWRITING tab -> Locate Policy -> search the Policy Number from Excel -> open it."""
    policy_number = require_value(row, "Policy Number")
    name = row["TestCaseName"]

    # 1. UNDERWRITING tab > Locate Policy
    app.open_underwriting_tab()
    ui.click(locators.NAV_LOCATE_POLICY)
    ui.wait_for(locators.LP_CMB_SEARCH_ON)

    # 2. Search On: the policy number option (see SEARCH_ON_POLICY_NUMBER in locators.py)
    ui.select_combo_item(locators.LP_CMB_SEARCH_ON, locators.SEARCH_ON_POLICY_NUMBER)

    # 3. Type the Policy Number from Excel and search
    ui.set_text(locators.LP_TXT_SEARCH_VALUE, policy_number)
    ui.click(locators.LP_BTN_SEARCH)

    # 4. Select the first result and open it
    ui.click(locators.LP_FIRST_RESULT)
    ui.click(locators.LP_BTN_OPEN_POLICY)
    ui.screenshot(f"{name}_policy_opened")


def renewal_invite_steps(row):
    """Renewal Invite = Yes: open the policy from the Policy Number column."""
    locate_and_open_policy(row)
    # TODO: the renewal invite actions on the open policy go here.
    ui.scroll_into_view(locators.PROCESS_RENEWAL_INVITE)
    ui.click(locators.PROCESS_RENEWAL_INVITE)
    ui.click(locators.PROCESS_RENEWAL_INVITE_BTN_CONTINUE)
    ui.screenshot(f"{row['TestCaseName']}_process_renewal_initiated")
    ui.click(locators.PROCESS_RENEWAL_INVITE_BTN_SAVE)
    ui.screenshot(f"{row['TestCaseName']}_process_renewal_completed")
    ui.click(locators.RENEWAL_INVITE_RESUBMIT)
    ui.screenshot(f"{row['TestCaseName']}_Renewal_invite_is_Obtained")
    ui.click(locators.RENEWAL_INVITE_QUOTE_TO_BROKER_BTN_NEXT)
    ui.click(locators.RENEWAL_INVITE_QUOTE_TO_BROKER_RATING_NOTES_BTN_NEXT)
    ui.click(locators.RENEWAL_INVITE_QUOTE_TO_BROKER_REPORT_QUESTIONS_BTN_NEXT)
    ui.click(locators.RENEWAL_INVITE_QUOTE_TO_BROKER_MESSAGE_TO_BROKER_BTN_SUBMIT)
    ui.click(locators.RENEWAL_INVITE_QUOTE_TO_BROKER_OPEN_QUOTE)
    ui.screenshot(f"{row['TestCaseName']}_Renewal_invite_is_Quoted_to_broker")


# ==========================================================================
# Other columns: replace not_automated_yet(...) with the real steps
# ==========================================================================
def policy_steps(row):
    not_automated_yet("Policy")


def mta_steps(row):
    # Start with locate_and_open_policy(row) when you write this
    not_automated_yet("MTA")


def cancellation_steps(row):
    # Start with locate_and_open_policy(row) when you write this
    not_automated_yet("Cancellation")


def renewal_steps(row):
    not_automated_yet("Renewal")


def renewal_execution_steps(row):
    # Script to use: row["Renewal Execution Script"]
    not_automated_yet("Renewal Execution")
