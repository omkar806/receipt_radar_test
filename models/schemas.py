from pydantic import BaseModel
from typing import List, Optional, Dict

class EmailAttachment(BaseModel):
    filename: str
    mime_type: str
    size: int
    content_id: Optional[str]
    data: Optional[bytes]

class EmailMessage(BaseModel):
    message_id: str
    subject: Optional[str]
    from_email: str
    from_domain: str
    date: str
    html_body: Optional[str]
    plain_body: Optional[str]
    attachments: List[EmailAttachment] = []

class GmailQueryRequest(BaseModel):
    access_token: str
    user_id:str
    session_id : int
    # query: str
    # max_results: Optional[int] = 100

class GmailResponse(BaseModel):
    success: bool
    message: str
    emails: List[EmailMessage] = []
    next_page_token: Optional[str] = None