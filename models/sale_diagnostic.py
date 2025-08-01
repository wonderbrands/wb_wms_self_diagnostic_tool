# -*- coding: utf-8 -*-

from odoo import models, fields, api
import base64
import io
from PyPDF2 import PdfReader
import logging

_logger = logging.getLogger(__name__)

class WMSSaleChecker(models.Model):
    _inherit = "sale.order"

    last_oms_sync = fields.Datetime(
        string="Last OMS Sync",
        readonly=True
    )

    last_wms_sync = fields.Datetime(
        string="Last WMS Sync",
        readonly=True
    )

    last_odoo_update = fields.Datetime(
        string="Last Odoo Update",
        readonly=True
    )

    has_carrier = fields.Boolean(
        string="Has Carrier",
        readonly=True
    )

    has_packet_guide = fields.Boolean(
        string="Has Packet Guide",
        readonly=True
    )

    packet_guide_att_page_num = fields.Integer(
        string="Packet Guide Att Page Num",
        readonly=True
    )

    status_oms = fields.Char(
        string="Status OMS",
        readonly=True
    )

    status_wms = fields.Char(
        string="Status WMS",
        readonly=True
    )

    packages = fields.Text(
        string="Packages",
        readonly=True
    )

    @api.depends('carrier_selection_relational')
    def _compute_has_carrier(self):
        for record in self:
            record.has_carrier = bool(record.carrier_selection_relational)
            record.last_odoo_update = fields.Datetime.now()

    @api.depends('channel_order_reference')
    def _compute_has_packet_guide(self):
        for record in self:
            record.has_packet_guide = bool(record.channel_order_reference)
            record.last_odoo_update = fields.Datetime.now()

    @api.depends("delivery_count", "channel_order_reference", "picking_ids")
    def _compute_packet_guide_att_page_num(self):
        Attachment = self.env['ir.attachment']

        for record in self:
            total_pages = 0
            pickings_with_pick = record.picking_ids.filtered(lambda p: 'PICK' in p.name)

            for picking in pickings_with_pick:
                attachments = Attachment.search([
                    ('res_model', '=', 'stock.picking'),
                    ('res_id', '=', picking.id),
                    ('mimetype', 'in', ['application/pdf', 'text/plain']),
                    ('type', '=', 'binary'),
                    ('datas', '!=', False),
                ])

                for att in attachments:
                    try:
                        data = base64.b64decode(att.datas)
                        if att.mimetype == 'application/pdf':
                            reader = PdfReader(io.BytesIO(data))
                            total_pages += len(reader.pages)
                        elif att.mimetype == 'text/plain':
                            total_pages += 1
                    except Exception as e:
                        _logger.warning(f"Failed to process attachment {att.name}: {e}")
                        continue

            record.packet_guide_att_page_num = total_pages
            record.last_odoo_update = fields.Datetime.now()


