frappe.pages['page-report-1'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Reports',
		single_column: true
	});
}