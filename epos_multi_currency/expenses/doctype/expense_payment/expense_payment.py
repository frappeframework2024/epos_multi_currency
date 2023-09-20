# Copyright (c) 2023, ESTC and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document


class ExpensePayment(Document):
	def validate(self):
		for payment in self.payments:
			if payment.balance < 0:
				frappe.throw(_("Payment amount cannot greater than grand total."))


	def on_submit(self):
		for a in self.payments:
			c = frappe.db.sql("""
					 update `tabExpense Total Summary` 
					 set paid_amount = paid_amount + {},
					 balance = total_amount - paid_amount
					 where parent = '{}' and currency='{}'""".
					 format(a.payment_amount,self.expense,a.currency))
			frappe.db.commit()

			c = frappe.db.sql("""UPDATE `tabExpense`
								SET status = (select if(sum(paid_amount)-sum(total_amount) = 0,"Paid","Partly Paid") from `tabExpense Total Summary` where parent = '{0}')
								WHERE NAME = '{0}'""".format(self.expense),as_dict=1)
			frappe.db.commit()


@frappe.whitelist()
def get_unpaid_currency(expense):
	data = frappe.db.get_all('Expense Total Summary',
	filters={
		'parent': expense,
		'balance':['!=',0]
	},
 	fields=['currency', 'total_amount' ,'balance','paid_amount'])
	return data
