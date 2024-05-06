# -*- coding: utf-8 -*-
import json
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class articleManager(models.Model):
    _name = 'article.article'
    _description = 'Article Management'
    _inherit = ['portal.mixin', 'mail.thread',
                'mail.activity.mixin']  # inherit models to be used in chatter to know user that created record


    def get_manager(self):
        logged_in_user = self.env.user
        if logged_in_user.has_group('article_manager.group_article_manager'):
            return True
        return False

    def get_reader(self):
        logged_in_user = self.env.user
        if logged_in_user.has_group('article_manager.group_article_reader'):
            return True
        return False

    # fields for model
    name = fields.Char()
    image = fields.Binary("Image")
    author = fields.Many2one('res.partner', 'Author', default=lambda self: self.env.user.partner_id.id)
    title = fields.Text('Title')
    publish_date = fields.Date('Publish Date')
    start_date = fields.Date('Start Date')
    finished_date = fields.Date('Finished Date')
    deadline = fields.Date('Deadline')
    assigned_to = fields.Many2one('res.partner', 'Assigned To')
    content = fields.Text('Content')
    is_article_manager = fields.Boolean('Manager', store=False, default=lambda self: self.get_manager())
    is_article_reader = fields.Boolean('Reader', store=False, default=lambda self: self.get_reader())
    active = fields.Boolean('Active', default=True)
    state = fields.Selection([('open', 'Open'), ('reading', 'Reading'), ('read', 'Read'), ('abandon', 'Abandoned')],
                             default="open", tracking=True, copy=False, readonly=False)

    @api.model
    def get_modified_data(self):

        context = dict(self.env.context or {})
        allowed_view_ids = []

        # load ids based on logged in user
        logged_in_user = self.env.user
        if logged_in_user.has_group('article_manager.group_article_manager'):
            # load all records
            allowed_view_ids = self.env['article.article'].search([]).ids

        elif logged_in_user.has_group('article_manager.group_article_reader'):
            # load only ids associated with user
            related_partner = self.env.user.partner_id.id
            allowed_view_ids = self.env['article.article'].search([('assigned_to', '=', related_partner)]).ids

        return {
            'name': _('Articles'),
            'type': 'ir.actions.act_window',
            'context': context,
            'view_mode': 'tree,kanban,form',
            'domain': [('id', 'in', allowed_view_ids)],
            'res_model': 'article.article',
        }


    def action_move_to_reading(self):
    	self.write({'state': 'reading'})
    	today = fields.Date.today()
    	self.write({'start_date': today})

    def action_move_to_read(self):

    	# send email to author here and update fields
        email_author = self.author
        email_values = {'book_title': self.title, 'book_reader_name': self.assigned_to.name, 'read_date': self.finished_date}

        # mail template details
        template_id = self.env.ref('article_manager.mail_template_read_article_notify').id
        template = self.env['mail.template'].browse(template_id)
        template.with_context(email_values).send_mail(email_author.id, force_send=True)
        self.write({'state': 'read'})
        today = fields.Date.today()
        self.write({'finished_date': today})

    def action_move_to_abandon(self):
    	self.write({'state': 'abandon'})

    # crud method create for ORM
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = vals['title']
        return super().create(vals_list)

class articleManagerReport(models.AbstractModel):

    # report model
    _name = 'report.article_manager.report_article'
    _description = 'Article Manager Report'

    # api to pass data from model to report template
    @api.model
    def _get_report_values(self, docids, data=None):
        model = 'article.article'
        docs = self.env[model].browse(self.env.context.get('active_ids', docids))

        # filter out only report with read state
        docs = docs.filtered(lambda r: r.state == 'read')
        if not docs:
            raise ValidationError(_('Report(s) not in read state.'))

        return {
            'doc_ids': docids,
            'doc_model': model,
            'data': data,
            'docs': docs,
        }

class resPartner(models.Model):
    # inherit this model as we used in email template
    _inherit = 'res.partner'

    # @api.model
    # def name_get(self):
    #     res = super().name_get()
    #     print("RES: ", res)
    #     return res
