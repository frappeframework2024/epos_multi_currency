# Copyright (c) 2023, ESTC and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from collections import Counter
from epos_multi_currency.utils import add_to_inventory_transaction,get_uom_conversion
from datetime import datetime

class StockTake(Document):
	def validate(self):
		error_msg=""
		for item in self.items:
			if not item.stock_location:
				item.stock_location = self.stock_location
			if item.quantity < 0:
				error_msg = error_msg + "Item {} quantity can't be greater than 0<br/>".format(item.item)
		if len(error_msg)>0:
			frappe.throw(error_msg)

	def on_submit(self):
		if len(self.items) >= 20:
			frappe.enqueue('epos_multi_currency.stock.doctype.stock_take.stock_take.update_inventory_on_submit',self=self)
		else:
			update_inventory_on_submit(self)


	def on_cancel(self):
		if len(self.items) >= 20:
			frappe.enqueue('epos_multi_currency.stock.doctype.stock_take.stock_take.update_inventory_on_cancel',self=self)
		else:
			update_inventory_on_cancel(self)


    
def update_inventory_on_submit(self):
	
	for p in self.items:
		if p.is_inventory_product:
			uom_conversion = get_uom_conversion(p.uom, p.stock_uom)
			add_to_inventory_transaction({
				'doctype': 'Inventory Transaction',
				'transaction_type':"Stock Take",
				'transaction_date':self.stock_take_date,
				'transaction_number':self.name,
				'item_code': p.item,
				'unit':p.uom,
				'stock_unit':p.stock_uom,
				'stock_location':self.stock_location,
				'out_quantity':p.quantity * uom_conversion,
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
				'transaction_type':"Stock Take",
				'transaction_date':self.stock_take_date,
				'transaction_number':self.name,
				'item_code': p.item,
				'unit':p.uom,
				'stock_unit':p.stock_uom,
				'stock_location':self.stock_location,
				'in_quantity':p.quantity * uom_conversion,
    			"uom_conversion":uom_conversion,
				"cost":p.cost,
				'note': 'Stock take cancelled.',
				'action': 'Cancel'
			})







