# Copyright (c) 2023, ESTC and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ePosMultiCurrencyReport(Document):
	pass

@frappe.whitelist()
def get_epos_report_as_tree():
	data = frappe.db.get_list('ePos Multi Currency Report' ,fields=['name', 'report','doctype','report_name','parent_doctype','is_group','parent_epos_multi_currency_report'])
	return data