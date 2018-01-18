#!/usr/bin/env python
# -*- coding: utf-8 -*-

import frappe
import json
from frappe import _


@frappe.whitelist()
def get_bomed_items(sales_order_name):
    '''Returns items with BOM that already do not have a linked Sales Order'''
    items = []
    sales_order_items = frappe.db.sql("""SELECT * FROM `tabSales Order Item` WHERE `parent`=%s""", (sales_order_name), as_dict=True)

    for item in sales_order_items:
        bom = get_default_bom_item_object(str(item["item_code"]))
        if bom:
            items.append(dict(
                item_code=str(item["item_code"]),
                sales_order=sales_order_name,
                warehouse=str(item["warehouse"])
            ))
    return items


def get_default_bom_item_object(item_code):
    bom = frappe.get_all('BOM', dict(item=item_code, is_active=True),
                         order_by='is_default desc')
    bom = bom[0].name if bom else None
    return bom


@frappe.whitelist()
def make_boms(items, sales_order, company):
    '''Make BOMs against the given Sales Order for the given `items`'''
    items = json.loads(items).get('items')
    out = []

    for i in items:
        if not i.get("qty"):
            frappe.throw(_("Please select Qty against item {0}").format(i.get("item_code")))

        bom = frappe.new_doc("BOM")
        bom.item = i['item_code']
        bom.quantity = i['qty']
        bom.company = company
        bom.sales_order = sales_order
        bom.fg_warehouse = 'Stores - DD'
        bom.append("items", {
            'item_code': '-15',
            'qty': 1,
            'conversion_factor': 1.0,
            'rate': 0.000001,
            'amount': 1
        })

        bom.ignore_permissions = True
        bom.insert()
        bom.save()
        bom.submit()

        out.append(bom)

    return [p.name for p in out]


@frappe.whitelist()
def get_sales_order_item(item_code, sales_order):
    soi = frappe.db.sql("""SELECT * FROM `tabSales Order Item` WHERE `item_code`=%s AND `parent`=%s""", (item_code, sales_order), as_dict=True)
    return soi[0]


@frappe.whitelist()
def get_quotation_attachments(quotation_name, sales_order_name):
    existing_attachments = frappe.db.sql("""SELECT * FROM `tabFile` WHERE `attached_to_doctype`='Sales Order' AND `attached_to_name`=%s""", (sales_order_name), as_dict=True)
    if len(existing_attachments) > 0:
        return False

    qattachments = frappe.db.sql("""SELECT * FROM `tabFile` WHERE `attached_to_doctype`='Quotation' AND `attached_to_name`=%s""", (quotation_name), as_dict=True)
    sattachments = []
    for qattachment in qattachments:
        sattachment = frappe.new_doc("File")
        sattachment.update(qattachment)
        sattachment.attached_to_name = sales_order_name
        sattachment.attached_to_doctype = "Sales Order"
        sattachment.save(ignore_permissions=True)
        sattachments.append(sattachment)
        frappe.db.commit()
    return sattachments


def divan_pillow_collection(item, number):
    html = ""

    space = False
    if item["divan_pcollection_" + str(number) + "_name"]:
        html += " " + item["divan_pcollection_" + str(number) + "_name"]
        space = True

    if item["divan_pcollection_" + str(number) + "_name"]:
        if space:
            html += ", "
        else:
            html += " "
            space = True
        html += u"Размер " + item["divan_pcollection_" + str(number) + "_size"]

    if item["divan_pcollection_" + str(number) + "_supplier"]:
        if space:
            html += ", "
        else:
            html += " "
            space = True
        html += u"Доставчик: " + item["divan_pcollection_" + str(number) + "_supplier"]

    if item["divan_pcollection_" + str(number) + "_damaska_color"]:
        if space:
            html += ", "
        else:
            html += " "
            space = True
        html += u"Дамаска цвят: " + item["divan_pcollection_" + str(number) + "_damaska_color"]

    if item["divan_pcollection_" + str(number) + "_quantity"]:
        if space:
            html += ", "
        else:
            html += " "
            space = True
        html += u"Дамаска количество: " + item["divan_pcollection_" + str(number) + "_quantity"]

    if item["divan_pcollection_" + str(number) + "_number"]:
        if space:
            html += ", "
        else:
            html += " "
            space = True
        html += str(item["divan_pcollection_" + str(number) + "_number"]) + u" броя"

    return html


