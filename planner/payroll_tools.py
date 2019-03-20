# -*- coding: utf-8 -*-
# Copyright (c) 2017-2018, libracore and contributors
# License: AGPL v3. See LICENCE

from __future__ import unicode_literals
import frappe
from erpnext.hr.doctype.leave_application.leave_application import get_leave_balance_on
import json

@frappe.whitelist()
def get_sal_slip_list(start_date, end_date, ss_status=0, as_dict=True):
	"""
		Returns list of salary slips based on selected criteria
	"""
	# cond = self.get_filter_condition()

	# ss_list = frappe.db.sql("""
		# select t1.name, t1.salary_structure from `tabSalary Slip` t1
		# where t1.docstatus = %s and t1.start_date >= %s and t1.end_date <= %s
		# and (t1.journal_entry is null or t1.journal_entry = "") and ifnull(salary_slip_based_on_timesheet,0) = %s %s
	# """ % ('%s', '%s', '%s','%s', cond), (ss_status, self.start_date, self.end_date, self.salary_slip_based_on_timesheet), as_dict=as_dict)
	# frappe.throw(ss_list)
	# return ss_list
	
	ss_list_draft = frappe.db.sql("""SELECT
									t1.name,
									t1.salary_structure,
									t1.employee
								FROM `tabSalary Slip` AS t1
								WHERE t1.docstatus = 0
								AND t1.start_date >= '{start_date}'
								AND t1.end_date <= '{end_date}'
								AND (t1.journal_entry is null OR t1.journal_entry = '')""".format(start_date=start_date, end_date=end_date), as_dict=as_dict)
								
	ss_list_submitted = frappe.db.sql("""SELECT
									t1.name,
									t1.salary_structure,
									t1.employee
								FROM `tabSalary Slip` AS t1
								WHERE t1.docstatus = 1
								AND t1.start_date >= '{start_date}'
								AND t1.end_date <= '{end_date}'
								AND (t1.journal_entry is null OR t1.journal_entry = '')""".format(start_date=start_date, end_date=end_date), as_dict=as_dict)
								
	return {'draft': ss_list_draft, 'submitted': ss_list_submitted}
	
	
@frappe.whitelist()
def increment_salary(start_date, end_date, salary_structure, posting_date, ss_status=0, as_dict=True):
	emp_list = frappe.db.sql("""SELECT
									t1.employee
								FROM `tabSalary Slip` AS t1
								WHERE t1.docstatus = 0
								AND t1.start_date >= '{start_date}'
								AND t1.end_date <= '{end_date}'
								AND (t1.journal_entry is null OR t1.journal_entry = '')
								AND t1.salary_structure = '{salary_structure}'""".format(ss_status=ss_status, start_date=start_date, end_date=end_date, salary_structure=salary_structure), as_dict=as_dict)
	
	for _emp in emp_list:
		emp = frappe.get_doc('Employee', _emp.employee)
		ml = emp.monatslohn
		zml = emp.zusatz_monatslohn
		
		update = frappe.db.sql("""UPDATE `tabEmployee` SET `zusatz_monatslohn` = '{new_zml}' WHERE `name` = '{name}'""".format(new_zml=(zml + (ml / 12)), name=emp.name), as_list=True)
	
	return 'ok'
	
@frappe.whitelist()
def update_leave_balance(employees, posting_date):
	if isinstance(employees, basestring):
		employees = json.loads(employees)
	for emp in employees:
		leave_balance = get_leave_balance_on(employee=emp, date=posting_date, leave_type='Bevorzugter Urlaub', consider_all_leaves_in_the_allocation_period=True)
		update = frappe.db.sql("""UPDATE `tabEmployee` SET `leave_balance` = '{leave_balance}' WHERE `name` = '{name}'""".format(name=emp, leave_balance=leave_balance), as_list=True)
		
	return True
	