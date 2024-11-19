import base64
import email
from bs4 import BeautifulSoup
import os
from models.schemas import EmailMessage, EmailAttachment

class EmailParser:
    @staticmethod
    def extract_domain(email_address: str) -> str:
        """Extract domain from email address"""
        try:
            return email_address.split('@')[1]
        except:
            return ''

    @staticmethod
    def decode_body(part) -> str:
        """Decode email body"""
        if part['body'].get('data'):
            return base64.urlsafe_b64decode(
                part['body']['data'].encode('ASCII')
            ).decode('utf-8')
        return ''

    @staticmethod
    def get_attachment_data(part) -> dict:
        """Extract attachment data"""
        if 'data' in part['body']:
            data = part['body']['data']
        else:
            att_id = part['body']['attachmentId']
            return {'attachment_id': att_id}
        return {
            'data': base64.urlsafe_b64decode(data.encode('ASCII')),
            'size': part['body']['size']
        }

    @staticmethod
    def is_pdf(filename: str) -> bool:
        """Check if file is PDF based on extension"""
        return filename.lower().endswith('.pdf')