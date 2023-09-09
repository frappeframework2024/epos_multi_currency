# Copyright (c) 2023, ESTC and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class InventoryTransaction(Document):
	def validate(self):
		data = frappe.db.sql("select name, quantity, cost from `tabStock Location Item` where parent ='{}' and stock_location = '{}' limit 1".format(self.item_code, self.stock_location), as_dict=1)
		if data:
			current_qty = data[0]["quantity"]

			current_cost = data[0]["cost"]
			if (current_cost or 0) == 0:
				#get cost from product
				p = frappe.get_doc("Item",self.item_code, "cost")
				current_cost = p.cost or 0
			
			self.price = self.price or current_cost
			
			self.beginning_stock_value = current_qty * current_cost
			self.quantity_on_hand = current_qty
			self.balance = self.quantity_on_hand + self.in_quantity - self.out_quantity
			if self.transaction_type =='Stock Adjustment' and self.action =="Submit":
				self.ending_stock_value = self.balance * self.price
			else:
				self.ending_stock_value = self.beginning_stock_value + (self.in_quantity - self.out_quantity) * (self.price or current_cost)
			
			self.product_has_in_stock_location = 1
			self.stock_location_product_name = data[0]["name"]
		else:
			self.product_has_in_stock_location = 0
			self.balance = self.in_quantity - self.out_quantity
			if (self.price or 0)==0:
				p = frappe.get_doc("Product",self.item_code, "cost")
				self.price = p.cost or 0
    
			if self.transaction_type =='Stock Adjustment' and self.action =="Submit":
				self.ending_stock_value = self.balance * self.price
			else:
				self.ending_stock_value =  (self.in_quantity - self.out_quantity) * (self.price or 0 )
		
		

	def after_insert(self):
		
		if self.product_has_in_stock_location==0:
			add_stock_location_item(self)
		else:
			update_stock_location_item(self)
        

def add_stock_location_item(self):
	cost = 0
	if self.transaction_type=="Stock Adjustment" and self.action =="Submit":
		cost = self.price
	else:
		cost = self.ending_stock_value / (self.balance if self.balance > 0 else 1)
		
	doc = frappe.get_doc({
			"doctype":"Stock Location Item",
			"parent":self.item_code,
			"parenttype":"Item",
			"parentfield":'stock_location_item',
			"stock_location" : self.stock_location, 
			"cost" : cost,
			"quantity" : self.balance,
			"is_inventory":self.is_inventory,
			"stock_location_enable":self.stock_location_enable,
			"total_cost" :  cost * (self.balance or 0)
		}
	)

	doc.insert()

def update_stock_location_item(self):
	doc = frappe.get_doc("Stock Location Item",self.stock_location_product_name )
	balance = 1 if self.balance == 0 else self.balance

	if self.transaction_type=="Stock Adjustment":
		if self.action =="Submit":
			doc.cost = self.price
		else:
			doc.cost = self.price
	else:
			doc.cost = self.ending_stock_value / balance

	doc.quantity = self.balance
	doc.total_cost =  self.ending_stock_value
	
	doc.save()
