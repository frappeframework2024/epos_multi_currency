# Copyright (c) 2023, ESTC and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from epos_multi_currency.utils import check_uom_conversion

class UnitofMeasurementConversion(Document):
	def after_insert(self):
		if not check_uom_conversion(self.unit_name,self.unit_name ):
			doc = frappe.get_doc({
				'doctype': 'Unit of Measurement Conversion',
				'from_uom':self.unit_name,
				'to_uom':self.unit_name,
				'conversion':1
			})
			doc.insert()
