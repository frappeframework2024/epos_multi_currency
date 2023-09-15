import frappe
import json
from datetime import datetime

def add_to_inventory_transaction(data):
	
	if data.get('in_quantity') or data.get('out_quantity'):
	# if data.get('in_quantity') is not None :
		doc = frappe.get_doc(data)
		
  
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

@frappe.whitelist()
def get_home_workspace_kpi():
	today = datetime.today() 
	mtd_date=today.replace(day=1) #first date of month
	ytd_date = today.replace(month=1).replace(day=1) #first date of month
	
	sql_today="""
			WITH sale AS(
				select 
					a.currency,
				coalesce(sum(coalesce(a.grand_total,0)),0) as grand_total
			FROM `tabSales Invoice Item` a
			inner join `tabSales Invoice` b on b.name = a.parent
			where 
				sale_date ='{}' 
			group by a.currency
			)
			select 
				a.name currency,
				a.number_format format,
				a.symbol,
				coalesce(sum(coalesce(b.grand_total,0)),0) as grand_total
			FROM `tabCurrency` a
				left join sale b ON b.currency = a.name
			where 
				a.enabled = 1
			group by a.name,a.number_format,a.symbol
		""".format(today.strftime('%Y-%m-%d'))
	sql_mtd="""
			WITH sale AS(
				select 
					a.currency,
				coalesce(sum(coalesce(a.grand_total,0)),0) as grand_total
			FROM `tabSales Invoice Item` a
			inner join `tabSales Invoice` b on b.name = a.parent
			where 
				sale_date between '{}' and '{}' 
			group by a.currency
			)
			select 
				a.name currency,
				a.number_format format,
				a.symbol,
				coalesce(sum(coalesce(b.grand_total,0)),0) as grand_total
			FROM `tabCurrency` a
				left join sale b ON b.currency = a.name
			where 
				a.enabled = 1
			group by a.name,a.number_format,a.symbol
		""".format(mtd_date.strftime('%Y-%m-%d'),today.strftime('%Y-%m-%d'))
	sql_ytd="""
			WITH sale AS(
				select 
					a.currency,
				coalesce(sum(coalesce(a.grand_total,0)),0) as grand_total
			FROM `tabSales Invoice Item` a
			inner join `tabSales Invoice` b on b.name = a.parent
			where 
				sale_date between '{}' and '{}' 
			group by a.currency
			)
			select 
				a.name currency,
				a.number_format format,
				a.symbol,
				coalesce(sum(coalesce(b.grand_total,0)),0) as grand_total
			FROM `tabCurrency` a
				left join sale b ON b.currency = a.name
			where 
				a.enabled = 1
			group by a.name,a.number_format,a.symbol
		""".format(ytd_date.strftime('%Y-%m-%d'),today.strftime('%Y-%m-%d'))
	data=dict()
	mtd_total_order = frappe.db.get_list('Sales Invoice',
		 filters= [[
				'sale_date', 'between', [mtd_date.strftime('%Y-%m-%d'),today.strftime('%Y-%m-%d')]
			]],
		fields=['Count(name) as total_order'],
	)
	ytd_total_order = frappe.db.get_list('Sales Invoice',
		filters= [[
				'sale_date', 'between', [ytd_date.strftime('%Y-%m-%d'),today.strftime('%Y-%m-%d')]
			]],
			fields=['Count(name) as total_order'],
		)
	data['today_revenue'] = frappe.db.sql(sql_today,as_dict=1)
	data['mtd_revenue'] = frappe.db.sql(sql_mtd,as_dict=1)
	data['ytd_revenue'] = frappe.db.sql(sql_ytd,as_dict=1)
	
	data['mtd_order'] = mtd_total_order[0].total_order
	data['ytd_order'] = ytd_total_order[0].total_order

	for d in data['today_revenue']:
		d.grand_total = frappe.utils.fmt_money(d.grand_total, currency=d.currency,format=d.format)
	for d in data['mtd_revenue']:
		d.grand_total = frappe.utils.fmt_money(d.grand_total, currency=d.currency,format=d.format)
	for d in data['ytd_revenue']:
		d.grand_total = frappe.utils.fmt_money(d.grand_total, currency=d.currency,format=d.format)


	return data

@frappe.whitelist()
def get_current_receiveable():
	sql = """
			select 
   				sum(balance) as total_balance,
       			currency,
				format
       		from `tabSales Invoice Payment` a
			inner join `tabSales Invoice` b on a.parent= b.name
			where b.is_return = 0
          	group by currency
 		"""
	data = frappe.db.sql(sql,as_dict=1)
	for d in data:
		d.total_balance=frappe.utils.fmt_money(d.total_balance, currency=d.currency,format=d.format)
	return data

