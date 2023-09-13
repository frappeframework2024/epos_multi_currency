frappe.listview_settings['Stock In'] = {
	get_indicator: function(doc) {
		const status_colors = {
			"Draft": "grey",
			"Unpaid": "orange",
			"Paid": "green",
			"Return": "gray",
			"Partly Paid": "yellow",
		};
		return [__(doc.status), status_colors[doc.status], "status,=,"+doc.status];
	}
};