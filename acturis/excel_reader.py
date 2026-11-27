"""Reads test case rows from an Excel workbook (.xls or .xlsx).

Row 1 of the sheet holds the column headers. Every value comes back as text:
- numbers lose a trailing .0 (12345.0 -> "12345")
- dates become dd/mm/yyyy
- yes / YES / No are tidied to "Yes" / "No", so the code can compare with "Yes"
- empty cells become ""
"""

import datetime
from pathlib import Path


def read_rows(file_path, sheet_name, key_column="TestCaseName"):
    """Returns every row that has a value in key_column, as a list of dicts keyed by header."""
    file_path = Path(file_path)
    if not file_path.is_file():
        raise FileNotFoundError(f"Test data file not found: {file_path}")

    extension = file_path.suffix.lower()
    if extension == ".xls":
        rows = _read_xls(file_path, sheet_name)
    elif extension in (".xlsx", ".xlsm"):
        rows = _read_xlsx(file_path, sheet_name)
    else:
        raise ValueError(f"Unsupported test data file type '{extension}'. Use .xls or .xlsx.")

    if not rows:
        raise ValueError(f"Sheet '{sheet_name}' in {file_path} is empty.")
    headers = rows[0]
    if key_column not in headers:
        raise ValueError(
            f"Column '{key_column}' not found in sheet '{sheet_name}'. "
            f"Columns: {', '.join(h for h in headers if h)}"
        )
    key_index = headers.index(key_column)

    result = []
    for row in rows[1:]:
        if key_index < len(row) and row[key_index]:
            result.append({
                header: (row[i] if i < len(row) else "")
                for i, header in enumerate(headers)
                if header
            })
    return result


def _read_xls(file_path, sheet_name):
    import xlrd

    book = xlrd.open_workbook(str(file_path))
    if sheet_name not in book.sheet_names():
        raise ValueError(
            f"Sheet '{sheet_name}' not found in {file_path}. "
            f"Available sheets: {', '.join(book.sheet_names())}"
        )
    sheet = book.sheet_by_name(sheet_name)

    def cell_text(cell):
        if cell.ctype == xlrd.XL_CELL_DATE:
            return _to_text(xlrd.xldate.xldate_as_datetime(cell.value, book.datemode))
        if cell.ctype == xlrd.XL_CELL_BOOLEAN:
            return _to_text(bool(cell.value))
        return _to_text(cell.value)

    return [[cell_text(cell) for cell in sheet.row(r)] for r in range(sheet.nrows)]


def _read_xlsx(file_path, sheet_name):
    from openpyxl import load_workbook

    workbook = load_workbook(file_path, read_only=True, data_only=True)
    try:
        if sheet_name not in workbook.sheetnames:
            raise ValueError(
                f"Sheet '{sheet_name}' not found in {file_path}. "
                f"Available sheets: {', '.join(workbook.sheetnames)}"
            )
        return [
            [_to_text(value) for value in row]
            for row in workbook[sheet_name].iter_rows(values_only=True)
        ]
    finally:
        workbook.close()


def _to_text(value):
    if value is None:
        return ""
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.strftime("%d/%m/%Y")
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    text = str(value).strip()
    if text.lower() == "yes":
        return "Yes"
    if text.lower() == "no":
        return "No"
    return text
