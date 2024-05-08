# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class resPartner(models.Model):
    # inherit this model as we used in email template
    _inherit = 'res.partner'