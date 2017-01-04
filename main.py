import xlrd
import json
import xls_utils
import StringIO
import datetime

from dateutil.parser import parse as parse_date
from elasticsearch import Elasticsearch,helpers


def get_sheet_names(xls_file):
    with open(xls_file) as f:
        workbook = xlrd.open_workbook(file_contents=f.read())
    return workbook.sheet_names()

def fix_transaction_json(sheet, json):
    date_reference = parse_date("Sat 30 Dec 1899")
    for doc in json:
        doc['_index'] = "perfios"
        doc['_type'] = sheet.lower().replace(" ", "_")

        if sheet.endswith("bank"):
            doc['type'] = "bank"
        if sheet.endswith("cc"):
            doc['type'] = "cc"

        doc["serial_no"] = doc["Sr. No. "]
        doc.pop("Sr. No. ")

        if "Cheque No." in doc:
            doc["cheque_no"] = doc["Cheque No."]
            doc.pop("Cheque No.")

        doc["category"] = doc["Category"]
        doc.pop("Category")

        if "Payment" in doc:
            doc["credit"] = doc["Payment"]
            doc.pop("Payment")
        if "Charge" in doc:
            doc["debit"] = doc["Charge"]
            doc.pop("Charge")
        if "Credit" in doc:
            doc["credit"] = doc["Credit"]
            doc.pop("Credit")
        if "Debit" in doc:
            doc["debit"] = doc["Debit"]
            doc.pop("Debit")

        doc["remarks"] = doc["Remarks"]
        doc.pop("Remarks")

        if "Balance" in doc:
            doc["balance"] = doc["Balance"]
            doc.pop("Balance")

        doc["description"] = doc["Description"]
        doc.pop("Description")

        doc["account"] = sheet

        days_diff = doc["Date"]
        doc["date"] = (date_reference + datetime.timedelta(days=days_diff)).isoformat()
        doc.pop("Date")

    return json

def read_all_sheets(xls_file):
    all_transactions = []
    for sheet in get_sheet_names(xls_file):
        if not (sheet.endswith("bank") or sheet.endswith("cc") or sheet.endswith("Transactions")):
            continue

        output = StringIO.StringIO()
        xls_utils.from_xls(xls_file, sheet=sheet, skip_rows=2).to_json(output)
        transaction_json = json.loads(output.getvalue())
        transaction_json = fix_transaction_json(sheet, transaction_json)
        all_transactions += transaction_json

    return all_transactions


if __name__ == '__main__':
    es = Elasticsearch()

    all_transactions = read_all_sheets("expenses.xls")
    helpers.bulk(es, all_transactions)
