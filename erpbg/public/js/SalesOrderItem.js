frappe.ui.form.on("Sales Order Item", "divan_modification_link", function (frm, cdt, cdn) {
    if(locals[cdt][cdn].divan_modification_link != "") {
        modification_image(locals[cdt][cdn]);
    }
});