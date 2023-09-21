// Copyright (c) 2023, ESTC and contributors
// For license information, please see license.txt

frappe.ui.form.on("Stock Payment", {
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
        if (frm.doc.item) {
            // console.log(frm.doc.item)
        }
        
    },
    
    stock_in: function (frm) {
        frm.clear_table('payments')
        frappe.call('epos_multi_currency.stock.doctype.stock_payment.stock_payment.get_unpaid_currency', {
            stock_in: frm.doc.stock_in
        }).then(r => {

            $.each(r.message, function (i, d) {
                frm.add_child("payments", {
                    currency: d.currency,
                    grand_total: d.grand_total,
                    paid_amount: d.paid_amount,
                    payment_amount: d.grand_total - d.paid_amount,
                    balance: 0,
                    sale_invoice: frm.doc.sale_invoice
                })

            });
            frm.refresh_field('payments')
        })
    }
});

frappe.ui.form.on('Stock Payment Currency', {
    payment_amount:function(frm,cdt,cdn){
        let doc=   locals[cdt][cdn];
        doc.balance = doc.grand_total - (doc.payment_amount + doc.paid_amount)
        frm.refresh_field('payments');
    }
})
