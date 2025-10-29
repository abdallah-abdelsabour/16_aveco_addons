# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductMaterial(models.Model):
    _name = 'product.material'
    _description = 'Product Material'

    name = fields.Many2one('product.template', string="Material", required=True)
    quantity = fields.Float(string="Quantity", required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    unit_price = fields.Monetary(string="Cost", required=True, currency_field='currency_id')
    total_price = fields.Monetary(string="Total Price", compute="_compute_total_price", store=True, currency_field='currency_id')
    uom_id = fields.Many2one('uom.uom', string="Unit of Measure", store=True)
    product_template_id = fields.Many2one('product.template', string="Product Template", required=True)

    @api.onchange('name')
    def _onchange_name(self):
        """
        Update the cost based on the product cost.
        """
        if self.name:
            self.unit_price = self.name.list_price
            self.uom_id = self.name.uom_id

    @api.depends('quantity', 'unit_price')
    def _compute_total_price(self):
        """
        Compute the total price.
        """
        for record in self:
            record.total_price = record.quantity * record.unit_price


class ProductLabor(models.Model):
    _name = 'product.labor'
    _description = 'Product Labor'

    name = fields.Many2one('hr.job', string="Labor", required=True)
    quantity = fields.Float(string="Quantity", required=True)
    unit_price = fields.Monetary(string="Cost", required=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    total_price = fields.Monetary(string="Total Price", compute="_compute_total_price", store=True, currency_field='currency_id')
    uom_id = fields.Many2one('uom.uom', string="Unit of Measure", store=True)
    product_template_id = fields.Many2one('product.template', string="Product Template", required=True)

    @api.depends('quantity', 'unit_price')
    def _compute_total_price(self):
        """
        Compute the total price.
        """
        for record in self:
            record.total_price = record.quantity * record.unit_price

    @api.onchange('name')
    def _onchange_name(self):
        """
        Update the cost based on the product cost.
        """
        if self.name:
            self.unit_price = self.name.unit_price


class ProductOther(models.Model):
    _name = 'product.other'
    _description = 'Product Other'

    name = fields.Many2one('product.template', string="Product", required=True)
    quantity = fields.Float(string="Quantity", required=True)
    uom_id = fields.Many2one('uom.uom', string="Unit of Measure", store=True)
    unit_price = fields.Monetary(string="Cost", required=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    total_price = fields.Monetary(string="Total Price", compute="_compute_total_price", store=True, currency_field='currency_id')
    product_template_id = fields.Many2one('product.template', string="Product Template", required=True)

    @api.depends('unit_price', 'quantity')
    def _compute_total_price(self):
        """
        Compute the total price.
        """
        for record in self:
            record.total_price = record.unit_price * record.quantity

    @api.onchange('name')
    def _onchange_name(self):
        """
        Update the cost based on the product cost.
        """
        if self.name:
            self.unit_price = self.name.list_price
            self.uom_id = self.name.uom_id


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_business_item = fields.Boolean(string="Is Business Item", default=False)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    material_ids = fields.One2many('product.material', 'product_template_id', string="Materials")
    total_material_cost = fields.Monetary(string="Total Material Cost", compute="_compute_total_material_cost", currency_field='currency_id')
    labor_ids = fields.One2many('product.labor', 'product_template_id', string="Labor")
    total_labor_cost = fields.Monetary(string="Total Labor Cost", compute="_compute_total_labor_cost", currency_field='currency_id')
    other_ids = fields.One2many('product.other', 'product_template_id', string="Other")
    total_other_cost = fields.Monetary(string="Total Other Cost", compute="_compute_total_other_cost", currency_field='currency_id')
    total_cost = fields.Monetary(string="Total Cost", compute="_compute_total_cost", currency_field='currency_id')
    project_name = fields.Char(string="Project Name", )

    @api.depends('material_ids')
    def _compute_total_material_cost(self):
        """
        Compute the total material cost.
        """
        for record in self:
            record.total_material_cost = sum(record.material_ids.mapped('total_price'))

    @api.depends('labor_ids')
    def _compute_total_labor_cost(self):
        """
        Compute the total labor cost.
        """
        for record in self:
            record.total_labor_cost = sum(record.labor_ids.mapped('total_price'))

    @api.depends('other_ids')
    def _compute_total_other_cost(self):
        """
        Compute the total other cost.
        """
        for record in self:
            record.total_other_cost = sum(record.other_ids.mapped('total_price'))

    @api.depends('total_material_cost', 'total_labor_cost', 'total_other_cost')
    def _compute_total_cost(self):
        """
        Compute the total cost.
        """
        for record in self:
            record.total_cost = record.total_material_cost + record.total_labor_cost + record.total_other_cost

    @api.onchange('total_cost')
    def _onchange_total_cost(self):
        """
        Update the list price based on the total cost.
        """
        if self.total_cost:
            self.standard_price = self.total_cost


class HRJob(models.Model):
    _inherit = 'hr.job'

    unit_price = fields.Monetary(string="Cost", required=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)


class CostSheet(models.Model):
    _name = 'cost.sheet'
    _description = 'Cost Sheet'

    name = fields.Many2one('project.project', string="Project", required=True)
    project_code = fields.Char(string="Project Code", related="name.project_code")
    partner_id = fields.Many2one('res.partner', string="Customer", related="name.partner_id")
    sale_order_id = fields.Many2one('sale.order', string="Quotation", required=True)
    sale_order_date = fields.Datetime(string="Quotation Date", related="sale_order_id.date_order")
    cost_sheet_line_ids = fields.One2many('cost.sheet.line', 'cost_sheet_id', string="Cost Sheet Lines")


class CostSheetLine(models.Model):
    _name = 'cost.sheet.line'
    _description = 'Cost Sheet Line'

    cost_sheet_id = fields.Many2one('cost.sheet', string="Cost Sheet", required=True)
    product_template_id = fields.Many2one('product.template', string="Product Template", required=True)
    product_id = fields.Many2one('product.product', string="Product", required=True)
    product_uom_qty = fields.Float(string="Quantity", required=True)
    product_uom = fields.Many2one('uom.uom', string="Unit of Measure", required=True)
    price_unit = fields.Monetary(string="Unit Price", required=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    total_price = fields.Monetary(string="Total Price", compute="_compute_total_price", store=True, currency_field='currency_id')
    sale_line_id = fields.Many2one('sale.order.line', string="Quotation Line")
    display_type = fields.Selection(related='sale_line_id.display_type', string='Type', readonly=False, store=True)

    @api.depends('product_uom_qty', 'price_unit')
    def _compute_total_price(self):
        """
        Compute the total price.
        """
        for record in self:
            record.total_price = record.product_uom_qty * record.price_unit

    def action_show_material(self):
        """
        Show the materials.
        """
        return {
            'name': _('Materials Details'),
            'view_mode': 'tree,form',
            'res_model': 'product.template',
            'type': 'ir.actions.act_window',
            'res_id': self.product_template_id.id,
            'views': [(self.env.ref('tender_costing.view_show_material_form').id, 'form')],
            'target': 'new',
            'context': self.env.context,
        }


class Project(models.Model):
    _inherit = 'project.project'

    project_code = fields.Char(string="Project Code", required=False, index=True)
    project_type_id = fields.Many2one('project.type', string="Project Type", required=False)
    is_construction_project = fields.Boolean(string="Is Construction Project", compute="_compute_is_construction_project", store=True)
    # Warehouse Tab
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")
    src_location_id = fields.Many2one('stock.location', string="Source Location")
    dest_location_id = fields.Many2one('stock.location', string="Destination Location")
    picking_type_id = fields.Many2one('stock.picking.type', string="Picking Type")

    @api.depends('project_type_id')
    def _compute_is_construction_project(self):
        """
        Check if the project type is construction project.
        """
        for record in self:
            record.is_construction_project = record.project_type_id.name == 'Construction'


class ProjectType(models.Model):
    _name = 'project.type'
    _description = 'Project Type'

    name = fields.Char(string="Name", required=True)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    construction_project_id = fields.Many2one('project.project', string="Construction Project")
    is_cost_sheet_created = fields.Boolean(string="Is Cost Sheet Created", default=False)
    cost_sheet_id = fields.Many2one('cost.sheet', string="Cost Sheet")
    is_construction_quotation = fields.Boolean(string="Is Construction Quotation", default=False)

    def action_confirm(self):
        """
        Create a cost sheet based on the quotation.
        """
        res = super(SaleOrder, self).action_confirm()
        if self.is_construction_quotation:
            # Create a cost sheet based on the quotation.
            cost_sheet = self.env['cost.sheet'].create({
                'name': self.construction_project_id.id,
                'sale_order_id': self.id,
                'cost_sheet_line_ids': [(0, 0, {
                    'product_template_id': line.product_id.product_tmpl_id.id,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'product_uom': line.product_uom.id,
                    'price_unit': line.price_unit,
                    'sale_line_id': line.id,
                }) for line in self.order_line]
            })
            self.cost_sheet_id = cost_sheet.id
            self.is_cost_sheet_created = True
        return res

    def open_cost_sheet(self):
        """
        Open the cost sheet.
        """
        return {
            'name': 'Cost Sheet',
            'view_mode': 'form',
            'res_model': 'cost.sheet',
            'type': 'ir.actions.act_window',
            'res_id': self.cost_sheet_id.id,
            'context': self.env.context,
        }


class Deductions(models.Model):
    _name = 'construction.deductions'

    name = fields.Char(sring="Deduction Name", required=True)
    amount = fields.Float(string="Amount/Percentage", required=False)
    notes = fields.Text(string="Notes")
    type = fields.Selection( [("amount", "Amount"),
        ("percent", "Percent"),], string="Type",default="amount", required=True)
    account_id = fields.Many2one('account.account',string="Account")


class SubscriptionContracts(models.Model):
    _inherit = 'subscription.contracts'

    construction_project_id = fields.Many2one('project.project', string="Construction Project")
    sale_order_id = fields.Many2one('sale.order', string="Quotation")
    contract_amount = fields.Monetary(related="sale_order_id.amount_total", string="Contract Amount", currency_field='currency_id')
    final_insurance_percentage = fields.Float(string="Final Insurance Percentage", required=False)
    final_insurance_amount = fields.Monetary(string="Final Insurance Amount", required=False, currency_field='currency_id')
    business_guarantee_percentage = fields.Float(string="Business Guarantee Percentage", required=False)
    business_guarantee_amount = fields.Monetary(string="Business Guarantee Amount", required=False, currency_field='currency_id')
    down_payment_percentage = fields.Float(string="Down Payment Percentage", required=False)
    down_payment_amount = fields.Monetary(string="Down Payment Amount", required=False, currency_field='currency_id')

    @api.onchange('business_guarantee_percentage')
    def _onchange_business_guarantee_percentage(self):
        """
        Update the business guarantee amount based on the business guarantee percentage.
        """
        if self.business_guarantee_percentage:
            self.business_guarantee_amount = self.contract_amount * (self.business_guarantee_percentage / 100)

    @api.onchange('business_guarantee_amount')
    def _onchange_business_guarantee_amount(self):
        """
        Update the business guarantee percentage based on the business guarantee amount.
        """
        if self.business_guarantee_amount:
            self.business_guarantee_percentage = self.business_guarantee_amount / self.contract_amount * 100

    @api.onchange('down_payment_percentage')
    def _onchange_down_payment_percentage(self):
        """
        Update the down payment amount based on the down payment percentage.
        """
        if self.down_payment_percentage:
            self.down_payment_amount = self.contract_amount * (self.down_payment_percentage / 100)

    @api.onchange('down_payment_amount')
    def _onchange_down_payment_amount(self):
        """
        Update the down payment percentage based on the down payment amount.
        """
        if self.down_payment_amount:
            self.down_payment_percentage = self.down_payment_amount / self.contract_amount * 100

    @api.onchange('final_insurance_percentage')
    def _onchange_final_insurance_percentage(self):
        """
        Update the final insurance amount based on the final insurance percentage.
        """
        if self.final_insurance_percentage:
            self.final_insurance_amount = self.contract_amount * (self.final_insurance_percentage / 100)

    @api.onchange('final_insurance_amount')
    def _onchange_final_insurance_amount(self):
        """
        Update the final insurance percentage based on the final insurance amount.
        """
        if self.final_insurance_amount:
            self.final_insurance_percentage = self.final_insurance_amount / self.contract_amount * 100

    def write(self, vals):
        res = super(SubscriptionContracts, self).write(vals)
        if vals.get('sale_order_id'):
            order_line = self.env['sale.order.line'].search([('order_id', '=', vals.get('sale_order_id'))])
            self.sale_order_line_ids.write({'contract_id': False})
            order_line.write({'contract_id': self.id})
        return res


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    is_subcontractor = fields.Boolean(string="Is Subcontractor", default=False)
