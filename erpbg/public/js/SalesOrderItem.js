frappe.ui.form.on("Sales Order Item", "onload_post_render", function (frm, cdt, cdn) {
    type_image(locals[cdt][cdn]);
});

frappe.ui.form.on("Sales Order Item", "divan_modification", function (frm, cdt, cdn) {
    type_image(locals[cdt][cdn]);
});