/**
 * Created by Simeon on 4-Dec-17.
 */
frappe.ui.form.on("Quotation Item", "onload_post_render", function (frm, cdt, cdn) {
    if(locals[cdt][cdn].divan_modification != "") {
        type_image(locals[cdt][cdn]);
    }
});
frappe.ui.form.on("Quotation Item", "divan_modification", function (frm, cdt, cdn) {
    if(locals[cdt][cdn].divan_modification != "") {
        type_image(locals[cdt][cdn]);
    }
});

