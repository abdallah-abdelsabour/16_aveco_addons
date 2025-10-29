# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression


class ProductCategory(models.Model):
    _inherit = 'product.category'

    construction_code = fields.Char(string="Construction Code", required=False, index=True)
    sequence_id = fields.Many2one('ir.sequence', string='Sequence', index=True)

    @api.constrains('construction_code')
    def _check_construction_code(self):
        """
        Ensure that the code is unique.
        Ensure that the code contains numbers and dots (optionally) only.
        Otherwise, raise an error.
        :return:
        """
        if not self.construction_code:
            return
        if self.search_count([('construction_code', '=', self.construction_code)]) > 1:
            raise ValidationError(_("Construction Code must be unique"))

        # Check if the code contains numbers and dots only
        if not self.construction_code.isdigit() and not self.construction_code.replace('.', '').isdigit():
            raise ValidationError(_("Construction Code must contain numbers and dots (optionally) only"))

    def _get_level(self):
        """
        Returns the number of parents or the child level
        :return:
        """
        if self.parent_id:
            return self.parent_id.parent_path.count('/')
        else:
            return 0

    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        """
        Update the construction code based on the parent category.

        If the parent category is not selected or does not have a construction code,
        the construction code remains unchanged.

        If the category level is 1, the construction code is updated as the parent construction code
        plus the number of child categories plus 1.

        If the category level is greater than 1, the construction code is updated as the parent construction code
        plus a dot plus the number of child categories plus 1.
        """
        if not self.parent_id or not self.parent_id.construction_code:
            return

        child_count = self.search_count([('parent_id', '=', self.parent_id.id)])
        category_level = self._get_level()

        if category_level == 1:
            self.construction_code = f"{int(self.parent_id.construction_code) + child_count + 1}"
        elif category_level > 1:
            self.construction_code = f"{self.parent_id.construction_code}.{child_count + 1}"
        else:
            pass

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        if not args:
            args = []
        if name:
            args += ['|', ('construction_code', operator, name)]
            args += [('name', operator, name)]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            categ_obj = self.env['product.category'].browse(vals.get('categ_id'))
            if categ_obj.construction_code:
                if not categ_obj.sequence_id:
                    sequence_obj = self.env['ir.sequence'].create({'name': f"Construction Code Sequence - {categ_obj.name}", 'padding': 3, 'prefix': f"{categ_obj.construction_code}.", 'code': 'product.category'})
                    categ_obj.sequence_id = sequence_obj.id
                else:
                    sequence_obj = categ_obj.sequence_id
                vals.update({'default_code': sequence_obj.next_by_id()})
        return super(ProductTemplate, self).create(vals_list)

    def write(self, vals):
        if 'categ_id' in vals:
            categ_obj = self.env['product.category'].browse(vals.get('categ_id'))
            if categ_obj.construction_code:
                if not categ_obj.sequence_id:
                    sequence_obj = self.env['ir.sequence'].create({'name': f"Construction Code Sequence - {categ_obj.name}", 'padding': 3, 'prefix': f"{categ_obj.construction_code}.", 'code': 'product.category'})
                    categ_obj.sequence_id = sequence_obj.id
                else:
                    sequence_obj = categ_obj.sequence_id
                vals.update({'default_code': sequence_obj.next_by_id()})
        return super(ProductTemplate, self).write(vals)

