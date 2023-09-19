frappe.pages['page-report'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Reports',
		single_column: true
	});
	$(frappe.render_template("page_report")).appendTo(page.body.addClass("no-border"));
};