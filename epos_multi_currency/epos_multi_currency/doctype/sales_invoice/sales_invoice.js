// Copyright (c) 2023, ESTC and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Invoice", {
	refresh:function(frm) {
		frm.add_custom_button(__('Reload'), function() {
			frm.reload_doc()
		});
		if (frm.doc.docstatus == 1 && frm.doc.status != "Paid") {
			frm.add_custom_button(__('Payment'), function() {
				frappe.new_doc('Sale Payment', {
					sale_invoice:frm.doc.name
				})
			}, __('Create'));
		}
	},
	onload: function(frm) {
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
			frm.set_value("sale_date", current);
			frm.set_value("sale_time", current.getHours()+":"+current.getMinutes()+":"+current.getSeconds());
		}else{
			frappe.call({
				type: "GET",
				method: "epos_multi_currency.utils.get_sales_invoice_stat",
				args: { "sales_invoice": frm.doc.name },
				callback: function (r) {
					r.message.forEach(element => {
						frm.dashboard.add_indicator(__('{1} : {0}', [format_currency(element.grand_total,element.currency),element.currency,element.symbol]), 'green')
						
					});
					
				}
			})
		}
	},
	after_save(frm){
		frm.reload_doc()
	},
	search_items(frm){
		if(frm.doc.search_items!=undefined){
				let barcode = frm.doc.search_items;
				frappe.call({
					method: "epos_multi_currency.epos_multi_currency.doctype.sales_invoice.sales_invoice.get_product",
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
						update_item(row_exist.doc,frm);
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
	discount_percent(frm){
		frm.doc.sales_invoice_payment.forEach(function(p){
			p.discount_amount = p.total_amount * frm.doc.discount_percent/100
			check_payment_discount(p)
		});
		frm.refresh_field('sales_invoice_payment'); 
	},
	stock_location(frm){
		frm.doc.items.forEach(function(p){
			p.stock_location = frm.doc.stock_location
			frappe.call({
				method: "epos_multi_currency.epos_multi_currency.doctype.sales_invoice.sales_invoice.get_available_stock",
				args: {
					stock_location: p.stock_location,
					item_code: p.item_code
				},
				callback: function(r){
					if(r.message != undefined){
						p.available_stock = r.message.quantity;
						frm.refresh_field('items');
					}
				}
			})
		});
		frm.refresh_field('items'); 
	},
	is_return:function(frm){
		var df = frappe.meta.get_docfield("Sales Invoice Payment","paid_amount", cur_frm.doc.name);
    	df.read_only = 1;
		frm.refresh_field(sales_invoice_payment)
	}
});


frappe.ui.form.on('Sales Invoice Item', {
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
					if(r.message.predefine == 1){
						doc.uom_conversion = r.message.uom_conversion
						doc.cost = r.message.cost;
						doc.whole_sale = r.message.whole_sale;
						doc.base_price = r.message.price;
						doc.price = r.message.price;
						doc.stock_location = frm.doc.stock_location
					}
					else{
						doc.uom_conversion = r.message.uom_conversion;
						doc.cost = r.message.cost * doc.uom_conversion;
						doc.whole_sale = r.message.whole_sale * doc.uom_conversion;
						doc.base_price = r.message.price * doc.uom_conversion;
						doc.price = r.message.price * doc.uom_conversion;
						doc.stock_location = frm.doc.stock_location
					}
				
					update_item(doc,frm);
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
    quantity(frm,cdt, cdn) {
      let doc=   locals[cdt][cdn];
	  update_item(doc,frm);
    },
    price(frm,cdt, cdn) {
		let doc=   locals[cdt][cdn];
		update_item(doc,frm);
	},
	discount(frm,cdt, cdn) {
		let doc=   locals[cdt][cdn];
		update_item(doc,frm)
	},
	discount_type(frm,cdt, cdn) {
        let doc=   locals[cdt][cdn];
        doc.discount = 0;
		doc.discount_amount=0;
		doc.grand_total = (doc.sub_total || 0) - (doc.discount_amount || 0);
        frm.refresh_field('items');
    },
	is_free_item(frm,cdt, cdn) {
        let doc=   locals[cdt][cdn];
		doc.discount_type = "Percent"
        if(doc.is_free_item == 1){
			doc.discount = 100;
		}
		else{
			doc.discount = 0;
		}
		doc.discount_amount = (doc.sub_total * doc.discount/100);
		doc.grand_total = doc.sub_total - (doc.discount_amount || 0);
        frm.refresh_field('items');
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
					if(r.message.predefine == 1){
						doc.uom_conversion = r.message.uom_conversion
						doc.cost = r.message.cost;
						doc.whole_sale = r.message.whole_sale;
						doc.base_price = r.message.price;
						doc.price = r.message.price;
						doc.stock_location = frm.doc.stock_location;
						doc.quantity = frm.doc.is_return === 1 ? -1 : 1 
					}
					else{
						doc.uom_conversion = r.message.uom_conversion;
						doc.cost = r.message.cost * doc.uom_conversion;
						doc.whole_sale = r.message.whole_sale * doc.uom_conversion;
						doc.base_price = r.message.price * doc.uom_conversion;
						doc.price = r.message.price * doc.uom_conversion;
						doc.stock_location = frm.doc.stock_location;
						doc.quantity = frm.doc.is_return === 1 ? -1 : 1 ;
					}
					update_item(doc,frm);
				}
			}
		})
        frm.refresh_field('items');
    },
  });
