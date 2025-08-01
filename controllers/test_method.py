from odoo import http

class TestMethod(http.Controller):
    @http.route('/test_method_oms', auth='public')
    def test_method(self, **kw):
        self.env['oms.sale.controller'].cron_sync_sales()
        return "Done"
