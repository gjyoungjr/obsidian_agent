import os

import resend

resend.api_key = os.getenv("RESEND_API_KEY")

params: resend.Emails.SendParams = {
    "from": "onboarding@resend.dev",
    "to": ["delivered@resend.dev"],
    "subject": "hi",
    "html": "<strong>hello, world!</strong>",
    "reply_to": "to@gmail.com",
    "bcc": "bcc@resend.dev",
    "cc": ["cc@resend.dev"],
    "tags": [
        {"name": "tag1", "value": "tagvalue1"},
        {"name": "tag2", "value": "tagvalue2"},
    ],
}

email: resend.Emails.SendResponse = resend.Emails.send(params)
print(email)
