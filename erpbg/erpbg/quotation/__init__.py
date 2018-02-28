#!/usr/bin/env python
# -*- coding: utf-8 -*-

import frappe
import datetime


@frappe.whitelist()
def generate_custom_number(qname, customer):
    if not customer:
        return
    number = ""

    if len(qname) > 0:
        quotation = frappe.db.get_values("Quotation", qname, "*", as_dict=True)[0]
        if quotation.customer == customer:
            return quotation.cnumber

    quotations = frappe.db.sql(
        '''SELECT `name`,`transaction_date` FROM `tabQuotation` WHERE `customer`=%s AND `transaction_date` LIKE %s;''',
        (customer,
         str(datetime.datetime.now().strftime("%Y")) + "-" + str(datetime.datetime.now().strftime("%m")) + "%"),
        as_dict=True)

    if len(quotations) > 0:
        year_and_month = str(quotations[0].transaction_date)[0:7]
    else:
        year_and_month = datetime.datetime.now().strftime("%Y-%m")

    number_of_quotations_that_month = len(quotations) + 1
    if len(qname) > 0:
        number_of_quotations_that_month -= 1
        that_month_number = str(datetime.datetime.now().strftime("%m"))
    else:
        that_month_number = year_and_month[-2:]
    number += str(number_of_quotations_that_month).zfill(2) + that_month_number

    customer = frappe.db.get_values("Customer", customer, "*")[0]
    number += "-"
    if customer.customer_commision > 0:
        number += "90" + str(customer.customer_commision)
    elif customer.customer_commision <= 0:
        number += "01"
    if customer.customer_cnumber:
        if len(number) > 0:
            number += "-"
        number += str(customer.customer_cnumber)

    return number


@frappe.whitelist()
def make_quick_quotation(customer_name, contact_name, email, communication):

    # type check and bug fix
    if isinstance(customer_name, tuple):
        customer_name = customer_name[0]
    if isinstance(contact_name, tuple):
        contact_name = contact_name[0]
    if isinstance(email, tuple):
        email = email[0]
    if isinstance(communication, tuple):
        communication = communication[0]

    # check for existing customer
    customer = frappe.db.sql('''SELECT `name` FROM `tabCustomer` WHERE `name`=%s;''', (customer_name), as_dict=True)
    if customer:
        return "The client <b><a href='#Form/Contact/"+customer[0].name+"'>"+customer[0].name+"</a></b> is already created. As such, can not be created again."

    # create customer
    customer = frappe.new_doc("Customer")
    customer.docname = customer_name
    customer.customer_name = customer_name
    customer.save()

    # create contact
    contact = frappe.new_doc("Contact")
    contact.name = contact_name + "-" + customer_name
    contact.first_name = contact_name
    contact.last_name = ""
    contact.email_id = email
    contact.save()

    # link contact to customer
    link = frappe.get_doc(dict(
        doctype = "Dynamic Link",
        parentfield = "links",
        parenttype = "Contact",
        parent = contact.name,
        link_doctype = "Customer",
        link_name = customer.name
    ))
    link.flags.ignore_permissions = True
    link.save()

    # create quotation
    quotation = frappe.new_doc("Quotation")
    quotation.transaction_date = str(datetime.datetime.now().strftime("%Y")) + "-" + str(datetime.datetime.now().strftime("%m")) + "-" + str(datetime.datetime.now().strftime("%d"))
    quotation.flags.ignore_mandatory = True
    quotation.flags.ignore_permissions = True
    quotation.save()

    quotation.cnumber = generate_custom_number(quotation.name, customer.name)
    quotation.customer = customer.name
    quotation.save()

    frappe.db.commit()

    return [quotation.name, customer.name, contact.name]
