import frappe
import json

def add_to_inventory_transaction(data):
	if data.get('in_quantity') or data.get('out_quantity'):
	# if data.get('in_quantity') is not None :
		doc = frappe.get_doc(data)
		# frappe.throw(str(json.dumps(data)))
		doc.insert()

def update_item_quantity(stock_location,item_code, quantity,cost,doc):
    if doc:
        doc.quantity =(doc.quantity or 0) + (quantity or 0)
        if cost != None:
                doc.cost = ((doc.total_cost or 0) + cost*quantity) / (doc.quantity if doc.quantity>0 else 1)  
                
        doc.total_cost = (doc.cost or 0) * (doc.quantity or 0)
        doc.save()
      
    else:
        doc = frappe.get_doc({
					'doctype': 'Stock Location Item',
					'item_code': item_code,
					'stock_location':stock_location,
					'quantity':quantity or 0,
					'cost':cost or 0,
					'total_cost':(quantity or 0) * (cost or 0)
				})
        doc.insert() 
        
def get_stock_location_product(stock_location,item_code):
    data = frappe.db.sql("select name from `tabStock Location Item` where stock_location='{}' and item_code='{}'".format(stock_location, item_code), as_dict=1)
    if data:
            return frappe.get_doc("Stock Location Item", data[0].name)
    else:
        return None

      
   

def get_uom_conversion(from_uom, to_uom):
    conversion =frappe.db.get_value('Unit of Measurement Conversion', {'from_uom': from_uom,"to_uom":to_uom}, ['conversion'], cache=True)
    
    return conversion or 1

def get_product_cost(stock_location, item_code):
    cost =frappe.db.get_value('Stock Location Item', {'stock_location':stock_location,"item_code":item_code}, ['cost'], cache=True)
    if (cost or 0) == 0:
        cost = frappe.db.get_value('Item',{'item_code':item_code}, ['cost'], cache=True)
    
    return cost or 0

def check_uom_conversion(from_uom, to_uom):
    conversion =frappe.db.get_value('Unit of Measurement Conversion', {'from_uom': from_uom,"to_uom":to_uom}, ['conversion'])
    return conversion

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
def get_default_stock_location():
	p = frappe.get_doc("Stock Location",{"is_default":1},["*"])
	if p:
		return {"stock_location_name": p.stock_location_name}

@frappe.whitelist()
def get_product_by_barcode(barcode):
	try:
		frappe.flags.mute_messages = True
		p = frappe.get_doc("Item",{"item_code":barcode,"enable":1},["*"])
		if p :
			return {
				"status":200,#success
				"item_code": p.item_code,
				"item_name":p.item_name_en,
				"currency":p.currency,
				"uom":p.uom,
				"cost":p.cost,
				"price":p.price,
				"allow_discount":p.allow_discount,
				"is_inventory_product":p.is_inventory_product,
				"uom_list":p.uom_list
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
def get_item_uoms(item):
	uom = frappe.db.sql("""select uom from `tabItem UOM` where parent = '{}'""".format(item))
	return uom