frappe.ui.form.on('Sales Invoice Payment', {
	currency(frm,cdt, cdn) {
        let doc=   locals[cdt][cdn];
		frappe.call({
			method: "epos_multi_currency.epos_multi_currency.doctype.sales_invoice.sales_invoice.get_currency_total_amount",
			args: {
				pcurrency: doc.currency,
				items:frm.doc.items
			},
			callback: function(r){
				if(r.message != undefined){
					doc.total_amount = r.message.total_amount;
					doc.grand_total = doc.total_amount - (doc.discount_amount - doc.write_off_amount)
					doc.balance = doc.grand_total - doc.paid_amount
					frm.refresh_field('sales_invoice_payment');
				}
			}
		})
    },
	discount_amount(frm,cdt, cdn) {
        let doc=   locals[cdt][cdn];
		check_payment_discount(doc)
		frm.refresh_field('sales_invoice_payment');
	},
	write_off_amount(frm,cdt, cdn) {
        let doc=   locals[cdt][cdn];
		doc.grand_total = doc.total_amount - (doc.discount_amount + doc.write_off_amount)
		doc.balance = doc.grand_total  - doc.paid_amount
		frm.refresh_field('sales_invoice_payment');
	},
	paid_amount(frm,cdt, cdn) {
        let doc=   locals[cdt][cdn];
		doc.grand_total = doc.total_amount - (doc.discount_amount + doc.write_off_amount)
		doc.balance = doc.grand_total - doc.paid_amount
		frm.refresh_field('sales_invoice_payment');
	}
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
		doc.price = p.price;
		doc.base_price = p.price;
		doc.quantity = frm.doc.is_return === 1 ? -1 : 1;
		doc.uom = p.uom;
		doc.stock_uom = p.uom;
		doc.uom_list = p.uom_list
		doc.allow_free = p.allow_free ;
		doc.allow_discount = p.allow_discount;
		doc.currency = p.currency;
		doc.stock_location = frm.doc.stock_location;
		doc.uom_conversion = 1
		doc.cost = p.cost
		doc.available_stock = p.available_stock
		update_item(doc,frm);
	}
}

function update_item(doc,frm){
	doc.sub_total = doc.quantity * doc.price;
	if(doc.allow_discount == 1){
		if (doc.discount_type == "Percent")
		{
			doc.discount_amount = (doc.sub_total * doc.discount/100); 
		}
		else
		{
			doc.discount_amount = doc.discount;
		}
	}
	else{
		frappe.show_alert({message:"Item not allow to discount", indicator:"orange"});
		doc.discount = 0
	}
	doc.grand_total = doc.sub_total - (doc.discount_amount || 0);
	frm.refresh_field('items');
}

function check_payment_discount(doc){
	if(doc.discountable_amount == 0 && doc.discount_amount > 0){
		frappe.show_alert({message:"Payment "+ doc.currency +" can't be discount", indicator:"orange"});
		doc.discount_amount = 0
	}
	else if(doc.discountable_amount<doc.discount_amount){
		doc.discount_amount = doc.discountable_amount
	}
	else{
		
	}
	doc.grand_total = doc.discountable_amount - (doc.discount_amount + doc.write_off_amount)
	doc.balance = doc.grand_total - doc.paid_amount
}