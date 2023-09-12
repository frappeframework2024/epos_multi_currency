# Copyright (c) 2023, ESTC and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Staff(Document):
	def on_update(self):
		self.full_name = self.first_name + " " + self.last_name	
