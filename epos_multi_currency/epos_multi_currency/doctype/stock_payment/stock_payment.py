# Copyright (c) 2023, ESTC and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class StockPayment(Document):
	def validate(self):
		for payment in self.payments:
			if payment.balance < 0:
				frappe.throw(_("Payment amount cannot greater than grand total."))


	def on_submit(self):
		for a in self.payments:
			c = frappe.db.sql("""
					 update `tabStock In Payment` 
					 set paid_amount = paid_amount + {},
					 balance = grand_total - paid_amount
					 where parent = '{}' and currency='{}'""".
					 format(a.payment_amount,self.stock_in,a.currency))
			
			c = frappe.db.sql("""UPDATE `tabStock In`
								SET status = if(status="Return","Return",(select if(sum(paid_amount)-sum(grand_total) = 0,"Paid","Partly Paid") from `tabStock In Payment` where parent = '{0}'))
								WHERE NAME = '{0}'""".format(self.stock_in),as_dict=1)
			frappe.db.commit()


@frappe.whitelist()
def get_unpaid_currency(stock_in):
	data = frappe.db.get_all('Stock In Payment',
	filters={
		'parent': stock_in,
		'balance':['!=',0]
	},
 	fields=['currency', 'grand_total','balance','paid_amount'])
	return data