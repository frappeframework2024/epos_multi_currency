# Copyright (c) 2023, ESTC and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
from collections import Counter

class SalesInvoice(Document):
	def before_save(self):
		for a in self.items:
			discount_rate = 0
			if a.discount_type == "Percent":
				discount_rate = a.price*a.discount/100; 
			else:
				discount_rate = a.discount_amount/a.quantity
			a.price_after_discount = a.price - discount_rate
	def on_update(self):
		c = Counter()
		for v in self.items:
			c[v.currency] += v.grand_total

		
		for currency, grand_total in c.items():
			
			c = frappe.get_doc({"doctype":"Sales Invoice Payment", 
					  "currency":currency,
					  "total_amount":grand_total,
					  "parent":self.name,
					  "parentfield":"payment",
					  "parenttype":"Sales Invoice"})
		c.insert()
		frappe.msgprint("aaaaaaaaaaaa")
		

	
@frappe.whitelist()
def get_product(barcode):
	try:
		frappe.flags.mute_messages = True
		p = frappe.get_doc("Item",{"item_code":barcode,"enable":1},["*"])
		if p :
			return {
				"status":0,#success
				"item_code": p.item_code,
				"item_name":p.item_name_en,
				"currency":p.currency,
				"uom":p.uom,
				"cost":p.cost,
				"price":p.price,
				"allow_discount":p.allow_discount,
				"is_inventory_product":p.is_inventory_product
			}
		else:
			return {
				"status":404,
				"message":("Product code {} is not exist".format(barcode))
			}
	except frappe.DoesNotExistError:
		return {
				"status":404,
				"message":("Product code {} is not exist".format(barcode))
			}
		
	finally:
		frappe.flags.mute_messages = False

@frappe.whitelist()
def get_item_uom_price(item_code,uom):
	try:
		frappe.flags.mute_messages = True
		p = frappe.get_doc("Item UOM",{"parent":item_code,"uom":uom},["*"])
		if p :
			return {
				"status":200,
				"cost": p.cost,
				"whole_sale": p.whole_sale,
				"price": p.price,
			}
		else:
			return {
				"status":404,
				"message":("No UOM")
			}
	except frappe.DoesNotExistError:
		return {
				"status":404,
				"message":("No UOM")
			}
		
	finally:
		frappe.flags.mute_messages = False

@frappe.whitelist()
def get_available_stock(stock_location,item_code):
	try:
		frappe.flags.mute_messages = True
		p = frappe.get_doc("Stock Location Item",{"parent":item_code,"stock_location":stock_location},["*"])
		if p :
			return {
				"quantity": p.quantity
			}
		else:
			return {
				"status":404,
				"message":("No Stock Location")
			}
	except frappe.DoesNotExistError:
		return {
				"status":404,
				"message":("No Stock Location")
			}
		
	finally:
		frappe.flags.mute_messages = False

@frappe.whitelist()
def get_item_uom_list(item_code):
	
		
		p = frappe.db.sql("select uom from `tabItem UOM` where parent = '{}'".format(item_code))

		if p :
			return p
		else:
			return {
				"status":404,
				"message":("No Stock Location")
			}
