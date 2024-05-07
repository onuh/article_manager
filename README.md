# Odoo Article Management Module
An ERP Module for creation and Management of articles

# About This Module
Odoo Article Management module allows managers to create articles and assign it to readers with a publish and a deadline date. Readers only have access to articles assigened to them. Readers can only change the states of an article from "open" to "reading" or to "read". Readers can also move to "abandoned" state. The module has a list and kanban view. The kanban view allows for change of article states using drag and drop. Once an article is moved from state "open" to "reading", the start date is automatically updated allowing the article author to see when the reader started reading the article. Once the article reader moves to "read" state, the end date is updated and an email notification is sent to the article createor informing him/her of the success of the reader. The module also has API endpoints to creste, update, delete and fetch an article. Users must authenticate to use the API endpoints. The module has a report template for only articles in "read" state with headers (S/N, Article, Date Published, Assigned To and Date Completed). Article can be filtered and grouped by Author, title, Assignees, state, deadline and publish date. The module comes with a demo data in [demo.xml](demo/demo.xml) file.

# Security Groups and Access Rights
The module has two security groups, `group_article_manager` and `group_article_reader`. Both security groups inherits from `base.group_user`. The security groups are in [security.xml](security/security.xml) file with access rights in [ir.model.access.csv](security/ir.model.access.csv) file.

# API Endpoints
The module has 4 API endpoints. Users must be authenticated using Odoo standand auth URL `/web/session/authenticate` and receieve a `session_id` to be used in subsequent request headers to consume the API. The API accept a json object in format `{"jsonrpc":"2.0","params":{"db":"odooxyzdb","login":"xyz","password":"******"}}` for authentication. After authentication, the `params` key should hold field keys and values. The API endpoints are given below:

   # Create API
   The create API endpoint is `/api/article_manager/create`. Article Managers can post the following Mandatory fields during article creation:
   - `title`
   - `publish_date`
   - `deadline`
   - `assigned_to`
   - `content`
   - On successful creation, the API will respond with the `create_id` which is id of the created record in model `article.article`.

   # Fetch API
   The Fetch API will pull all records available in `article.article` model. Records retrieved will be based on user's group and security policy. The API endpoint is `/api/article_manager/fetch`. A success fetch will give the below field values for each record in the database.
   - `id`
   - `title`
   - `author`
   - `assigned_to`
   - `publish_date`
   - `deadline`
   - `start_date`
   - `finished_date`
   - `state`
   - `content`
   - `image`
   - Note: `image` is a base64 encoded string.

   # Update API
   The update API endpoint is `/api/article_manager/update/<int:rec_id>`. Users must supply the id which is `rec_id` of the record to update including parameters fields to the endpoint. The author field cannot be updated, so sending an `author` id is inconsequential. The update api once succeeded will respond with a success json.

   # Delete API
   The delete API endpoint is `/api/article_manager/delete/<int:rec_id>`. Users must supply the id which is `rec_id` of the record to delete. Only Authenticated Article Managers will receive a success response upon consumation of the endpoint.

# Usage of Module
After installation of module, users must either be assigned to either a `group_article_manager` or a `group_article_reader` to have access to the module icon on their main home dashboard.