def collection(item, number):
    html = ""

    space = False
    if item["name_" + str(number)]:
        html += " " + item["name_" + str(number)]

    if item["purpose_" + str(number)]:
        if space:
            html += " "
        else:
            html += " "
            space = True
        html += u"(приложение - " + item["purpose_" + str(number)] + ")"

    if item["color_" + str(number)]:
        if space:
            html += ", "
        else:
            html += " "
            space = True
        html += u"Цвят: " + item["color_" + str(number)]

    if item["supplier_" + str(number)]:
        if space:
            html += ", "
        else:
            html += " "
            space = True
        html += u"Доставчик: " + item["supplier_" + str(number)]

    if item["quantity_" + str(number)]:
        if space:
            html += ", "
        else:
            html += " "
            space = True
        html += item["quantity_" + str(number)] + u" броя"

    return html


@frappe.whitelist()
def make_report(names):
    import json
    if names[0] != "[":
        names = [names]
    else:
        names = json.loads(names)

    print ""
    print ""

    html = "<html><head><title>Print Report</title></head><body style='margin: 0; padding-left: 100px; padding-right: 100px;'>"
    for doc_name in names:
        print doc_name
        doc = frappe.db.get_values("Sales Order", doc_name, "*", as_dict=True)[0]
        attachments = frappe.db.sql("""SELECT * FROM `tabFile` WHERE `attached_to_doctype`='Sales Order' AND `attached_to_name`=%s;""", (doc_name), as_dict=True)
        items = frappe.db.sql("""SELECT * FROM `tabSales Order Item` WHERE `parent`=%s;""", (doc_name), as_dict=True)

        html += "<div style='width:100%;'>"
        html += u"<font style='font-weight: bold'>Заявка " + doc_name + "</font>"

        info = False
        if doc.execution_date_limit:
            if not info:
                html += " - "
            info = True
            html += u"Срок " + str(doc.execution_date_limit.strftime("%d") + "-" + doc.execution_date_limit.strftime("%m") + "-" + doc.execution_date_limit.strftime("%Y")) + u"г. "
        if doc.owner:
            if not info:
                html += " - "
            info = True
            html += doc.owner
        html += "<br/>"

        image = False

        for item in items:
            html += "<div style='padding-left: 30px; padding-right: 30px;'>- " + item.item_name

            # koja section
            koja = False
            if item.estestvena_koja or item.eco_koja or item.damaska:
                html += u" с "
            if item.estestvena_koja:
                html += u"Естествена кожа"
                koja = True
            if item.eco_koja:
                if koja:
                    html += ", "
                html += u"Еко кожа"
                koja = True
            if item.damaska:
                if koja:
                    html += ", "
                html += u"Дамаска"
                koja = True
            if koja:
                html += u" от:<br/>"
                if item.collection_1:
                    html += u"Колекция: " + collection(item, 1) + "<br/>"
                if item.collection_2:
                    html += u"Колекция: " + collection(item, 2) + "<br/>"
                if item.collection_3:
                    html += u"Колекция: " + collection(item, 3) + "<br/>"

            # pillow section
            if item.divan_pillow_collection_1:
                html += u"Колекция декоративни възглавници:"
                html += divan_pillow_collection(item, 1) + "<br/>"
            if item.divan_pillow_collection_2:
                html += u"Колекция декоративни възглавници:"
                html += divan_pillow_collection(item, 2) + "<br/>"
            if item.divan_pillow_collection_3:
                html += u"Колекция декоративни възглавници:"
                html += divan_pillow_collection(item, 3) + "<br/>"

            #

            html += "</div>"
            if not image and item.divan_modification_image:
                html += "<div style='margin-left: auto; margin-right: auto; display: block; text-align: center;'>"
                image = True
            if item.divan_modification_image:
                html += "<div style='align:left;'><img src='" + item.divan_modification_image + "' alt='' style='max-height: 600px;' /></div>"

        if not image and len(attachments)>0:
            html += "<div style='margin-left: auto; margin-right: auto; display: block; text-align: center;'>"
            image = True
        for file in attachments:
            html += "<div style='align:left;'><img src='" + file.file_url + "' alt='' style='max-height: 600px;' /></div>"
        if image:
            html += "<div style='clear:both;'></div></div>"
            html += "</div><br/>"
        html += "<br/>"

    html += "</body></html>"

    from werkzeug.wrappers import Response
    response = Response()
    response.mimetype = 'text/html'
    response.charset = 'utf-8'
    response.data = html

    print ""
    print ""

    return response
