// Copyright (c) 2023, ESTC and contributors
// For license information, please see license.txt

frappe.ui.form.on("Inventory Transaction", {
	refresh(frm) {
        frm.add_custom_button('Product', () => {
            frappe.set_route('product', frm.doc.item_code);
        })
	},
});