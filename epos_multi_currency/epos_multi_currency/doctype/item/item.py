# Copyright (c) 2023, ESTC and contributors
# For license information, please see license.txt

import frappe
from epos_multi_currency.utils import add_to_inventory_transaction

from frappe.model.document import Document
from frappe.utils import fmt_money
from frappe.utils.formatters import format_value

class Item(Document):
	def after_insert(self):
		stock_location = frappe.db.get_list('Stock Location')
		for a in stock_location:
			if a.name == self.opening_stock_location:
				b = frappe.get_doc({"doctype":"Stock Location Item", 
						"stock_location": a.name,
						"item":self.item_code,
						"quantity":self.opening_qty,
						"stock_uom":self.uom,
						"is_inventory":self.is_inventory_product,
						"stock_location_enable":1,
						"item_enable":1,
						"parent":self.name,
						"parentfield":"stock_location_item",
						"parenttype":"item"})
				b.insert(ignore_permissions = True)
			else:
				b = frappe.get_doc({"doctype":"Stock Location Item", 
						"stock_location": a.name,
						"item":self.item_code,
						"quantity":0,
						"stock_uom":self.uom,
						"is_inventory":self.is_inventory_product,
						"stock_location_enable":1,
						"item_enable":1,
						"parent":self.name,
						"parentfield":"stock_location_item",
						"parenttype":"item"})
				b.insert(ignore_permissions = True)
			add_to_inventory_transaction({
				'doctype': 'Inventory Transaction',
				'transaction_type':"Item",
				'transaction_date':self.creation,
				'transaction_number':self.name,
				'item_code': self.name,
				'unit':self.uom,
				'stock_location':a.name,
				'in_quantity':0,
				'uom_conversion':1,
				'cost':self.cost,
				'price':self.price,
				'stock_unit':self.uom,
				'note': """New Item {} - {} created""".format(self.item_code,self.item_name_en),
				'action': 'create'
			})
			self.reload()


		c = frappe.get_doc({"doctype":"Item UOM", 
			"item": self.name,
			"currency":self.currency,
			"uom":self.uom,
			"cost":self.cost,
			"whole_sale":self.whole_sale,
			"price":self.price,
			"parent":self.name,
			"parentfield":"item_uom",
			"parenttype":"item"})
		c.insert(ignore_permissions = True)

		self.reload()



	def before_save(self):
		if len(self.item_uom)>0:
			uom_list = self.item_uom
			str_json = ""
			for x in uom_list:
				str_json += str(x.uom) + ","
			str_json = str_json[0:len(str_json)-1]
			self.uom_list = str_json
		else:
			self.uom_list = ""
	
	def on_update(self):
		for a in self.item_uom:
			c = frappe.get_doc("Item UOM",a.name)
			if c.uom == self.uom:
				c.cost = self.cost
				c.whole_sale = self.whole_sale
				c.price = self.price
				c.save()
		self.reload()