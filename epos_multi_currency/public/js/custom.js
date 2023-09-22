frappe.ui.form.on('Login', {
    onload: function(frm) {
        console.log(222)
        // Hide the "Forgot Password?" link
        frm.fields_dict['forgot_password'].wrapper.style.display = 'none';
    }
});