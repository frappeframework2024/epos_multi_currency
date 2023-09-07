# Copyright (c) 2023, ESTC and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


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