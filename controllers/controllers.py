# -*- coding: utf-8 -*-
# from odoo import http


# class WbWmsSelfDiagnosticTool(http.Controller):
#     @http.route('/wb_wms_self_diagnostic_tool/wb_wms_self_diagnostic_tool', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wb_wms_self_diagnostic_tool/wb_wms_self_diagnostic_tool/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('wb_wms_self_diagnostic_tool.listing', {
#             'root': '/wb_wms_self_diagnostic_tool/wb_wms_self_diagnostic_tool',
#             'objects': http.request.env['wb_wms_self_diagnostic_tool.wb_wms_self_diagnostic_tool'].search([]),
#         })

#     @http.route('/wb_wms_self_diagnostic_tool/wb_wms_self_diagnostic_tool/objects/<model("wb_wms_self_diagnostic_tool.wb_wms_self_diagnostic_tool"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wb_wms_self_diagnostic_tool.object', {
#             'object': obj
#         })
