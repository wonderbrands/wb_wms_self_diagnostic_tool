# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class wb_wms_self_diagnostic_tool(models.Model):
#     _name = 'wb_wms_self_diagnostic_tool.wb_wms_self_diagnostic_tool'
#     _description = 'wb_wms_self_diagnostic_tool.wb_wms_self_diagnostic_tool'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
