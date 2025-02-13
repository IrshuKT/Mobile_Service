from odoo import models, fields, api

class DocumentUpload(models.Model):
    _name = 'document.upload'
    _description = 'Document, Video, or Image Upload'

    name = fields.Char(string="Name", required=True)
    file_ids = fields.Many2many('ir.attachment', string='Uploaded Files')
    contact_id = fields.Many2one('mobile.contact')
    mimetype = fields.Char(string='MIME Type')  # Add mimetype here if needed

    def _create_attachment(self, file_data, filename, file_type):
        """Helper method to create an attachment"""
        attachment_obj = self.env['ir.attachment']
        attachment = attachment_obj.create({
            'name': filename,
            'datas': file_data,
            'type': 'binary',
            'mimetype': file_type,  # This will be used for the mimetype
            'res_model': 'document.upload',
            'res_id': self.id,
        })

        # Optionally, you can store the mimetype in the DocumentUpload model if you need to
        self.mimetype = file_type

        return attachment
