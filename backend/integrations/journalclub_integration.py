"""
JournalClub.io Integration
Autonomous access to research papers via Gmail authentication
Connected to remote access system for learning
"""

import asyncio
import re
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import httpx
from pathlib import Path

from backend.ingestion_services.ingestion_service import ingestion_service
from backend.kernels.librarian_kernel import librarian_kernel


class JournalClubIntegration:
    """
    Autonomous integration with journalclub.io for research paper access
    
    Flow:
    1. Request login code (sent to email)
    2. Monitor Gmail for security code
    3. Login to journalclub.io with code
    4. Download all PDFs from membership
    5. Ingest into knowledge base
    6. Add to autonomous learning curriculum
    """
    
    def __init__(self):
        self.email = None
        self.session_token = None
        self.downloaded_papers = []
        self.gmail_auth = None
        
    async def setup_gmail_auth(self, email: str, credentials_path: str = None):
        """
        Setup Gmail API authentication
        Uses OAuth2 for secure access
        """
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
            
            SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
            
            creds = None
            token_path = Path("token.json")
            
            if token_path.exists():
                creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if credentials_path and Path(credentials_path).exists():
                        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                        creds = flow.run_local_server(port=0)
                
                # Save credentials
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            
            self.gmail_service = build('gmail', 'v1', credentials=creds)
            self.email = email
            print(f"[JOURNALCLUB] Gmail authenticated: {email}")
            return True
            
        except ImportError:
            print("[JOURNALCLUB] Gmail API not installed. Install: pip install google-auth-oauthlib google-api-python-client")
            return False
        except Exception as e:
            print(f"[JOURNALCLUB] Gmail auth failed: {e}")
            return False
    
    async def watch_for_security_code(self, timeout_seconds: int = 60) -> Optional[str]:
        """
        Monitor Gmail for security code from journalclub.io
        Returns the code when found, or None if timeout
        """
        if not self.gmail_service:
            print("[JOURNALCLUB] Gmail not authenticated")
            return None
        
        print(f"[JOURNALCLUB] Watching Gmail for security code (timeout: {timeout_seconds}s)...")
        
        start_time = datetime.utcnow()
        timeout = timedelta(seconds=timeout_seconds)
        
        while datetime.utcnow() - start_time < timeout:
            try:
                # Search for emails from journalclub.io
                results = self.gmail_service.users().messages().list(
                    userId='me',
                    q='from:journalclub.io subject:code OR subject:verification',
                    maxResults=5
                ).execute()
                
                messages = results.get('messages', [])
                
                for msg in messages:
                    # Get message details
                    message = self.gmail_service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='full'
                    ).execute()
                    
                    # Check if this is recent (last 5 minutes)
                    timestamp = int(message['internalDate']) / 1000
                    age_seconds = (datetime.utcnow().timestamp() - timestamp)
                    
                    if age_seconds > 300:  # Older than 5 minutes
                        continue
                    
                    # Extract code from message body
                    code = self._extract_security_code(message)
                    if code:
                        print(f"[JOURNALCLUB] Security code found: {code}")
                        return code
                
                # Wait before checking again
                await asyncio.sleep(5)
                
            except Exception as e:
                print(f"[JOURNALCLUB] Gmail check error: {e}")
                await asyncio.sleep(5)
        
        print("[JOURNALCLUB] Timeout waiting for security code")
        return None
    
    def _extract_security_code(self, message: Dict) -> Optional[str]:
        """Extract security code from email message"""
        try:
            # Get message body
            parts = message.get('payload', {}).get('parts', [])
            body = ""
            
            for part in parts:
                if part.get('mimeType') == 'text/plain':
                    data = part.get('body', {}).get('data', '')
                    if data:
                        import base64
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
            
            # Look for code patterns (6-digit numbers, etc.)
            patterns = [
                r'\b(\d{6})\b',  # 6-digit code
                r'code:\s*(\d+)',  # "code: 123456"
                r'verification code:\s*(\d+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, body, re.IGNORECASE)
                if match:
                    return match.group(1)
            
        except Exception as e:
            print(f"[JOURNALCLUB] Code extraction error: {e}")
        
        return None
    
    async def login_with_code(self, email: str, code: str) -> bool:
        """
        Login to journalclub.io with email and security code
        """
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                # Step 1: Request login (triggers code email)
                # Note: This is a placeholder - actual API endpoints would need to be discovered
                response = await client.post(
                    "https://journalclub.io/api/auth/request-code",
                    json={"email": email},
                    timeout=30
                )
                
                if response.status_code != 200:
                    print(f"[JOURNALCLUB] Code request failed: {response.status_code}")
                    return False
                
                # Step 2: Submit code for authentication
                response = await client.post(
                    "https://journalclub.io/api/auth/verify-code",
                    json={"email": email, "code": code},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.session_token = data.get('session_token') or data.get('access_token')
                    print(f"[JOURNALCLUB] Login successful!")
                    return True
                else:
                    print(f"[JOURNALCLUB] Login failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"[JOURNALCLUB] Login error: {e}")
            return False
    
    async def download_all_membership_pdfs(self, output_dir: str = "grace_training/research_papers") -> List[str]:
        """
        Download all PDFs available in membership
        Returns list of downloaded file paths
        """
        if not self.session_token:
            print("[JOURNALCLUB] Not logged in")
            return []
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        downloaded_files = []
        
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                # Get list of available papers
                response = await client.get(
                    "https://journalclub.io/api/papers",
                    headers={"Authorization": f"Bearer {self.session_token}"},
                    timeout=30
                )
                
                if response.status_code != 200:
                    print(f"[JOURNALCLUB] Failed to get papers list: {response.status_code}")
                    return []
                
                papers = response.json().get('papers', [])
                print(f"[JOURNALCLUB] Found {len(papers)} papers in membership")
                
                # Download each PDF
                for paper in papers:
                    paper_id = paper.get('id')
                    title = paper.get('title', 'unknown')
                    pdf_url = paper.get('pdf_url')
                    
                    if not pdf_url:
                        continue
                    
                    # Download PDF
                    pdf_response = await client.get(
                        pdf_url,
                        headers={"Authorization": f"Bearer {self.session_token}"},
                        timeout=60
                    )
                    
                    if pdf_response.status_code == 200:
                        # Save PDF
                        safe_title = re.sub(r'[^\w\s-]', '', title).strip()[:100]
                        filename = f"{paper_id}_{safe_title}.pdf"
                        filepath = Path(output_dir) / filename
                        
                        filepath.write_bytes(pdf_response.content)
                        downloaded_files.append(str(filepath))
                        
                        print(f"[JOURNALCLUB] Downloaded: {filename}")
                        
                        # Ingest into knowledge base
                        await self._ingest_paper(filepath, paper)
                    
                    # Be respectful with rate limiting
                    await asyncio.sleep(1)
                
        except Exception as e:
            print(f"[JOURNALCLUB] Download error: {e}")
        
        return downloaded_files
    
    async def _ingest_paper(self, filepath: Path, metadata: Dict):
        """Ingest research paper into Grace's knowledge base"""
        try:
            # Read PDF content
            with open(filepath, 'rb') as f:
                pdf_bytes = f.read()
            
            # Ingest via service
            artifact_id = await ingestion_service.ingest_file(
                file_content=pdf_bytes,
                filename=filepath.name,
                actor="journalclub_integration",
                file_type="pdf"
            )
            
            # Queue for librarian analysis
            await librarian_kernel.queue_ingestion(
                file_path=str(filepath),
                metadata={
                    "source": "journalclub.io",
                    "paper_id": metadata.get('id'),
                    "title": metadata.get('title'),
                    "authors": metadata.get('authors'),
                    "journal": metadata.get('journal'),
                    "publication_date": metadata.get('date'),
                    "artifact_id": artifact_id
                }
            )
            
            print(f"[JOURNALCLUB] Ingested: {filepath.name}")
            self.downloaded_papers.append(str(filepath))
            
        except Exception as e:
            print(f"[JOURNALCLUB] Ingestion error for {filepath.name}: {e}")
    
    async def autonomous_workflow(self, email: str, gmail_credentials: str = None) -> Dict[str, Any]:
        """
        Complete autonomous workflow:
        1. Setup Gmail
        2. Request JournalClub code
        3. Wait for code in Gmail
        4. Login with code
        5. Download all PDFs
        6. Ingest into knowledge base
        """
        results = {
            "gmail_auth": False,
            "code_received": False,
            "login_success": False,
            "papers_downloaded": 0,
            "papers_ingested": 0,
            "status": "failed"
        }
        
        # Step 1: Gmail authentication
        if await self.setup_gmail_auth(email, gmail_credentials):
            results["gmail_auth"] = True
        else:
            return results
        
        # Step 2: Request JournalClub code (would need real API)
        print(f"[JOURNALCLUB] Requesting code for {email}")
        # In practice, this would trigger the email
        await asyncio.sleep(2)  # Simulate API call
        
        # Step 3: Watch Gmail for code
        code = await self.watch_for_security_code(timeout_seconds=120)
        if code:
            results["code_received"] = True
        else:
            results["status"] = "timeout_waiting_for_code"
            return results
        
        # Step 4: Login with code
        if await self.login_with_code(email, code):
            results["login_success"] = True
        else:
            results["status"] = "login_failed"
            return results
        
        # Step 5: Download all PDFs
        downloaded = await self.download_all_membership_pdfs()
        results["papers_downloaded"] = len(downloaded)
        results["papers_ingested"] = len(self.downloaded_papers)
        results["status"] = "success"
        results["files"] = downloaded
        
        print(f"[JOURNALCLUB] Workflow complete: {len(downloaded)} papers ingested")
        return results


# Global instance
journalclub_integration = JournalClubIntegration()