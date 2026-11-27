"""All locators for Acturis Assistant, in one place (taken from FlaUInspect).

How a FlaUInspect tree line becomes a pywinauto locator:

    Edit "User Name" "[LoginScreen][LogontoActuris][UserName]"
     |       |                     |
     |       |                     +-- auto_id       (best: doesn't change)
     |       +------------------------ title         (the Name; can change with language)
     +-------------------------------- control_type

    -> {"auto_id": "[LoginScreen][LogontoActuris][UserName]", "control_type": "Edit"}

Each locator is a PATH: a list of steps from the main window down to the element.
Each step searches anywhere below the previous one (like // in an XPath), so
LOGIN_PANE + [...] means "inside the login pane, find ...".

Keys you can use in a step: auto_id, title, control_type, class_name (exact matches, fastest),
title_re (a regular expression on the Name) and found_index (0 = first match, 1 = second...).

tools/print_controls.py prints every control as child_window(title=..., auto_id=...,
control_type=...): copy those three values into a dict here.

Lines marked VERIFY are educated guesses: check them in FlaUInspect before the first run.
"""

# ==========================================================================
# Main window
# The title is "Acturis - UAT" on the login screen and grows after login,
# e.g. "Acturis - UAT - <user> - [Locate Task]". The regex ^ means "starts with".
# Change "Acturis - UAT" for other environments.
# ==========================================================================
MAIN_WINDOW = {"title_re": r"^Acturis - UAT", "control_type": "Window"}


# ==========================================================================
# Login screen
# ==========================================================================
LOGIN_PANE = [{"auto_id": "[LoginScreen]", "control_type": "Pane"}]
LOGIN_TXT_USERNAME = LOGIN_PANE + [{"auto_id": "[LoginScreen][LogontoActuris][UserName]", "control_type": "Edit"}]
LOGIN_TXT_PASSWORD = LOGIN_PANE + [{"auto_id": "[LoginScreen][LogontoActuris][Password]", "control_type": "Edit"}]
LOGIN_BTN_LOGIN = LOGIN_PANE + [{"auto_id": "[LoginScreen][LogontoActuris][Logon]", "control_type": "Button"}]  # "Log On"
LOGIN_RB_LOGON = LOGIN_PANE + [{"auto_id": "[LoginScreen][RadioButtons][LogontoActuris]", "control_type": "RadioButton"}]


# ==========================================================================
# Module tabs along the top (shown after login)
# The UNDERWRITING tab's auto_id is [PolicyAdmin].
# ==========================================================================
TABS_LIST = [{"auto_id": "[ModuleTabsObject]", "control_type": "List"}]
TAB_HOME = TABS_LIST + [{"auto_id": "[Home]", "control_type": "ListItem"}]
TAB_TASK_MANAGEMENT = TABS_LIST + [{"auto_id": "[TaskManagement]", "control_type": "ListItem"}]
TAB_UNDERWRITING = TABS_LIST + [{"auto_id": "[PolicyAdmin]", "control_type": "ListItem"}]
TAB_RENEWALS = TABS_LIST + [{"auto_id": "[Renewals]", "control_type": "ListItem"}]
TAB_BATCH_DOCUMENTS = TABS_LIST + [{"auto_id": "[BatchDocumentsModule]", "control_type": "ListItem"}]
TAB_AUTOMATION = TABS_LIST + [{"auto_id": "[Automation]", "control_type": "ListItem"}]
TAB_REPORTING = TABS_LIST + [{"auto_id": "[Reporting]", "control_type": "ListItem"}]
TAB_CONFIGURATION = TABS_LIST + [{"auto_id": "[Config]", "control_type": "ListItem"}]
BTN_LOG_OUT = [{"auto_id": "[LogoutObject]", "control_type": "SplitButton"}]


# ==========================================================================
# UNDERWRITING > left "Options" pane > "Search" list
# The "Locate Quote" list item and the Locate Quote screen share the auto_id
# [SearchLocateQuote], so control_type (ListItem vs Pane) tells them apart.
# ==========================================================================
NAV_SEARCH_LIST = [{"auto_id": "[ContactsSearchFrame]", "control_type": "List"}]
NAV_LOCATE_CONTACT = NAV_SEARCH_LIST + [{"auto_id": "[SearchLocateContact]", "control_type": "ListItem"}]
NAV_LOCATE_RFQ = NAV_SEARCH_LIST + [{"auto_id": "[SearchLocateRFQ]", "control_type": "ListItem"}]
NAV_LOCATE_QUOTE = NAV_SEARCH_LIST + [{"auto_id": "[SearchLocateQuote]", "control_type": "ListItem"}]
NAV_LOCATE_POLICY = NAV_SEARCH_LIST + [{"auto_id": "[SearchLocatePolicy]", "control_type": "ListItem"}]
NAV_LOCATE_CLAIM = NAV_SEARCH_LIST + [{"auto_id": "[SearchLocateClaim]", "control_type": "ListItem"}]


