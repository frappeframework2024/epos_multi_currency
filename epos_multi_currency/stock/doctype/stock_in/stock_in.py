# Copyright (c) 2023, ESTC and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from collections import Counter
from epos_multi_currency.utils import add_to_inventory_transaction,get_uom_conversion
from datetime import datetime

class StockIn(Document):
	def validate(self):
		error_msg=""
		for item in self.items:
			if not item.stock_location:
				item.stock_location = self.stock_location
			if item.quantity < 0:
				error_msg = error_msg + "Item {} quantity can't be smaller than 0<br/>".format(item.item)
		if len(error_msg)>0:
			frappe.throw(error_msg)
	def before_save(self):
		self.status = "Unpaid"

	def on_update(self):
		if len(self.stock_in_payments) > 0:
			already = []
			duplicate = []
			for a in self.stock_in_payments:
				if a.currency not in already:
					already.append(a.currency)
				else:
					duplicate.append(a.currency)
			if(len(duplicate)>0):
				for a in duplicate:
					error_msg = error_msg + "{} already exist".format(a.currency)
				frappe.throw(str(error_msg))

		item_currencies = Counter()
		for v in self.items:
			item_currencies[v.currency] += v.grand_total

		payment_currency=[]
		for a in self.stock_in_payments:
			payment_currency.append(a)
		
		frappe.db.sql("delete from `tabStock In Payment` where parent = '{}' ".format(self.name))

		for currency, grand_total in item_currencies.items():
			list_payment_currency = list([a for a in payment_currency if a.currency == currency])
			if len(list_payment_currency) > 0:
				b = list_payment_currency[0]
				if currency == b.currency:
					c = frappe.get_doc({"doctype":"Stock In Payment", 
							"currency":currency,
							"total_amount":grand_total,
							"discount_amount":b.discount_amount or 0,
							"write_off_amount":b.write_off_amount or 0,
							"grand_total":grand_total,
							"paid_amount":b.paid_amount or 0,
							"balance":b.balance or 0,
							"parent":self.name,
							"parentfield":"stock_in_payments",
							"parenttype":"Stock In"})
					c.insert()
			else:
				c = frappe.get_doc({"doctype":"Stock In Payment", 
						"currency":currency,
						"total_amount":grand_total,
						"discount_amount": 0 if self.discount_percent is None or 0 else grand_total * self.discount_percent/100,
						"write_off_amount": 0,
						"grand_total":grand_total,
						"paid_amount":0,
						"balance":grand_total,
						"parent":self.name,
						"parentfield":"stock_in_payments",
						"parenttype":"Stock In"})
				c.insert()
		self.reload()

	def on_submit(self):
		if len(self.items) >= 20:
			frappe.enqueue('epos_multi_currency.stock.doctype.stock_in.stock_in.update_inventory_on_submit',self=self)
		else:
			update_inventory_on_submit(self)


	def on_cancel(self):
		if len(self.items) >= 20:
			frappe.enqueue('epos_multi_currency.stock.doctype.stock_in.stock_in.update_inventory_on_cancel',self=self)
		else:
			update_inventory_on_cancel(self)


    
def update_inventory_on_submit(self):
	
	for p in self.items:
		if p.is_inventory_product:
			uom_conversion =  get_uom_conversion(p.uom, p.stock_uom)
			add_to_inventory_transaction({
				'doctype': 'Inventory Transaction',
				'transaction_type':"Stock In",
				'transaction_date':self.stock_in_date,
				'transaction_number':self.name,
				'item_code': p.item,
				'unit':p.uom,
				'stock_unit':p.stock_uom,
				'stock_location':self.stock_location,
				'in_quantity':p.quantity * uom_conversion,
				"uom_conversion":uom_conversion,
				"cost":p.cost,
				'note': 'New Stock In submitted.',
				'action': 'Submit'
			})

def update_inventory_on_cancel(self):
	for p in self.items:
		if p.is_inventory_product:
			uom_conversion = get_uom_conversion(p.uom, p.stock_uom)
			print(uom_conversion)
			add_to_inventory_transaction({
				'doctype': 'Inventory Transaction',
				'transaction_type':"Stock In",
				'transaction_date':self.stock_in_date,
				'transaction_number':self.name,
				'item_code': p.item,
				'unit':p.uom,
				'stock_unit':p.stock_uom,
				'stock_location':self.stock_location,
				'out_quantity':p.quantity * uom_conversion,
    			"uom_conversion":uom_conversion,
				"cost":p.cost,
				'note': 'Stock In cancelled.',
				'action': 'Cancel'
			})







