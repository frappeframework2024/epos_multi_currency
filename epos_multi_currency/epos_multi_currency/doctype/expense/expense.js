// Copyright (c) 2023, ESTC and contributors
// For license information, please see license.txt
frappe.ui.form.on("Expense", {
    refresh:function(frm) {
		frm.add_custom_button(__('Reload'), function() {
			frm.reload_doc()
		});
		if (frm.doc.docstatus == 1 && frm.doc.status != "Paid") {
			frm.add_custom_button(__('Payment'), function() {
				frappe.new_doc('Expense Payment', {
					expense:frm.doc.name
				})
			}, __('Create'));
		}
	},
}),
frappe.ui.form.on("Expense Item", {
    expense(frm,cdn,cdt){
        let doc = locals[cdt][cdn];
        doc.amount = doc.quantity * doc.price
        frm.refresh_field("expense_items")
    },
	quantity(frm,cdt, cdn) {
		let doc = locals[cdt][cdn];
        doc.amount = doc.quantity * doc.price
        frm.refresh_field("expense_items")
	},
    price(frm,cdt, cdn) {
		let doc = locals[cdt][cdn];
        doc.amount = doc.quantity * doc.price
        frm.refresh_field("expense_items")
	},
});
