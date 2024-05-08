# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


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



    def write(self, vals):
        if 'state' in vals and vals['state'] == 'reading':
            vals['start_date'] = fields.Date.today()

        elif 'state' in vals and vals['state'] == 'read':

            # send email to author here and update fields
            email_author = self.author
            email_values = {'book_title': self.title, 'book_reader_name': self.assigned_to.name, 'read_date': self.finished_date}

            # mail template details
            template_id = self.env.ref('article_manager.mail_template_read_article_notify').id
            template = self.env['mail.template'].browse(template_id)
            template.with_context(email_values).sudo().send_mail(email_author.id, force_send=True)
            vals['finished_date'] = fields.Date.today()

        res = super().write(vals)
        return res

    def get_allowed_ids(self):
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

        return allowed_view_ids

    def get_allowed_ids_with_state(self, state):

        allowed_view_ids = []
        # load ids based on logged in user
        logged_in_user = self.env.user
        if logged_in_user.has_group('article_manager.group_article_manager'):
            # load all records
            allowed_view_ids = self.env['article.article'].search([('state', '=', state)]).ids

        elif logged_in_user.has_group('article_manager.group_article_reader'):
            # load only ids associated with user
            related_partner = self.env.user.partner_id.id
            allowed_view_ids = self.env['article.article'].search([('assigned_to', '=', related_partner), ('state', '=', state)]).ids

        return allowed_view_ids


    @api.model
    def get_modified_data(self):

        context = dict(self.env.context or {})
        allowed_view_ids = self.get_allowed_ids()

        return {
            'name': _('Articles'),
            'type': 'ir.actions.act_window',
            'context': context,
            'view_mode': 'tree,kanban,form',
            'domain': [('id', 'in', allowed_view_ids)],
            'res_model': 'article.article',
        }

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if len(domain) <= 1 and 'assigned_to' in fields:
            domain = [['id', 'in', self.get_allowed_ids()]]
            return super().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
        if domain[0] == '&' and domain[1][0] == 'state' and 'assigned_to' in fields:
            state = domain[1][2]
            domain[2] = ['id', 'in', self.get_allowed_ids_with_state(state)]
        return super().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)

    @api.model
    def web_read_group(self, domain, fields, groupby, limit=None, offset=0, orderby=False,lazy=True, expand=False, expand_limit=None, expand_orderby=False):
        res = super().web_read_group(domain=domain, fields=fields, groupby=groupby, limit=limit, orderby=orderby, lazy=lazy, expand_limit=expand_limit, expand_orderby=expand_orderby)
        if 'assigned_to' in fields and groupby[0] == 'state':
            # alter the data
            states = []
            state_count = []
            ids = []
            groups = []

            state_open = self.get_allowed_ids_with_state('open')
            if state_open:
                states.append('open')
                state_count.append(len(state_open))
                ids.append(state_open)

            state_reading = self.get_allowed_ids_with_state('reading')
            if state_reading:
                states.append('reading')
                state_count.append(len(state_reading))
                ids.append(state_reading)

            state_read = self.get_allowed_ids_with_state('read')
            if state_read:
                states.append('read')
                state_count.append(len(state_read))
                ids.append(state_read)

            state_abandon = self.get_allowed_ids_with_state('abandon')
            if state_abandon:
                states.append('abandon')
                state_count.append(len(state_abandon))
                ids.append(state_abandon)

            i = 0
            for state in states:
                if len(states) == 1:
                    state_dict = {'state_count': state_count[i], 'state': state, '__domain': [('state', '=', state)]}
                else:
                    state_dict = {'state_count': state_count[i], 'state': state, '__domain': ['&', ('state', '=', state), ('id', 'in', ids[i])]}
                groups.append(state_dict)
                i += 1
            res1 = {'groups': groups, 'length': len(states)}
            return res1
        return res

    def action_move_to_reading(self):
    	self.write({'state': 'reading'})
    	today = fields.Date.today()
    	self.write({'start_date': today})

    def action_move_to_read(self):
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
