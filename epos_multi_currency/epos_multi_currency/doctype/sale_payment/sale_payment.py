# Copyright (c) 2023, ESTC and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class SalePayment(Document):
	def validate(self):
		for payment in self.payments:
			if payment.balance > 0:
				frappe.throw(_("Payment amount cannot greater than grand total."))


	def on_submit(self):
		for a in self.payments:
			c = frappe.db.sql("""
					 update `tabSales Invoice Payment` 
					 set paid_amount = paid_amount + {},
					 balance = paid_amount - grand_total
					 where parent = '{}' and currency='{}'""".
					 format(a.payment_amount,self.sale_invoice,a.currency))
			frappe.db.commit()

@frappe.whitelist()
def get_unpaid_currency(sale_invoice):
	data = frappe.db.get_all('Sales Invoice Payment',
	filters={
		'parent': sale_invoice,
		'balance':['!=',0]
	},
 	fields=['currency', 'grand_total','balance','paid_amount'])
	return data