# ==========================================================================
# Locate Quote screen
# ==========================================================================
LQ_PANE = [{"auto_id": "[SearchLocateQuote]", "control_type": "Pane"}]
LQ_CMB_SEARCH_ON = LQ_PANE + [{"auto_id": "[SearchLocateQuote][MainSearchCriteria][SearchOn]", "control_type": "ComboBox"}]
# The search box's Name follows the "Search On" choice (e.g. "Quote Ref."), so use its auto_id
LQ_TXT_SEARCH_VALUE = LQ_PANE + [{"auto_id": "[SearchLocateQuote][MainSearchCriteria][SearchOnValue]", "control_type": "Edit"}]
LQ_BTN_CANCEL = LQ_PANE + [{"auto_id": "[SearchLocateQuote][LocateQuoteBar][CancelScreen]", "control_type": "Button"}]

# VERIFY: these three weren't in your screenshots, so they are found by title or control_type.
# found_index=0 takes the first match. Replace them with the auto_ids FlaUInspect shows.
LQ_BTN_SEARCH = LQ_PANE + [{"title": "Search", "control_type": "Button", "found_index": 0}]
LQ_FIRST_RESULT = LQ_PANE + [{"control_type": "DataItem", "found_index": 0}]
LQ_BTN_OPEN_QUOTE = LQ_PANE + [{"title": "Open Quote", "control_type": "Button", "found_index": 0}]

# Items in the "Search On" drop-down. Their Names end with a full stop.
SEARCH_ON_INSURER_QUOTE_NO = "Insurer Quote No."
SEARCH_ON_QUOTE_REF = "Quote Ref."
SEARCH_ON_INSURER_POLICY_NO = "Insurer Policy No."


# ==========================================================================
# Locate Policy screen
# VERIFY: this screen wasn't in your screenshots. The auto_ids follow the same pattern as
# Locate Quote ([SearchLocateQuote]... -> [SearchLocatePolicy]...). If one fails, check it in
# FlaUInspect on the Locate Policy screen and correct it here.
# ==========================================================================
LP_PANE = [{"auto_id": "[SearchLocatePolicy]", "control_type": "Pane"}]
LP_CMB_SEARCH_ON = LP_PANE + [{"auto_id": "[SearchLocatePolicy][MainSearchCriteria][SearchOn]", "control_type": "ComboBox"}]
LP_TXT_SEARCH_VALUE = LP_PANE + [{"auto_id": "[SearchLocatePolicy][MainSearchCriteria][SearchOnValue]", "control_type": "Edit"}]
LP_BTN_CANCEL = LP_PANE + [{"title": "Cancel", "control_type": "Button"}]
LP_BTN_SEARCH = LP_PANE + [{"title": "Search", "control_type": "Button"}]
LP_FIRST_RESULT = LP_PANE + [{"control_type": "DataItem"}]
LP_BTN_OPEN_POLICY = LP_PANE + [{"title": "Open Policy", "control_type": "Button"}]

# VERIFY: the "Search On" item for the Policy Number column (e.g. RICA0004048).
# If it's called something else, the error lists every option in the drop-down.
SEARCH_ON_POLICY_NUMBER = "Insurer Policy No."


# ==========================================================================
# Quote screen (after Open Quote) > left "Options" pane > "Actions" list
# ==========================================================================
QUOTE_ACTIONS_LIST = [{"auto_id": "[QuoteActionsFrame]", "control_type": "List"}]
# "Authorise Refer" only shows while the quote is in Refer status. It's found by the text shown
# on screen, anywhere in the window, so it works whichever list it sits in.
QUOTE_ACT_AUTHORISE_REFER = [{"title": "Authorise Refer", "control_type": "ListItem"}]
QUOTE_ACT_QUOTE_TO_BROKER = QUOTE_ACTIONS_LIST + [{"auto_id": "[LaunchQuoteToAgent]", "control_type": "ListItem"}]
QUOTE_ACT_REFER_TO_BROKER = QUOTE_ACTIONS_LIST + [{"auto_id": "[LaunchReferToAgent]", "control_type": "ListItem"}]
QUOTE_ACT_DECLINE_TO_BROKER = QUOTE_ACTIONS_LIST + [{"auto_id": "[SubmitToAgentDeclineNoRender]", "control_type": "ListItem"}]
QUOTE_ACT_REJECT = QUOTE_ACTIONS_LIST + [{"auto_id": "[RejectQuote]", "control_type": "ListItem"}]
QUOTE_ACT_SUBMIT = QUOTE_ACTIONS_LIST + [{"auto_id": "[ResubmitQuote]", "control_type": "ListItem"}]
QUOTE_ACT_SET_TO_MANUAL = QUOTE_ACTIONS_LIST + [{"auto_id": "[SetToManualQuote]", "control_type": "ListItem"}]
QUOTE_ACT_CLONE_QUOTE = QUOTE_ACTIONS_LIST + [{"auto_id": "[QuoteCopyToQuote]", "control_type": "ListItem"}]


