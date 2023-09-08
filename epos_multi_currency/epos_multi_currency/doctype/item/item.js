// Copyright (c) 2023, ESTC and contributors
// For license information, please see license.txt

frappe.ui.form.on("Item", {
	onload(frm) {
        frm.toggle_display("stock_location_item", !frm.is_new()); 
	},
});
