# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class ArticleManager(http.Controller):
    @http.route('/api/article_manager/create', auth='user', type='json')
    def create_record(self, **kw):
        
        try:
            articles = []
            create_data = []
            if not kw.get('assigned_to') or not kw.get('title') or not kw.get('publish_date') or not kw.get('deadline') or not kw.get('content'):
                vals = {'"assigned_to", "title", "publish_date", "deadline", "content" are required parameter keys'}
                articles.append(vals)
                data = {"status": "error", "response": articles}
                return data
            if not isinstance(kw['assigned_to'], int):
                vals = {'"assigned_to" must have an integer value, this is related partner id of user'}
                articles.append(vals)
                data = {"status": "error", "response": articles}
                return data
            kw['author'] = request.env.user.partner_id.id
            create_data.append(kw)
            model = request.env['article.article']
            for data in create_data:
                create_article = model.create(data)
                vals = {'create_id': create_article.id}
                articles.append(vals)
                data = {"status": "success", "response": articles}
                return data
        except Exception as e:
            data = {"status": "error", "response": e}
            return data

    @http.route('/api/article_manager/delete/<int:rec_id>', auth='user', type='json')
    def delete_record(self, rec_id):
        try:
            rec_id = int(rec_id)
            model = request.env['article.article'].browse(rec_id)
            articles = []
            delete_record = model.unlink()
            if delete_record:
                vals = {'delete_id': rec_id}
                articles.append(vals)
                data = {"status": "success", "response": articles}
                return data
            data = {"status": "error", "response": "error deleting record"}
            return data

        except Exception as e:
            data = {"status": "error", "response": e}
            return data

    @http.route('/api/article_manager/update/<int:rec_id>', auth='user', type='json')
    def update_record(self, rec_id, **kw):
        articles = []
        write_data = []
        try:
            rec_id = int(rec_id)
            if request.env.user.has_group('article_manager.group_article_reader'):
                user_id = request.env.user.id
                all_data = request.env['article.article'].search([('assigned_to', '=', user_id)]).ids
                if rec_id not in all_data:
                    data = {"status": "error", "response": "You are not authorised to update data or record does not exist"}
                    return data
                elif len(kw.values()) > 1 or not kw.get('state'):
                    data = {"status": "error", "response": "You cannot update more than the state of an article, kindly send only 'state' param"}
                    return data

            if kw.get('assigned_to') and not isinstance(kw['assigned_to'], int):
                vals = {'"assigned_to" must have an integer value, this is related partner id of user'}
                articles.append(vals)
                data = {"status": "error", "response": articles}
                return data
            # try for author not to be changed even if edited by another person
            exist_rec = request.env['article.article'].search([('id', '=', rec_id)])
            kw['author'] = exist_rec.author.id
            write_data.append(kw)
            model = request.env['article.article']
            for data in write_data:
                write_article = model.write(data)
                vals = {'write_id': rec_id}
                articles.append(vals)
                data = {"status": "success", "response": articles}
                return data
        except Exception as e:
            data = {"status": "error", "response": e}
            return data
            

    @http.route('/api/article_manager/fetch', auth='user', type='json')
    def fetch_record(self, **kw):
        try:
            if request.env.user.has_group('article_manager.group_article_manager'):
                all_data = request.env['article.article'].search([])

            elif request.env.user.has_group('article_manager.group_article_reader'):
                user_id = request.env.user.id
                all_data = request.env['article.article'].search([('assigned_to', '=', user_id)])

            articles = []
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
                articles.append(vals)
            data = {"status": "success", "response": articles}
            return data
        except Exception as e:
            data = {"status": "error", "response": e}
            return data
