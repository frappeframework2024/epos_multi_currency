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
			if(len(duplicate)>0  and not self.is_new()):
				error_msg="Currency Already Exist: "
				for a in duplicate:
					error_msg = error_msg + a + " " + str(self)
				frappe.throw(str(error_msg))

			for currency, grand_total in item_currencies.items():
				for a in self.stock_in_payments:
					c = frappe.get_doc("Stock In Payment",a.name)
					if c.currency == currency:
						c.total_amount = grand_total
						c.grand_total = c.total_amount - (c.discount_amount + c.write_off_amount)
						c.balance = c.paid_amount - c.grand_total
						c.save()
			

		
		item_currency=[]
		for currency,grand_total in item_currencies.items():
			item_currency.append(currency)

		if len(item_currency) >= len(self.stock_in_payments):
			for a in self.stock_in_payments:
				item_currency.remove(a.currency)
			for currency, grand_total in item_currencies.items():
				if currency in item_currency:
					c = frappe.get_doc({"doctype":"Stock In Payment", 
							"currency":currency,
							"total_amount":grand_total,
							"grand_total":grand_total,
							"balance" : grand_total *-1,
							"parent":self.name,
							"parentfield":"stock_in_payments",
							"parenttype":"Stock In"})
					c.insert()
		else:
			
			for a in self.stock_in_payments:
				if a.currency not in item_currency:
					c = frappe.delete_doc("Stock In Payment",a.name)

	def on_submit(self):
		"""Update product inventory when submit"""
		frappe.enqueue('epos_multi_currency.epos_multi_currency.doctype.stock_in.stock_in.update_inventory_on_submit',self=self)
	def on_cancel(self):
		"""	update product inventory when cancel
  		"""
		frappe.enqueue('epos_multi_currency.epos_multi_currency.doctype.stock_in.stock_in.update_inventory_on_cancel',self=self)


    
def update_inventory_on_submit(self):
	
	for p in self.items:
		if p.is_inventory_product:
			
			uom_conversion = get_uom_conversion(p.stock_uom, p.uom)
			add_to_inventory_transaction({
				'doctype': 'Inventory Transaction',
				'transaction_type':"Stock In",
				'transaction_date':self.stock_in_date,
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
			uom_conversion = get_uom_conversion(p.stock_uom, p.uom)
			print(uom_conversion)
			add_to_inventory_transaction({
				'doctype': 'Inventory Transaction',
				'transaction_type':"Stock In",
				'transaction_date':self.posting_date,
				'transaction_number':self.name,
				'item_code': p.item,
				'unit':p.uom,
				'stock_location':self.stock_location,
				'out_quantity':p.quantity / uom_conversion,
    			"uom_conversion":uom_conversion,
				"cost":p.cost,
				'note': 'Purchase order cancelled.',
				'action': 'Cancel'
			})





