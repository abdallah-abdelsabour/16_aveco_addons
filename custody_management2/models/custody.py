# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError, UserError


class Custody(models.Model):
    _name = "custody.custody"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Custody"

    name = fields.Char(string="Number", readonly=True, tracking=True, translate=True, copy=False)
    date = fields.Date(string="Date", default=fields.Date.context_today, required=True, tracking=True)
    user_id = fields.Many2one("res.users", string="User", tracking=True, default=lambda self: self.env.user)
    date_deadline = fields.Datetime(string="Deadline", tracking=True)
    partner_id = fields.Many2one("res.partner", string="Contact", tracking=True)
    state = fields.Selection([
        ("draft", "Draft"),
        ("submit", "Submitted"),
        ("approve", "Approved"),
        ("refuse", "Refused"),
        ("cancel", "Cancel")], string="Status", required=True, tracking=True, default="draft", copy=False, index=True)
    company_id = fields.Many2one("res.company", string="Company", required=True, tracking=True,
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Currency", readonly=True, store=True)
    amount = fields.Monetary(string="Amount", required=True, tracking=True)
    description = fields.Text(string="Description")
    project_id = fields.Many2one("project.project", string="Project", tracking=True)
    payment_id = fields.Many2one("account.payment", string="Payment", copy=False)

    @api.constrains("amount")
    def _check_amount(self):
        for custody in self:
            if custody.amount <= 0:
                raise ValidationError(_("The amount must be positive."))

    def name_get(self):
        result = []
        for custody in self:
            if custody.state == "draft" and not custody.name:
                result.append((custody.id, _("Custody Draft")))
            else:
                result.append((custody.id, custody.name))

        return result

    def unlink(self):
        for custody in self:
            if custody.state != "draft" and custody.name:
                raise ValidationError(_(f"You cannot delete custody {custody.name} at this stage."))

        return super().unlink()

    def action_submit(self):
        sequence_obj = self.env["ir.sequence"]
        for custody in self.filtered(lambda c: c.state == "draft"):
            vals = {"state": "submit"}
            if not custody.name:
                vals.update({"name": sequence_obj.with_company(custody.company_id).next_by_code("custody.custody")})

            custody.write(vals)

    def _prepare_payment(self):
        return {
            "payment_type": "outbound",
            "partner_type": "supplier",
            "partner_id": self.partner_id and self.partner_id.id or self.user_id.partner_id.id,
            "amount": self.amount,
            "journal_id": self.company_id.custody_payment_journal_id.id,
            "date": self.date,
            "company_id": self.company_id.id,
            "ref": self.name
        }

    def action_approve(self):
        account_payment_obj = self.env["account.payment"].sudo()
        for custody in self:
            if not custody.company_id.custody_payment_journal_id:
                raise UserError(_("Check the settings to set the custody payment journal for approval."))

            custody.write({
                "state": "approve",
                "payment_id": account_payment_obj.create(custody._prepare_payment()).id
            })

    def action_refuse(self):
        self.filtered(lambda c: c.state == "submit").write({"state": "refuse"})

    def action_cancel(self):
        self.filtered(lambda c: c.state in ["draft", "submit"]).write({"state": "cancel"})

    def action_reset_draft(self):
        self.filtered(lambda c: c.state == "cancel").write({"state": "draft"})

    def action_get_payment(self):
        if not self.payment_id:
            return

        form = self.env.ref("account.view_account_payment_form")

        return {
            "type": "ir.actions.act_window",
            "res_model": "account.payment",
            "view_mode": "form",
            "res_id": self.payment_id.id,
            "views": [(form.id, "form")],
            "view_id": form.id,
        }