# ==========================================================================
# Pop-up window (Authorise Refer and other actions open inside it)
# ==========================================================================
POPUP_WINDOW = [{"auto_id": "[ChildWindowPopup]", "control_type": "Window"}]
POPUP_BTN_CLOSE = POPUP_WINDOW + [{"auto_id": "[Close]", "control_type": "Button"}]

# Authorise Refer pop-up
AR_PANE = POPUP_WINDOW + [{"auto_id": "[AuthoriseReferQuotePopUp]", "control_type": "Pane"}]
# Its auto_id was cut off in the screenshot, so it's found by its Name (a masked field: IsPassword = True)
AR_TXT_AUTH_CODE = AR_PANE + [{"title": "Authorisation Code", "control_type": "Edit"}]
AR_BTN_SAVE = AR_PANE + [{"auto_id": "[AuthoriseReferQuotePopUp][AuthoriseReferButtonBar][Save]", "control_type": "Button"}]
AR_BTN_CANCEL = AR_PANE + [{"auto_id": "[AuthoriseReferQuotePopUp][AuthoriseReferButtonBar][Cancel]", "control_type": "Button"}]


# Quote to Broker Pane buttons
QUOTE_TO_BROKER_BTN_NEXT = [{"auto_id": "[QuoteToAgentProcessQuoteToAgent][QuoteToAgentButtonBar][Next]", "control_type": "Button"}]
QUOTE_TO_BROKER_RATING_NOTES_BTN_NEXT = [{"auto_id": "[QuoteRatingNotesSummary][RatingNotesBar][Next]", "control_type": "Button"}]
QUOTE_TO_BROKER_REPORT_QUESTIONS_BTN_NEXT = [{"auto_id": "[QuoteToAgentProcessReportQuestions][ReportQuestionsBar][Next]", "control_type": "Button"}]
QUOTE_TO_BROKER_MESSAGE_TO_BROKER_BTN_SUBMIT = [{"auto_id": "[QuoteToAgentProcessMessageToAgent][MessageToAgentButtonBar][SubmitToAgent]", "control_type": "Button"}]

OPEN_QUOTE_POPUP=[{"auto_id": "[QuoteToAgentWizardFinishBeforeSavePopUp]", "control_type": "Pane"}]
QUOTE_TO_BROKER_OPEN_QUOTE=OPEN_QUOTE_POPUP + [{"auto_id": "[QuoteToAgentProcessQuoteToAgent][QuoteToAgentButtonBar][OpenQuote]", "control_type": "Button"}]


# ==========================================================================
# Quote screen (after Open Quote) > left "Options" pane > "Actions" list
# ==========================================================================

PROCESS_RENEWAL_INVITE = [{"auto_id": "[PolicyBandProcessRenewal]", "control_type": "ListItem"}]
PROCESS_RENEWAL_INVITE_BTN_CONTINUE = [{"auto_id": "Continue", "control_type": "Button"}]
PROCESS_RENEWAL_INVITE_BTN_SAVE = [{"auto_id": "[ProcessRenewalPopUp][ProcessRenewalBar][Save]", "control_type": "Button"}]
RENEWAL_INVITE_RESUBMIT = [{"auto_id": "[RenewalResubmit]", "control_type": "ListItem"}]
RENEWAL_INVITE_QUOTE_TO_BROKER = [{"auto_id": "[LaunchQuoteToAgentPolicy]", "control_type": "ListItem"}]


RENEWAL_INVITE_QUOTE_TO_BROKER_BTN_NEXT = [{"auto_id": "[QuoteToAgentPolicyProcessQuoteToAgent][QuoteToAgentButtonBar][Next]", "control_type": "Button"}]
RENEWAL_INVITE_QUOTE_TO_BROKER_RATING_NOTES_BTN_NEXT = [{"auto_id": "[PolicyBandRatingNotesSummary][RatingNotesBar][Next]", "control_type": "Button"}]
RENEWAL_INVITE_QUOTE_TO_BROKER_REPORT_QUESTIONS_BTN_NEXT = [{"auto_id": "[QuoteToAgentPolicyProcessReportQuestions][ReportQuestionsBar][Next]", "control_type": "Button"}]
RENEWAL_INVITE_QUOTE_TO_BROKER_MESSAGE_TO_BROKER_BTN_SUBMIT = [{"auto_id": "[QuoteToAgentRenewalProcessMessageToAgent][MessageToAgentButtonBar][SubmitToAgent]", "control_type": "Button"}]
RENEWAL_INVITE_QUOTE_TO_BROKER_OPEN_QUOTE=[{"auto_id": "[QuoteToAgentWizardFinishBeforeSavePopUp][UNButtonBar][OpenQuote]", "control_type": "Button"}]


