# Copyright (c) 2023, ESTC and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from collections import Counter
from epos_multi_currency.epos_multi_currency.utils import add_to_inventory_transaction,get_uom_conversion


class StockIn(Document):
	def validate(self):
		a = Counter()
		# frappe.throw(str(a))
		for item in self.items:
			if not item.stock_location:
				item.stock_location = self.stock_location

	def after_insert(self):
		c = Counter()
		for v in self.items:
			c[v.currency] += v.grand_total

		for currency, grand_total in c.items():
			c = frappe.get_doc({
       					"doctype":"Stock In Payment", 
					  	"currency":currency,
					  	"total_amount":grand_total,
					  	"parent":self.name,
					  	"parentfield":"stock_in_payments",
					  	"parenttype":"Stock In"
       				})
			c.insert()
		self.reload()

	def on_update(self):
		if len(self.stock_in_payments)>0:
			already = []
			duplicate = []
			for a in self.stock_in_payments:
				if a.currency not in already:
					already.append(a.currency)
				else:
					duplicate.append(a.currency)
			if(len(duplicate)>0):
				error_msg=""
				for a in duplicate:
					error_msg = error_msg + a
				frappe.throw(str(error_msg))

			c = Counter()
			for v in self.items:
				c[v.currency] += v.grand_total

			for currency, grand_total in c.items():
				for a in self.stock_in_payments:
					c = frappe.get_doc("Stock In Payment",a.name)
					if c.currency == currency:
						c.total_amount = grand_total
						c.grand_total = c.total_amount - c.discount_amount
						c.balance = c.paid_amount - c.grand_total
						c.save()
			
		# for a in self.items:
		# 	if self.discount_percent > 0 :
		# 		c = frappe.get_doc("Stock In Item",a.name)
		# 		c.sales_invoice_discount = c.price * self.discount_percent/100
		# 		c.save()
		self.reload()

	def on_submit(self):
		"""Update product inventory when submit"""
		frappe.enqueue('epos_multi_currency.epos_multi_currency.doctype.stock_in.stock_in.update_inventory_on_submit',self=self)
	def on_cancel(self):
		"""	update product inventory when cancel
  		"""
		frappe.enqueue('epos_multi_currency.epos_multi_currency.doctype.stock_in.stock_in.update_inventory_on_cancel',self=self)

	def on_update(self):
		
		item_currencies = Counter()
		for v in self.items:
			item_currencies[v.currency] += v.grand_total

		if len(self.stock_in_payments)>0:
			already = []
			duplicate = []
			for a in self.stock_in_payments:
				if a.currency not in already:
					already.append(a.currency)
				else:
					duplicate.append(a.currency)
			if(len(duplicate)>0):
				error_msg="Currency Already Exist: "
				for a in duplicate:
					error_msg = error_msg + a + " "
				frappe.throw(str(error_msg))

			for currency, grand_total in item_currencies.items():
				for a in self.stock_in_payments:
					c = frappe.get_doc("Sales Invoice Payment",a.name)
					if c.currency == currency:
						c.total_amount = grand_total
						c.grand_total = c.total_amount - (c.discount_amount + c.write_off_amount)
						c.balance = c.paid_amount - c.grand_total
						c.save()
			

		
		item_currency=[]
		for currency,grand_total in item_currencies.items():
			item_currency.append(currency)

		if len(item_currency) >= len(self.sales_invoice_payment):
			for a in self.sales_invoice_payment:
				item_currency.remove(a.currency)
			for currency, grand_total in item_currencies.items():
				if currency in item_currency:
					c = frappe.get_doc({"doctype":"Sales Invoice Payment", 
							"currency":currency,
							"total_amount":grand_total,
							"grand_total":grand_total,
							"balance" : grand_total *-1,
							"parent":self.name,
							"parentfield":"sales_invoice_payment",
							"parenttype":"Sales Invoice"})
					c.insert()
		else:
			
			for a in self.sales_invoice_payment:
				if a.currency not in item_currency:
					c = frappe.delete_doc("Sales Invoice Payment",a.name)		
		
		for b in self.sales_invoice_payment:
			for a in self.items:
				if a.currency == b.currency:
					frappe.db.set_value('Sales Invoice Item', a.name, {
						'sales_invoice_discount_rate': a.price * b.discount_amount/b.total_amount,
						'sales_invoice_write_off_rate': a.price * b.write_off_amount/b.total_amount
					})
    
def update_inventory_on_submit(self):
	
	for p in self.items:
		if p.is_inventory_product:
			
			uom_conversion = get_uom_conversion(p.base_uom, p.uom)
			add_to_inventory_transaction({
				'doctype': 'Inventory Transaction',
				'transaction_type':"Stock In",
				'transaction_date':self.posting_date,
				'transaction_number':self.name,
				'item_code': p.item,
				'unit':p.uom,
				'stock_location':self.stock_location,
				'in_quantity':p.quantity / uom_conversion,
				"uom_conversion":uom_conversion,
				"cost":p.cost,
				'note': 'New Stock In submitted.',
				'action': 'Submit'
			})

def update_inventory_on_cancel(self):
	for p in self.items:
		if p.is_inventory_product:
			uom_conversion = get_uom_conversion(p.base_uom, p.uom)
			add_to_inventory_transaction({
				'doctype': 'Inventory Transaction',
				'transaction_type':"Stock In",
				'transaction_date':self.posting_date,
				'transaction_number':self.name,
				'item_code': p.item,
				'unit':p.uom,
				'stock_location':self.stock_location,
				'out_quantity':p.quantity / uom_conversion,
				"cost":p.cost,
				'note': 'Purchase order cancelled.',
				'action': 'Cancel'
			})





