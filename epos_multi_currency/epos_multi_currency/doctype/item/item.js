// Copyright (c) 2023, ESTC and contributors
// For license information, please see license.txt

frappe.ui.form.on("Item", {
	refresh:function(frm){
		frm.fields_dict["stock_location_item"].grid.wrapper.find('.grid-remove-rows').hide();
	},
});
