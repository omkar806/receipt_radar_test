from fastapi import APIRouter, HTTPException
from models.schemas import GmailQueryRequest, GmailResponse
from services.gmail_service import GmailService
from constants import G_QUERY
router = APIRouter()

@router.post("/extract-emails", response_model=GmailResponse)
async def extract_emails(request: GmailQueryRequest):
    try:
        gmail_service = GmailService(request.access_token)
        
        # Get messages matching the query
        result = gmail_service.list_messages(
            query=G_QUERY
        )
        print("Printing result")
        print(result)
        print(f"{len(result['messages'])} messages found!")
        if not result.get('messages'):
            return GmailResponse(
                success=True,
                message="No messages found",
                emails=[],
                next_page_token=result.get('nextPageToken')
            )
        
        # Process messages in batches
        emails = gmail_service.process_message_batch(result['messages'])
        print("Completed Processing the message!")
        return GmailResponse(
            success=True,
            message=f"Successfully extracted {len(emails)} emails",
            emails=emails,
            next_page_token=result.get('nextPageToken')
        )
        return GmailResponse(
                success=True,
                message="No messages found",
                emails=[],
                next_page_token=result.get('nextPageToken')
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
