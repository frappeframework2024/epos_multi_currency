# Copyright (c) 2023, ESTC and contributors
# For license information, please see license.txt

import json
import frappe
from collections import Counter
from frappe.model.document import Document


class Expense(Document):
	def before_save(self):
		self.status = "Unpaid"


	def on_update(self):
		item_currencies = Counter()
		for v in self.expense_items:
			item_currencies[v.currency] += v.amount or 0
		
		payment_currency=[]
		for a in self.total_amount:
			payment_currency.append(a)

		frappe.db.sql("delete from `tabExpense Total Summary` where parent = '{}' ".format(self.name))

		for currency, grand_total in item_currencies.items():
			list_payment_currency = list([a for a in payment_currency if a.currency == currency])
			if len(list_payment_currency) > 0:
				b = list_payment_currency[0]
				if currency == b.currency:
					c = frappe.get_doc({"doctype":"Expense Total Summary", 
							"currency":currency,
							"total_amount":grand_total,
							"paid_amount":b.paid_amount or 0,
							"balance":grand_total - b.paid_amount or 0,
							"parent":self.name,
							"parentfield":"total_amount",
							"parenttype":"Expense"})
					c.insert()
			else:
				c = frappe.get_doc({"doctype":"Expense Total Summary", 
						"currency":currency,
						"total_amount":grand_total,
						"paid_amount":0,
						"balance":grand_total,
						"parent":self.name,
						"parentfield":"total_amount",
						"parenttype":"Expense"})
				c.insert()
				
		self.reload()

