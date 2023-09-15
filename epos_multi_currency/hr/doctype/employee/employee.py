# Copyright (c) 2023, ESTC and contributors
# For license information, please see license.txt

import base64
import frappe
from frappe.model.document import Document

class Employee(Document):
	def validate(self):
		if self.password:
			self.pos_pin_code = str( base64.b64encode(self.password.encode("utf-8")).decode("utf-8"))

	def on_update(self):
		
		 
		if self.allow_login:
			if self.user_id:
				
				doc = frappe.get_doc("User", self.user_id)
				doc.enabled = 1
				doc.username = self.username
				doc.first_name = self.employee_name
				doc.role_profile_name = self.role_profile
				doc.module_profile = self.module_profile
				doc.user_image = self.photo
				
				if self.password:
					doc.new_password = self.password

				
				doc.save()
				
				if self.password:
					self.password = None
					self.save()
			else:
				doc = frappe.get_doc({
						"doctype":"User",
						"enabled": 1,
						"email": "{}@mail.com".format(self.username),
						"first_name": self.employee_name,
						"username": self.username,
						"language": "en",
						"time_zone": "Asia/Phnom_Penh",
						"send_welcome_email": 0,
						"role_profile_name": self.role_profile,
						"module_profile": self.module_profile,
						"user_type": "System User",
						"new_password":self.password,
						"user_image" : self.photo
						
					}
				).insert()

				self.password = None
				self.user_id = doc.name
				self.save()


		else:
			if self.user_id:
				doc = frappe.get_doc("User", self.user_id)
				doc.enabled = 0
				doc.save()

	def on_trash(self):
		frappe.throw("delete me")
