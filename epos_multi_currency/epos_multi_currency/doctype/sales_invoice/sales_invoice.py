# Copyright (c) 2023, ESTC and contributors
# For license information, please see license.txt
from epos_multi_currency.utils import get_uom_conversion,add_to_inventory_transaction
import frappe
from frappe.model.document import Document
import json
from datetime import datetime
from collections import Counter
from frappe import _
from frappe.model.naming import make_autoname

class SalesInvoice(Document):

	def validate(self):
		if len(self.items) == 0:
			frappe.throw("Item Can't Be Empty")
		error_msg=""
		if self.is_return == 1:
			for a in self.items:
				if a.quantity > 0:
					error_msg = error_msg + "Item {} quantity can't be greater than 0<br/>".format(a.item_code)

		else:
			for a in self.items:
				if a.quantity < 0:
					error_msg = error_msg + "Item {} 1qantity can't be negative<br/>".format(a.item_code)
		if error_msg:
			frappe.throw(str(error_msg))

	def on_cancel(self):
		for a in self.items:
			update_stock(self,a,1)

	def on_submit(self):
		for a in self.items:
			update_stock(self,a,self.is_return)

	def before_save(self):
		self.status = "Unpaid" if self.is_return == 0 else "Return"
		date_object = datetime.strptime(self.sale_date, '%Y-%m-%d')
		day_name = date_object.strftime('%A')
		self.khmer_day = _(day_name)

		for a in self.items:
			discount_rate = 0
			if a.discount_type == "Percent":
				discount_rate = 0 if a.discount is None or 0 else a.price*a.discount/100; 
			else:
				discount_rate = a.discount_amount or 0/a.quantity
			a.price_after_discount = a.price - discount_rate

	def after_insert(self):
		if not self.document_number:
			document_number = make_autoname(".#####", "", self)
			frappe.db.set_value('Sales Invoice', self.name, 'document_number', document_number, update_modified=False)

	def on_update(self):
		
		if len(self.sales_invoice_payment) > 0:
			already = []
			duplicate = []
			for a in self.sales_invoice_payment:
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
		for a in self.sales_invoice_payment:
			payment_currency.append(a)
		
		frappe.db.sql("delete from `tabSales Invoice Payment` where parent = '{}' ".format(self.name))

		for currency, grand_total in item_currencies.items():
			list_payment_currency = list([a for a in payment_currency if a.currency == currency])
			if len(list_payment_currency) > 0:
				b = list_payment_currency[0]
				if currency == b.currency:
					c = frappe.get_doc({"doctype":"Sales Invoice Payment", 
							"currency":currency,
							"total_amount":grand_total,
							"discount_amount":b.discount_amount or 0,
							"write_off_amount":b.write_off_amount or 0,
							"grand_total":grand_total,
							"paid_amount":b.paid_amount or 0,
							"balance":b.balance or 0,
							"parent":self.name,
							"parentfield":"sales_invoice_payment",
							"parenttype":"Sales Invoice"})
					c.insert()
			else:
				c = frappe.get_doc({"doctype":"Sales Invoice Payment", 
						"currency":currency,
						"total_amount":grand_total,
						"discount_amount": 0 if self.discount_percent is None or 0 else grand_total * self.discount_percent/100,
						"write_off_amount": 0,
						"grand_total":grand_total,
						"paid_amount":0,
						"balance":grand_total,
						"parent":self.name,
						"parentfield":"sales_invoice_payment",
						"parenttype":"Sales Invoice"})
				c.insert()
		self.reload()

		for a in self.sales_invoice_payment:
			c = frappe.get_doc("Sales Invoice Payment",a.name)
			c.grand_total = c.total_amount - (c.discount_amount + c.write_off_amount)
			c.balance = c.grand_total - c.paid_amount
			c.save()

		for b in self.sales_invoice_payment:
			for a in self.items:
				if a.currency == b.currency:
					frappe.db.set_value('Sales Invoice Item', a.name, {
						'sales_invoice_discount_rate': 0 if a.price == 0 or b.discount_amount ==0 else a.price * b.discount_amount/b.total_amount,
						'sales_invoice_write_off_rate': 0 if a.price ==0 or b.write_off_amount ==0 else a.price * b.write_off_amount/b.total_amount
					})
		
def update_stock(self,item,is_return):
	
	if is_return == 0:
		add_to_inventory_transaction({
			'doctype': 'Inventory Transaction',
			'transaction_type':"Sales Invoice",
			'transaction_date':self.sale_date,
			'transaction_number':self.name,
			'item_code': item.item,
			'unit':item.uom,
			'stock_location':item.stock_location,
			'out_quantity':item.quantity * item.uom_conversion,
			"uom_conversion":item.uom_conversion,
			"cost":item.cost,
			'action': 'Submit'
		})
	else:
		add_to_inventory_transaction({
			'doctype': 'Inventory Transaction',
			'transaction_type':"Sales Invoice",
			'transaction_date':self.sale_date,
			'transaction_number':self.name,
			'item_code': item.item,
			'unit':item.uom,
			'stock_location':item.stock_location,
			'in_quantity':item.quantity * item.uom_conversion,
			"uom_conversion":item.uom_conversion,
			"cost":item.cost,
			"Note":"Cancel Sales Invoice",
			'action': 'Submit'
		})

	
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
				"allow_discount":p.allow_discount,
				"is_inventory_product":p.is_inventory_product,
				"uom_list":p.uom_list,
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
def get_item_uom_price(item_code,uom,stock_uom):
	uom_coversion = get_uom_conversion(uom,stock_uom)
	if frappe.db.exists("Item UOM", {"parent":item_code,"uom":uom}):
		p = frappe.get_doc("Item UOM",{"parent":item_code,"uom":uom},["*"])
		if p :
			return {
				"cost": p.cost,
				"whole_sale": p.whole_sale,
				"price": p.price,
				"uom_conversion":uom_coversion,
				"predefine":1
			}
			
	else:
		p = frappe.get_doc("Item UOM",{"parent":item_code,"uom":stock_uom},["*"])
		return {
			"cost": p.cost,
			"whole_sale": p.whole_sale,
			"price": p.price,
			"uom_conversion":uom_coversion,
			"predefine":0
		}
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

@frappe.whitelist()
def get_item_uom_list(item_code):
	p = frappe.db.sql("select uom from `tabItem UOM` where parent = '{}'".format(item_code))
	if p :
		return p
	else:
		return {
			"status":404,
			"message":("No Item UOM")
		}

@frappe.whitelist()
def get_currency_total_amount(pcurrency,items):
	c = Counter()
	list_item = json.loads(items)
	for v in list_item:
		c[v['currency']] += v['grand_total']
	total_amount = 0
	filtered_list = [grand_total for currency,grand_total in c.items() if currency == pcurrency]
	if len(filtered_list) > 0:
		total_amount = float(filtered_list[0])
	else:
		total_amount = 0
	return {"total_amount" : total_amount}

@frappe.whitelist()
def get_default_stock_location():
	p = frappe.get_doc("Stock Location",{"is_default":1},["*"])
	if p:
		return {"stock_location_name": p.stock_location_name}