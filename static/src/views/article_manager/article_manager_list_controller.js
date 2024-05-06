/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { useService } from "@web/core/utils/hooks"
const { Component, EventBus, onWillStart, useSubEnv, useState, useComponent, useEnv } = owl;



export class ArticleManagerControllerList extends ListController {
    setup() {
        super.setup();
            this.orm = useService("orm");
            this.actionService = useService("action");
            const component = useComponent();
            const env = useEnv();
         onWillStart(async () => {
            //console.log(this.getRecords())
        
        });
        
    }

        async getRecords() {
        const action = await this.orm.call(
            "article.article",
            "get_modified_data",
        );
        return action
    }
  
}