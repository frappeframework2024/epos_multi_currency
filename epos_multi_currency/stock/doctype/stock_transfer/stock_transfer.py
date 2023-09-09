# Copyright (c) 2023, ESTC and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from frappe import _

class StockTransfer(Document):
	def validate(self):
		for item in self.items:
			if not item.source_stock_location:
				item.source_stock_location = self.source_stock_location
			if not item.target_stock_location:
				item.target_stock_location = self.target_stock_location

		if self.source_stock_location == self.target_stock_location:
			frappe.throw(_('Source Stock Location and Target Stock Location Cannot be the same.'))

	def on_submit(self):
		self.update_stock()

	def update_stock(self):
		frappe.enqueue('epos_multi_currency.stock.doctype.stock_transfer.stock_transfer.update_inventory_to_source',self=self)
		frappe.enqueue('epos_multi_currency.stock.doctype.stock_transfer.stock_transfer.update_inventory_to_target',self=self)

def update_inventory_to_source(self):
	for p in self.items:
		if p.is_inventory_product:
			
			uom_conversion = get_uom_conversion(p.stock_uom, p.uom)
			add_to_inventory_transaction({
				'doctype': 'Inventory Transaction',
				'transaction_type':"Stock In",
				'transaction_date':self.transafer_date,
				'transaction_number':self.name,
				'item_code': p.item,
				'unit':p.uom,
				'stock_location':self.stock_location,
				'in_quantity':p.quantity / uom_conversion,
				"uom_conversion":uom_conversion,
				"cost":p.cost,
				'note': "New Stock In submitted from ".format(),
				'action': 'Submit'
			})

def update_inventory_to_target(self):
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
				'note': 'Stock Transfer transafer.',
				'action': 'Cancel'
			})