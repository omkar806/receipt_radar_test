from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
from utils.email_parser import EmailParser
from models.schemas import EmailMessage, EmailAttachment
from config import settings
import os
import base64
from email.utils import parseaddr


class GmailService:
    def __init__(self, access_token: str):
        credentials = Credentials(access_token)
        self.service = build('gmail', 'v1', credentials=credentials)
        self.parser = EmailParser()

    def list_messages(self, query: str, page_token: Optional[str] = None) -> Dict:
        """List Gmail messages based on query"""
        try:
            return self.service.users().messages().list(
                userId='me',
                q=query,
                pageToken=page_token
            ).execute()
        except Exception as e:
            raise Exception(f"Error listing messages: {str(e)}")

    def get_message_detail(self, msg_id: str) -> EmailMessage:
        """Get detailed message content"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()

            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
            from_email = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')

            with open('logs.txt', 'a') as file:
                file.write("subject: \n"+str(subject)+"\n")
                file.write("from_email : \n"+str(from_email)+"\n")
                file.write("date : \n"+str(date)+"\n")

            # Extract email address from the "From" field
            _, from_email = parseaddr(from_email)
            from_domain = self.parser.extract_domain(from_email)

            html_body = ''
            plain_body = ''
            attachments = []

            def process_parts(parts):
                nonlocal html_body, plain_body, attachments
                
                for part in parts:
                    mime_type = part['mimeType']
                    
                    if 'parts' in part:
                        process_parts(part['parts'])
                    elif mime_type == 'text/html':
                        html_body = self.parser.decode_body(part)
                    elif mime_type == 'text/plain':
                        plain_body = self.parser.decode_body(part)
                    elif 'filename' in part:
                        filename = part['filename']
                        if self.parser.is_pdf(filename):
                            att_data = self.parser.get_attachment_data(part)
                            attachment = EmailAttachment(
                                filename=filename,
                                mime_type=mime_type,
                                size=att_data.get('size', 0),
                                content_id=part.get('contentId'),
                                data=att_data.get('data')
                            )
                            attachments.append(attachment)

            if 'parts' in message['payload']:
                process_parts(message['payload']['parts'])
            else:
                # Handle messages without parts
                mime_type = message['payload']['mimeType']
                if mime_type == 'text/html':
                    html_body = self.parser.decode_body(message['payload'])
                elif mime_type == 'text/plain':
                    plain_body = self.parser.decode_body(message['payload'])
            
            with open('logs.txt', 'a') as file:
                file.write("plain_body : \n"+str(plain_body)+"\n")
                file.write("attachments : \n"+str(attachments)+"\n")

            return EmailMessage(
                message_id=msg_id,
                subject=subject,
                from_email=from_email,
                from_domain=from_domain,
                date=date,
                html_body=html_body,
                plain_body=plain_body,
                attachments=attachments
            )

        except Exception as e:
            with open('logs.txt', 'a') as file:
                file.write("-----------------------------"+"Error : "+str(e)+"\n \n -----------------------------")

            raise Exception(f"Error getting message detail: {str(e)}")

    def process_message_batch(self, messages: List[Dict]) -> List[EmailMessage]:
        """Process a batch of messages concurrently"""
        with ThreadPoolExecutor(max_workers=settings.MAX_CONCURRENT_THREADS) as executor:
            future_to_msg = {
                executor.submit(self.get_message_detail, msg['id']): msg
                for msg in messages
            }
            
            results = []
            for future in as_completed(future_to_msg):
                try:
                    email_message = future.result()
                    results.append(email_message)
                except Exception as e:
                    print(f"Error processing message: {str(e)}")
                    continue
                    
        return results