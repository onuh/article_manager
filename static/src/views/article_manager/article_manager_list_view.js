/** @odoo-module **/

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ArticleManagerControllerList } from "@article_manager/views/article_manager/article_manager_list_controller";


export const ArticleManagerListView = {
    ...listView,
    Controller: ArticleManagerControllerList,
};

registry.category("views").add("article_manage_tree", ArticleManagerListView);
