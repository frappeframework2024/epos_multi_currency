// Copyright (c) 2023, ESTC and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Invoice", {
	search_items(frm){
		if(frm.doc.search_items!=undefined){
				let barcode = frm.doc.search_items;
				frappe.call({
					method: "epos_multi_currency.epos_multi_currency.doctype.sales_invoice.sales_invoice.get_product",
					args: {
						barcode:frm.doc.search_items
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
									update_sale_product_amount(frm,row_exist.doc);
								}
                else 
                {
									add_product_to_sale_product(frm,r.message);
								}
								frm.refresh_field("items");
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
});


frappe.ui.form.on('Sales Invoice Item', {
    quantity(frm,cdt, cdn) {
      let doc=   locals[cdt][cdn];
      doc.sub_total = doc.quantity*doc.price;
      frm.refresh_field('items');
    },
    price(frm,cdt, cdn) {
        let doc=   locals[cdt][cdn];
        doc.sub_total = doc.quantity*doc.price;
        frm.refresh_field('items');
      }
  })
function check_row_exist(frm, barcode,uom){

  var row = frm.fields_dict["items"].grid.grid_rows.filter(function(d)
      { 
        return ((d.doc.item_code==undefined?"":d.doc.item_code).toLowerCase() === barcode.toLowerCase()  && d.doc.uom === uom)
      })[0];
  return row;
}
function update_sale_product_amount(frm,doc){
 
	doc.amount = doc.quantity * doc.price;

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
		doc.quantity = 1;
		doc.uom = p.uom;
		doc.allow_free = p.allow_free ;
		doc.allow_discount = p.allow_discount;
    doc.currency = p.currency;
    doc.sub_total = doc.quantity * p.price;
    if (doc.discount_type == "Percent")
    {
			doc.discount_amount = (doc.sub_total * doc.discount/100); 
		}
    else
    {
			doc.discount_amount = doc.discount;
		}
    doc.amount = (doc.sub_total || 0) - (doc.discount_amount || 0);
	}
	
}