@frappe.whitelist()
def get_sales_invoice_stat(sales_invoice):
	sql="""
 			select 
    			sum(grand_total) - sum(quantity*sales_invoice_discount_rate) as grand_total,
       			currency,
          		format
          	from `tabSales Invoice Item` 
			  where parent = '{}'
           group by
			format,
           	currency
    	""".format(sales_invoice)
	data = frappe.db.sql(sql,as_dict=1)
	return data



@frappe.whitelist()
def get_recent_sale_invoice():
	

	payment =  get_recent_payment()
	data = 	get_recent_sale()
	sale_return = 	get_recent_sale_return()

	return {"sale":data,"payment":payment,"sale_return":sale_return}


def get_recent_payment():
	currencies=[]
	if frappe.cache().exists('currencies')==0:
		currencies=frappe.db.get_list('Currency',
			filters={
				'enabled': 1
			},
			fields=['number_format', 'name']
		)
		frappe.cache().set_value('currencies', currencies)
	else:
		currencies = frappe.cache().get_value('currencies')	


	payment_currencies = ', '.join([
		f"sum(if(currency='{c['name']}',a.payment_amount,0)) as {c['name']}"
		for c in currencies
	])

	sql_recent_payment="""select 
		b.name,
		b.payment_date,
		b.customer_name,
		{}
		from `tabSales Payment Currency` a
		inner join `tabSale Payment` b on b.name = a.parent
		group by
			b.name,
			b.payment_date,
			b.customer_name
		order by 
			b.creation desc
		limit 15
		""".format(payment_currencies)

	payment = frappe.db.sql(sql_recent_payment,as_dict=1)

	

	for d in payment:
		d["payment_date"] = frappe.format(d["payment_date"],{"fieldtype":"Date"})
		for currency in currencies:
			for key in d:
				if key == currency.name:
					d[key] = frappe.utils.fmt_money(d[key], currency=get_currency(key).name,format=get_currency(key).number_format)
	return payment

def get_recent_sale():

	currencies=[]
	if frappe.cache().exists('currencies')==0:
		currencies=frappe.db.get_list('Currency',
			filters={
				'enabled': 1
			},
			fields=['number_format', 'name']
		)
		frappe.cache().set_value('currencies', currencies)
	else:
		currencies = frappe.cache().get_value('currencies')	
  
	sale_currencies = ', '.join([
			f"sum(if(currency='{c['name']}',a.grand_total,0)) as {c['name']}"
			for c in currencies
	])

	sql="""select 
		b.name,
		b.sale_date,
		b.customer_name,
		{}
		from `tabSales Invoice Payment` a
		inner join `tabSales Invoice` b on b.name = a.parent
		where b.is_return = 0
		group by
			b.name,
			b.sale_date,
			b.customer
		order by 
			b.creation desc
		limit 15
		""".format(sale_currencies)
	data = frappe.db.sql(sql,as_dict=1)
	for d in data:
		d["sale_date"] = frappe.format(d["sale_date"],{"fieldtype":"Date"})
		for currency in currencies:
			for key in d:
				if key == currency.name:
					d[key] = frappe.utils.fmt_money(d[key], currency=get_currency(key).name,format=get_currency(key).number_format)
	return data

def get_recent_sale_return():
	currencies=[]
	if frappe.cache().exists('currencies')==0:
		currencies=frappe.db.get_list('Currency',
			filters={
				'enabled': 1
			},
			fields=['number_format', 'name']
		)
		frappe.cache().set_value('currencies', currencies)
	else:
		currencies = frappe.cache().get_value('currencies')	
  
	sale_currencies = ', '.join([
			f"sum(if(currency='{c['name']}',a.grand_total,0)) as {c['name']}"
			for c in currencies
	])

	sql="""select 
		b.name,
		b.sale_date as return_date,
		b.customer_name,
		{}
		from `tabSales Invoice Payment` a
		inner join `tabSales Invoice` b on b.name = a.parent
		where b.is_return = 1
		group by
			b.name,
			b.sale_date,
			b.customer
		order by 
			b.creation desc
		limit 15
		""".format(sale_currencies)
	data = frappe.db.sql(sql,as_dict=1)
	for d in data:
		d["return_date"] = frappe.format(d["return_date"],{"fieldtype":"Date"})
		for currency in currencies:
			for key in d:
				if key == currency.name:
					d[key] = frappe.utils.fmt_money(d[key], currency=get_currency(key).name,format=get_currency(key).number_format)
	return data

@frappe.whitelist()
def get_currency(name):
	currencies = frappe.cache().get_value('currencies')
	currency_filtered = [currency for currency in currencies if currency["name"] == name]
	return currency_filtered[0]

@frappe.whitelist()
def remove_cache(key):
	result = frappe.cache().delete_value(key)
	
	return result