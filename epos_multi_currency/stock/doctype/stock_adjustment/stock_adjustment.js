// Copyright (c) 2023, ESTC and contributors
// For license information, please see license.txt

frappe.ui.form.on("Stock Adjustment", {
    onload:function(frm){
        if(frm.is_new()){
			frappe.call({
				method: "epos_multi_currency.epos_multi_currency.doctype.sales_invoice.sales_invoice.get_default_stock_location",
				args: {},
				callback: function(r){
					if(r.message != undefined){
						frm.set_value("stock_location", r.message.stock_location_name);
					}
				}
			}),
			current =new Date();
			frm.set_value("stock_adjustment_date", current);
		}
    },
    stock_location(frm){
		frm.doc.items.forEach(function(p){
			p.stock_location = frm.doc.stock_location
			frappe.call({
				method: "epos_multi_currency.epos_multi_currency.doctype.sales_invoice.sales_invoice.get_available_stock",
				args: {
					stock_location: p.stock_location,
					item_code: p.item_code ?? ""
				},
				callback: function(r){
					if(r.message != undefined){
						p.current_quantity = r.message.quantity;
						frm.refresh_field('items');
					}
				}
			})
		});
		frm.refresh_field('items'); 
	},
	search_items(frm){
		if(frm.doc.search_items!=undefined){
				let barcode = frm.doc.search_items;
				frappe.call({
					method: "epos_multi_currency.stock.doctype.stock_adjustment.stock_adjustment.get_product",
					args: {
						barcode:frm.doc.search_items,
						stock_location:frm.doc.stock_location
					},
					callback: function(r){
			if(r.message != undefined)
            {
				if(r.message.status ==0)
              	{ 
					let row_exist = check_row_exist(frm,barcode,r.message.uom);
					if(row_exist!=undefined)
                	{
						row_exist.doc.quantity = row_exist.doc.quantity + 1;
						row_exist.doc.quantity = frm.doc.is_return === 1 ? row_exist.doc.quantity * -1 : row_exist.doc.quantity;
						frm.refresh_field('items');
					}
					else 
					{
						add_product_to_sale_product(frm,r.message);
						frm.refresh_field('items');
					}
				}
              else {}
			}
			else {
				frappe.throw(_("Load data fail."))
			}
		},
		error: function(r) {
			frappe.throw(_("Load data fail."))
		},
	});			
		}
		frm.doc.search_items = "";
		frm.refresh_field('search_items');  
	},
}),
frappe.ui.form.on('Stock Adjustment Item', {
	uom(frm,cdt, cdn) {
		let doc=   locals[cdt][cdn];
		frappe.call({
			method: "epos_multi_currency.epos_multi_currency.doctype.sales_invoice.sales_invoice.get_item_uom_price",
			args: {
				item_code: doc.item_code,
				uom:doc.uom,
				stock_uom:doc.stock_uom
			},
			callback: function(r){
				if(r.message != undefined){
					frappe.call({
                        method: "epos_multi_currency.epos_multi_currency.doctype.sales_invoice.sales_invoice.get_available_stock",
                        args: {
                            stock_location: frm.doc.stock_location,
                            item_code: doc.item_code
                        },
                        callback: function(a){
                            if(r.message != undefined){
                                if(r.message.predefine == 1){
                                    doc.uom_conversion = r.message.uom_conversion
                                    doc.cost = r.message.cost;
                                    doc.whole_sale = r.message.whole_sale;
                                    doc.price = r.message.price;
                                    doc.stock_location = frm.doc.stock_location;
                                    doc.current_quantity = a.message.quantity / r.message.uom_conversion;
                                }
                                else{
                                    doc.uom_conversion = r.message.uom_conversion;
                                    doc.cost = r.message.cost * doc.uom_conversion;
                                    doc.whole_sale = r.message.whole_sale * doc.uom_conversion;
                                    doc.price = r.message.price * doc.uom_conversion;
                                    doc.stock_location = frm.doc.stock_location;
                                    doc.current_quantity =  a.message.quantity / r.message.uom_conversion;
                                }
                                frm.refresh_field('items');
                            }
                        }
                    })
				}
			}
		})
	},
	stock_location(frm,cdt, cdn) {
	let doc=   locals[cdt][cdn];
	frappe.call({
		method: "epos_multi_currency.epos_multi_currency.doctype.sales_invoice.sales_invoice.get_available_stock",
		args: {
			stock_location: doc.stock_location,
			item_code: doc.item_code
		},
		callback: function(r){
			if(r.message != undefined){
				doc.available_stock = r.message.quantity;
				frm.refresh_field('items');
			}
		}
	})
	
	},
	item(frm,cdt, cdn) {
        let doc=   locals[cdt][cdn];
		doc.uom = doc.stock_uom;
		frappe.call({
			method: "epos_multi_currency.epos_multi_currency.doctype.sales_invoice.sales_invoice.get_item_uom_price",
			args: {
				item_code: doc.item_code,
				uom:doc.uom,
				stock_uom:doc.stock_uom
			},
			callback: function(r){
				if(r.message != undefined)
				{
                    frappe.call({
                        method: "epos_multi_currency.epos_multi_currency.doctype.sales_invoice.sales_invoice.get_available_stock",
                        args: {
                            stock_location: frm.doc.stock_location,
                            item_code: doc.item_code
                        },
                        callback: function(a){
                            if(r.message != undefined){
                                if(r.message.predefine == 1){
                                    doc.uom_conversion = r.message.uom_conversion
                                    doc.cost = r.message.cost;
                                    doc.whole_sale = r.message.whole_sale;
                                    doc.price = r.message.price;
                                    doc.stock_location = frm.doc.stock_location;
                                    doc.current_quantity = a.message.quantity;
                                }
                                else{
                                    doc.uom_conversion = r.message.uom_conversion;
                                    doc.cost = r.message.cost * doc.uom_conversion;
                                    doc.whole_sale = r.message.whole_sale * doc.uom_conversion;
                                    doc.price = r.message.price * doc.uom_conversion;
                                    doc.stock_location = frm.doc.stock_location;
                                    doc.current_quantity =  a.message.quantity;
                                }
                                frm.refresh_field('items');
                            }
                        }
                    })
				}
			}
		})
    },
  });

function check_row_exist(frm, barcode,uom)
{
  var row = frm.fields_dict["items"].grid.grid_rows.filter(function(d)
      { 
        return ((d.doc.item_code==undefined?"":d.doc.item_code).toLowerCase() === barcode.toLowerCase()  && d.doc.uom === uom)
      })[0];
  return row;
}

function add_product_to_sale_product(frm,p){
	let all_rows = frm.fields_dict["items"].grid.grid_rows.filter(function(d)
	{ return  d.doc.product_code==undefined});
	
	let row =undefined;
	if (all_rows.length>0)
  {
		if ( all_rows[0].doc.item_code == undefined)
    { 
			row = all_rows[0];
		}
	}
	let doc = undefined;
	if(row==undefined)
  {
		 doc = frm.add_child("items");
	}
  else 
  {
		doc = row.doc;
	}
	if(doc!=undefined){
    	doc.item =  p.item_code;
		doc.item_code = p.item_code;
		doc.item_name = p.item_name;
        doc.cost = p.cost;
        doc.whole_sale = p.whole_sale;
		doc.price = p.price;
		doc.quantity = 1;
		doc.uom = p.uom;
        doc.stock_uom = p.uom;
		doc.currency = p.currency;
		doc.stock_location = frm.doc.stock_location;
		doc.uom_conversion = 1;
		doc.current_quantity = p.available_stock;
		frm.refresh_field('items');
	}
}