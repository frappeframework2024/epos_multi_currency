app_name = "epos_multi_currency"
app_title = "ePos Multi Currency"
app_publisher = "ESTC"
app_description = "ePos Multi Currency"
app_email = "estc@mail.com"
app_license = "MIT"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/epos_multi_currency/css/epos_multi_currency.css"
# app_include_js = "/assets/epos_multi_currency/js/epos_multi_currency.js"

# include js, css files in header of web template
# web_include_css = "/assets/epos_multi_currency/css/epos_multi_currency.css"
# web_include_js = "/assets/epos_multi_currency/js/epos_multi_currency.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "epos_multi_currency/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "epos_multi_currency.utils.jinja_methods",
#	"filters": "epos_multi_currency.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "epos_multi_currency.install.before_install"
# after_install = "epos_multi_currency.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "epos_multi_currency.uninstall.before_uninstall"
# after_uninstall = "epos_multi_currency.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "epos_multi_currency.utils.before_app_install"
# after_app_install = "epos_multi_currency.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "epos_multi_currency.utils.before_app_uninstall"
# after_app_uninstall = "epos_multi_currency.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "epos_multi_currency.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"epos_multi_currency.tasks.all"
#	],
#	"daily": [
#		"epos_multi_currency.tasks.daily"
#	],
#	"hourly": [
#		"epos_multi_currency.tasks.hourly"
#	],
#	"weekly": [
#		"epos_multi_currency.tasks.weekly"
#	],
#	"monthly": [
#		"epos_multi_currency.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "epos_multi_currency.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "epos_multi_currency.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "epos_multi_currency.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["epos_multi_currency.utils.before_request"]
# after_request = ["epos_multi_currency.utils.after_request"]

# Job Events
# ----------
# before_job = ["epos_multi_currency.utils.before_job"]
# after_job = ["epos_multi_currency.utils.after_job"]

# User Data Protection
# --------------------
website_context = {
    "js": [
        "/assets/epos_multi_currency/js/custom_report_view.js",
    ]
}
# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"epos_multi_currency.auth.validate"
# ]
login_page = "www/login.html"
fixtures = [
    {"dt": "Workspace","filters": [["module", "in", ["ePos Multi Currency","Reports","Expenses","Stock","HR"]]]},
    {"dt": "Custom HTML Block"},
    {"dt": "ePos Multi Currency Report"},
    {"dt": "Client Script"},
    {"dt": "Report","filters": [["module", "=", "Reports"]]},
    {"dt": "Print Format","filters": [["module", "=", "ePos Multi Currency"]]}
]

