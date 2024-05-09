# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class ArticleManager(http.Controller):
    # responses for success is an array of json object while an error response is a string, 
    # so always check for the status field to know whether response is array of json object or string.

    def success_response(self, response):
        data = {"status": "success", "response": response}
        return data

    def error_response(self, response):
        data = {"status": "error", "response": str(response)}
        return data

    @http.route('/api/article_manager/create', auth='user', type='json')
    def create_record(self, **kw):
        
        try:
            response = []
            if not kw.get('assigned_to') or not kw.get('title') or not kw.get('publish_date') or not kw.get('deadline') or not kw.get('content'):
                return self.error_response('"assigned_to", "title", "publish_date", "deadline", "content" are required parameter keys')
            if not isinstance(kw['assigned_to'], int):
                return self.error_response('"assigned_to" must have an integer value, this is related partner id of user')
            kw['author'] = request.env.user.partner_id.id
            model = request.env['article.article']
            create_article = model.create(kw)
            vals = {'create_id': create_article.id}
            response.append(vals)
            return self.success_response(response)
        except Exception as e:
            return self.error_response(e)

    @http.route('/api/article_manager/delete/<int:rec_id>', auth='user', type='json')
    def delete_record(self, rec_id):
        try:
            rec_id = int(rec_id)
            model = request.env['article.article'].sudo().browse(rec_id)
            response = []
            if not model:
                return self.error_response("Record does not exist")
            delete_record = model.unlink()
            if delete_record:
                vals = {'delete_id': rec_id}
                response.append(vals)
                return self.success_response(response)
            return self.error_response('error deleting record')
        except Exception as e:
            return self.error_response(e)

    @http.route('/api/article_manager/update/<int:rec_id>', auth='user', type='json')
    def update_record(self, rec_id, **kw):
        response = []
        try:
            rec_id = int(rec_id)
            if request.env.user.has_group('article_manager.group_article_reader'):
                user_id = request.env.user.partner_id.id
                all_data = request.env['article.article'].search([('assigned_to', '=', user_id)]).ids
                if rec_id not in all_data:
                    return self.error_response("You are not authorised to update data or record does not exist")
                elif len(kw.values()) > 1 or not kw.get('state'):
                    return self.error_response("You cannot update more than the state of an article, kindly send only 'state' param")
            if kw.get('assigned_to') and not isinstance(kw['assigned_to'], int):
                return self.error_response('"assigned_to" must have an integer value, this is related partner id of user')
            # try for author not to be changed even if edited by another person
            exist_rec = request.env['article.article'].search([('id', '=', rec_id)])
            if not exist_rec:
                return self.error_response("Record does not exist")
            kw['author'] = exist_rec.author.id
            write_article = exist_rec.write(kw)
            vals = {'write_id': rec_id}
            response.append(vals)
            return self.success_response(response)
        except Exception as e:
            return self.error_response(e)
            

    @http.route('/api/article_manager/fetch', auth='user', type='json')
    def fetch_record(self, **kw):
        try:
            if request.env.user.has_group('article_manager.group_article_manager'):
                all_data = request.env['article.article'].search([])

            elif request.env.user.has_group('article_manager.group_article_reader'):
                user_id = request.env.user.partner_id.id
                all_data = request.env['article.article'].search([('assigned_to', '=', user_id)])

            response = []
            for rec in all_data:
                vals ={
                'id': rec.id,
                'title': rec.title, 
                'author': rec.author.name,
                'assigned_to': rec.assigned_to.name,
                'publish_date': rec.publish_date,
                'deadline': rec.deadline,
                'start_date': rec.start_date,
                'finished_date': rec.finished_date,
                'state': rec.state,
                'content': rec.content,
                'image': rec.image
                }
                response.append(vals)
            return self.success_response(response)
        except Exception as e:
            return self.error_response(e)
