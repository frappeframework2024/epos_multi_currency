# Copyright (c) 2023, ESTC and contributors
# For license information, please see license.txt
from epos_multi_currency.utils import add_to_inventory_transaction
import frappe
from frappe.model.document import Document


class StockAdjustment(Document):
	def on_submit(self):
		if len(self.items) >= 20:
			frappe.enqueue('epos_multi_currency.stock.doctype.stock_adjustment.stock_adjustment.update_inventory_on_submit',self=self)
		else:
			update_inventory_on_submit(self)

@frappe.whitelist()
def get_product(stock_location,barcode):
	try:
		frappe.flags.mute_messages = True
		p = frappe.get_doc("Item",{"item_code":barcode,"enable":1},["*"])
		if p :
			return {
				"status":0,#
				"item_code": p.item_code,
				"item_name":p.item_name_en,
				"currency":p.currency,
				"uom":p.uom,
				"cost":p.cost,
				"price":p.price,
				"whole_sale":p.whole_sale,
				"available_stock":get_available_stock(stock_location,barcode)["quantity"] or 0
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
def get_available_stock(stock_location,item_code):
	if frappe.db.exists("Stock Location Item",{"parent":item_code,"stock_location":stock_location}):
		p = frappe.get_doc("Stock Location Item",{"parent":item_code,"stock_location":stock_location},["*"])
		if p :
			return {
				"quantity": p.quantity
			}
	else:
		return {
			"quantity": 0
		}
	
def update_inventory_on_submit(self):
	for item in self.items:
			if item.new_quantity - item.current_quantity < 0:
				add_to_inventory_transaction({
					'doctype': 'Inventory Transaction',
					'transaction_type':"Stock Adjustment",
					'transaction_date':self.stock_adjustment_date,
					'transaction_number':self.name,
					'item_code': item.item,
					'unit':item.uom,
					'stock_location':item.stock_location,
					'out_quantity': (item.current_quantity - item.new_quantity) * item.uom_conversion,
					"uom_conversion":item.uom_conversion,
					"cost":item.cost,
					'action': 'Submit'
				})
			else:
				add_to_inventory_transaction({
					'doctype': 'Inventory Transaction',
					'transaction_type':"Stock Adjustment",
					'transaction_date':self.stock_adjustment_date,
					'transaction_number':self.name,
					'item_code': item.item,
					'unit':item.uom,
					'stock_location':item.stock_location,
					'in_quantity':(item.new_quantity - item.current_quantity) * item.uom_conversion,
					"uom_conversion":item.uom_conversion,
					"cost":item.cost,
					'action': 'Submit'
				})