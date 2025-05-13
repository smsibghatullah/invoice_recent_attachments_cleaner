from odoo import models, fields, api
from datetime import datetime, timedelta

class AttachmentCleaner(models.Model):
    _inherit = 'account.move'

    @api.model
    def clean_old_invoice_attachments(self):
        three_months_ago = datetime.today() - timedelta(days=100)

        invoices = self.env['account.move'].search([
            ('move_type', '=', 'out_invoice')
        ])

        attachment_model = self.env['ir.attachment']
        deleted_count = 0

        for invoice in invoices:
            old_attachments = attachment_model.search([
                ('res_model', '=', 'account.move'),
                ('res_id', '=', invoice.id),
                ('create_date', '<', three_months_ago),
            ])
            deleted_count += len(old_attachments)
            old_attachments.unlink()

        _logger = self.env['ir.logging']
        _logger.sudo().create({
            'name': 'Attachment Cleaner',
            'type': 'server',
            'dbname': self._cr.dbname,
            'level': 'info',
            'message': f'Deleted {deleted_count} old invoice attachments.',
            'path': 'models/attachment_cleaner.py',
            'line': 25,
            'func': 'clean_old_invoice_attachments',
        })

        return True
