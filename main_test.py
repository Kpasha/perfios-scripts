import main


def test_fix_transaction_json():
    source_json_paytm = [{u'Category': u'Cash Back', u'Remarks': None, u'Description': u'Cashback Received-Paytm for Order #1982274_cc67598-bigbasket', u'Credit': 5.03, u'Debit': None, u'Date': 42727.0, u'Balance': 57.48, u'Sr. No. ': 86.0}]
    expected_json_paytm = [{'category': u'Cash Back', '_type': u'paytm_transactions', 'balance': 57.48, 'date': '2016-12-23T00:00:00', '_index': 'perfios', 'credit': 5.03, 'serial_no': 86.0, 'debit': None, 'remarks': None, 'account': u'PayTM Transactions', 'description': u'Cashback Received-Paytm for Order #1982274_cc67598-bigbasket'}]
    assert expected_json_paytm == main.fix_transaction_json("PayTM Transactions", source_json_paytm)
