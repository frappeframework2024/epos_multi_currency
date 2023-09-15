// Copyright (c) 2023, ESTC and contributors
// For license information, please see license.txt

frappe.ui.form.on("Stock Transfer", {
	onload(frm) {
        if (frm.is_new()){
            if (frm.is_new()) {
                current = new Date();
                frm.set_value("transfer_date", current);
            }
        }
	},
    after_save(frm){
		frm.reload_doc()
	},
    branch:function(frm){
        frm.doc.source_stock_location=''
        frm.doc.target_stock_location=''
        frm.set_query("source_stock_location", function() {
			return {
				filters: {
				    branch: frm.doc.branch,
				}
			};
		});
        frm.set_query("target_stock_location", function() {
			return {
				filters: {
				    branch: frm.doc.branch,
					
				}
			};
		});
        frm.refresh_field('target_stock_location')
        frm.refresh_field('source_stock_location')
    },
    search_items(frm) {
		if (frm.doc.search_items != undefined) {
			let barcode = frm.doc.search_items;
			frappe.call({
				method: "epos_multi_currency.utils.get_product_by_barcode",
				args: {
					barcode: frm.doc.search_items
				},
				callback: function (r) {
					if (r.message != undefined) {
						if (r.message.status == 200) {
							let row_exist = check_row_exist(frm, barcode, r.message.uom);
							if (row_exist != undefined) {
								row_exist.doc.quantity = row_exist.doc.quantity + 1;
								update_item(row_exist.doc, frm);
								frm.refresh_field('items');
							}
							else {
								add_product_to_sale_product(frm, r.message);
								frm.refresh_field('items');
							}
						}
						else {
							frappe.show_alert({
								message: __(r.message.message),
								indicator: 'orange'
							}, 5);
						}
					}
					else {
						frappe.show_alert({
							message: __(r.message.message),
							indicator: 'orange'
						}, 5);

					}
				},
				error: function (r) {
					frappe.show_alert({
						message: __('Load data fail.'),
						indicator: 'red'
					}, 5);
				},
			});
		}
		frm.doc.search_items = "";
		frm.refresh_field('search_items');
	},
});

frappe.ui.form.on('Stock Transfer Item', {
	uom(frm, cdt, cdn) {
		let doc = locals[cdt][cdn];
		if (doc.item && doc.uom) {
			frappe.call({
				method: "epos_multi_currency.utils.get_item_uom_price",
				args: {
					item_code: doc.item,
					uom: doc.uom,
					stock_uom:doc.stock_uom
				},
				callback: function (r) {
					if (r.message != undefined) {
						if(r.message.predefine == 1){
							doc.uom_conversion = r.message.uom_conversion
							doc.cost = r.message.cost;
							doc.stock_location = frm.doc.stock_location
						}
						else{
							doc.uom_conversion = r.message.uom_conversion;
							doc.cost = r.message.cost * doc.uom_conversion;
							doc.stock_location = frm.doc.stock_location
						}
					
						update_item(doc,frm);
					}
				}
			})
		}

	},
	source_stock_location(frm, cdt, cdn) {
		let doc = locals[cdt][cdn];
		frappe.call({
			method: "epos_multi_currency.utils.get_available_stock",
			args: {
				stock_location: doc.source_stock_location,
				item_code: doc.item
			},
			callback: function (r) {
				if (r.message != undefined) {
					doc.available_stock = r.message.quantity;
					frm.refresh_field('items');
				}
			}
		})
	},
    target_stock_location(frm, cdt, cdn) {
		let doc = locals[cdt][cdn];
		frappe.call({
			method: "epos_multi_currency.utils.get_available_stock",
			args: {
				stock_location: doc.target_stock_location,
				item_code: doc.item
			},
			callback: function (r) {
				if (r.message != undefined) {
					doc.available_stock = r.message.quantity;
					frm.refresh_field('items');
				}
			}
		})
	},
	quantity(frm, cdt, cdn) {
		let doc = locals[cdt][cdn];
		update_item(doc, frm);
	},

	item(frm, cdt, cdn) {
		let doc = locals[cdt][cdn];
		frappe.call({
			method: "epos_multi_currency.utils.get_item_uom_price",
			args: {
				item_code: doc.item,
				uom: doc.uom,
				stock_uom:doc.stock_uom
			},
			callback: function (r) {
				if (r.message != undefined) {
					doc.cost = r.message.cost;
					doc.whole_sale = r.message.whole_sale;
					doc.stock_location = frm.doc.stock_location,
					doc.uom_conversion = r.message.uom_conversion
					update_item(doc, frm);
				}
			}
		})
		frm.refresh_field('items');
	},

})

function add_product_to_sale_product(frm, p) {
	let all_rows = frm.fields_dict["items"].grid.grid_rows.filter(function (d) { return d.doc.item == undefined });

	let row = undefined;
	if (all_rows.length > 0) {
		if (all_rows[0].doc.item_code == undefined) {
			row = all_rows[0];
		}
	}
	let doc = undefined;
	if (row == undefined) {
		doc = frm.add_child("items");
	}
	else {
		doc = row.doc;
	}
	if (doc != undefined) {
		doc.item = p.item_code;
		doc.item_code = p.item_code;
		doc.item_name = p.item_name;
		doc.cost = p.cost;
		doc.uom_conversion = p.uom_conversion,
		doc.quantity = 1;
		doc.uom = p.uom;
		doc.stock_uom = p.uom;
		doc.uom_list = p.uom_list
		doc.allow_free = p.allow_free;
		doc.allow_discount = p.allow_discount;
		doc.currency = p.currency;
		doc.stock_location = frm.doc.stock_location
		update_item(doc, frm);
	}
}
function update_item(doc, frm) {
	doc.sub_total = doc.quantity * doc.cost;
	if (doc.discount_type == "Percent") {
		doc.discount_amount = (doc.sub_total * doc.discount / 100);
	}
	else {
		doc.discount_amount = doc.discount;
	}
	doc.grand_total = doc.sub_total - (doc.discount_amount || 0);
	frm.refresh_field('items');
}
function check_row_exist(frm, barcode, uom) {
	var row = frm.fields_dict["items"].grid.grid_rows.filter(function (d) {
		return ((d.doc.item_code == undefined ? "" : d.doc.item_code).toLowerCase() === barcode.toLowerCase() && d.doc.uom === uom)
	})[0];
	return row;
}
