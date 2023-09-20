// Copyright (c) 2023, ESTC and contributors
// For license information, please see license.txt

frappe.ui.form.on("Expense Payment", {
    refresh(frm) {
        frm.fields_dict["payments"].grid.wrapper.find('.grid-remove-rows').hide();
        frm.fields_dict["payments"].grid.wrapper.find('.grid-add-row').hide();
        frm.remove_custom_button('Duplicate');
        frm.set_query("sale_invoice", function () {
            return {
                    filters: [
                        ['status', 'in', ["Unpaid","Partly Paid"]]
                    ]
            }
        });
        if (frm.is_new()) {
            current = new Date();
            frm.set_value("payment_date", current);
        }
    },
    
    expense: function (frm) {
        frm.clear_table('payments')
        frappe.call('epos_multi_currency.expenses.doctype.expense_payment.expense_payment.get_unpaid_currency', {
            expense: frm.doc.expense
        }).then(r => {

            $.each(r.message, function (i, d) {
                frm.add_child("payments", {
                    currency: d.currency,
                    total_amount: d.total_amount,
                    paid_amount: d.paid_amount,
                    payment_amount: d.total_amount - d.paid_amount ?? 0,
                    balance: 0
                })

            });
            frm.refresh_field('payments')
        })
    }
});

frappe.ui.form.on('Expense Payment Currency', {
    payment_amount:function(frm,cdt,cdn){
        let doc=   locals[cdt][cdn];
        doc.balance = doc.total_amount - (doc.payment_amount + doc.paid_amount)
        frm.refresh_field('payments');
    }
})
