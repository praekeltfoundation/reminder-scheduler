Quick Replies
-------------
This adds functionality to be able to handle quick reply messages from WhatsApp.

The way it achieves this is:
- If a message is a quick reply, it changes it to a normal text message, and then 
forwards it on to the configured URL.
- If a message is not a quick reply, it will get forwarded to the configured URL

All message forwarding happens through celery tasks, so if the upstream service can't
handle the load, then we will become the buffer. This is not ideal, but better than
holding up the web worker waiting for an HTTP response.

It supports multi-tenancy, with the configuration for each tenant being stored as a row
in the database.
