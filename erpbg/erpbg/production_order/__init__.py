import frappe


@frappe.whitelist()
def get_sales_order_item(item_name, sales_order):
    soi = frappe.db.sql("""SELECT * FROM `tabSales Order Item` WHERE `item_name`=%s `parent`=%s""", (item_name, sales_order))
    return soi[0]
