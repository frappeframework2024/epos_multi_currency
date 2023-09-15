# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	return get_columns(filters),get_report_data(filters)

def get_filters(filters):
	data= "b.docstatus=1 and b.sale_date between '{}' AND '{}'".format(filters.start_date,filters.end_date)
	if filters.get("branch"):data = data +	" and b.branch in (" + get_list(filters,"branch") + ")"
	return data

def get_columns(filters):
	columns = []
	columns.append({'fieldname':'sale_date','label':"Sale Date",'fieldtype':'Date','align':'center','width':150})
	columns.append({'fieldname':'transaction','label':"Transactions",'fieldtype':'Data','align':'center','width':110})
	columns.append({'fieldname':'quantity','label':"Quanity",'fieldtype':'Data','align':'center','width':100})
	columns.append({'fieldname':'cost','label':"Cost",'fieldtype':'Data','align':'right','width':130})
	columns.append({'fieldname':'grand_total','label':"Grand Total",'fieldtype':'Data','align':'right','width':130})
	columns.append({'fieldname':'profit','label':"Profit",'fieldtype':'Data','align':'right','width':130})
	return columns

def get_report_data(filters):
	data=[]
	
	parent = """
				SELECT 
					b.sale_date,
					count(distinct a.parent) transaction,
					sum(a.quantity) quantity
				FROM `tabSales Invoice Item` a
					INNER JOIN `tabSales Invoice` b ON b.name = a.parent
				WHERE {}
					GROUP BY b.sale_date
			""".format(get_filters(filters))
	parent_data = frappe.db.sql(parent,as_dict=1)
	for dic_p in parent_data:
		dic_p["indent"] = 0
		dic_p["is_group"] = 1
		data.append(dic_p)
		child_data = ("""
						SELECT 
							sum(a.quantity) quantity,
							concat(format(SUM(a.cost),2),' ',a.symbol) cost,
							concat(format(sum(a.grand_total) - sum(a.sales_invoice_discount_rate * a.quantity) - sum(a.sales_invoice_write_off_rate * a.quantity),2),' ',a.symbol) grand_total,
							concat(format(sum(a.grand_total) - sum(a.sales_invoice_discount_rate * a.quantity) - sum(a.sales_invoice_write_off_rate * a.quantity) - SUM(a.cost),2),' ',a.symbol) profit
						FROM `tabSales Invoice Item` a
						INNER JOIN `tabSales Invoice` b ON b.name = a.parent
						where b.sale_date = '{}'  and b.docstatus = 1
						GROUP BY b.sale_date,a.currency,a.symbol
					""".format(dic_p["sale_date"]))
		child = frappe.db.sql(child_data,as_dict=1)
		for dic_c in child:
			dic_c["indent"] = 1
			dic_c["is_group"] = 0
			data.append(dic_c)
	return data

def get_list(filters,name):
	data = ','.join("'{0}'".format(x.replace("'", "''")) for x in filters.get(name))
	return data