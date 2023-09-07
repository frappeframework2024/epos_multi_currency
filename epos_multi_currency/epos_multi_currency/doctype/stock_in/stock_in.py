# Copyright (c) 2023, ESTC and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
# from py_linq import Enumerable
from epos_multi_currency.epos_multi_currency.utils import add_to_inventory_transaction,get_uom_conversion


class StockIn(Document):
	def validate(self):
		for item in self.items:
			if not item.stock_location:
				item.stock_location = self.stock_location

	def on_submit(self):
		#update_inventory_on_submit(self)
		frappe.enqueue("epos_multi_currency.epos_multi_currency.doctype.stock_in.stock_in.update_inventory_on_submit", queue='short', self=self)

def update_inventory_on_submit(self):
	
	for p in self.stock_in_item:
		if p.is_inventory_product:
			
			uom_conversion = get_uom_conversion(p.base_unit, p.unit)
			add_to_inventory_transaction({
				'doctype': 'Inventory Transaction',
				'transaction_type':"Stock In",
				'transaction_date':self.posting_date,
				'transaction_number':self.name,
				'product_code': p.item,
				'unit':p.unit,
				'stock_location':self.stock_location,
				'in_quantity':p.quantity / uom_conversion,
				"uom_conversion":uom_conversion,
				"price":p.cost,
				'note': 'New Stock In submitted.',
    			'action': 'Submit'
			})

def update_inventory_on_cancel(self):
	for p in self.purchase_order_products:
		if p.is_inventory_product:
			uom_conversion = get_uom_conversion(p.base_unit, p.unit)
			add_to_inventory_transaction({
				'doctype': 'Inventory Transaction',
				'transaction_type':"Stock In",
				'transaction_date':self.posting_date,
				'transaction_number':self.name,
				'product_code': p.product_code,
				'unit':p.unit,
				'stock_location':self.stock_location,
				'out_quantity':p.quantity / uom_conversion,
				"price":p.cost,
				'note': 'Purchase order cancelled.',
				'action': 'Cancel'
			})


