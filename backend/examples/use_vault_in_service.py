"""
Example: Using Secrets Vault in Backend Services
Demonstrates how to replace os.getenv() with vault.get_secret()
"""

from backend.security.secure_credential_vault import credential_vault
import os


# ============================================================================
# BEFORE (Unsafe - secrets in .env)
# ============================================================================

class OldLearningService:
    """Old approach - reads from environment variables"""
    
    def __init__(self):
        # ❌ Plain text in environment
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.github_token = os.getenv("GITHUB_TOKEN")
        
        # Problems:
        # - Secrets in plain text
        # - No access control
        # - No audit trail
        # - Easy to leak in logs


# ============================================================================
# AFTER (Secure - secrets from vault)
# ============================================================================

class NewLearningService:
    """New approach - retrieves from encrypted vault"""
    
    def __init__(self):
        self.openai_key = None
        self.github_token = None
    
    async def initialize(self):
        """Load secrets from vault on startup"""
        
        # ✅ Encrypted at rest
        # ✅ Access logged
        # ✅ Governance enforced
        self.openai_key = await credential_vault.get_secret("OPENAI_API_KEY")
        self.github_token = await credential_vault.get_secret("GITHUB_TOKEN")
        
        print(f"[Service] Secrets loaded from vault (access logged)")
    
    async def use_openai(self):
        """Use OpenAI API with vault-retrieved key"""
        if not self.openai_key:
            await self.initialize()
        
        # Use the key
        import openai
        openai.api_key = self.openai_key
        
        # Access is logged to immutable audit trail:
        # - Who: service identity
        # - What: retrieved OPENAI_API_KEY
        # - When: timestamp
        # - Why: for learning operation


# ============================================================================
# Example: Autonomous Curriculum (Real Integration)
# ============================================================================

class AutonomousCurriculumWithVault:
    """
    Real example from backend/learning_systems/autonomous_curriculum.py
    """
    
    async def _get_openai_key(self):
        """Retrieve OpenAI key from vault"""
        
        # Try vault first (secure)
        try:
            key = await credential_vault.get_secret("OPENAI_API_KEY")
            if key:
                return key
        except Exception as e:
            print(f"[Curriculum] Vault retrieval failed: {e}")
        
        # Fallback to env (for backwards compatibility)
        key = os.getenv("OPENAI_API_KEY")
        if key:
            print("[Curriculum] WARNING: Using OPENAI_API_KEY from .env (not secure)")
            return key
        
        raise ValueError("OPENAI_API_KEY not found in vault or environment")
    
    async def generate_lesson(self, topic: str):
        """Generate lesson using OpenAI"""
        
        # Get key securely
        api_key = await self._get_openai_key()
        
        # Use it (never log the key!)
        import openai
        openai.api_key = api_key
        
        # Generate content
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": f"Teach me about {topic}"}]
        )
        
        return response.choices[0].message.content


# ============================================================================
# Example: GitHub Knowledge Miner (Real Integration)
# ============================================================================

class GitHubKnowledgeMinerWithVault:
    """
    Real example from backend/knowledge/github_knowledge_miner.py
    """
    
    async def get_github_token(self):
        """Get GitHub token from vault"""
        
        # Try vault first
        try:
            token = await credential_vault.get_secret("GITHUB_TOKEN")
            if token:
                print("[GitHub] Token retrieved from vault (access logged)")
                return token
        except Exception as e:
            print(f"[GitHub] Vault retrieval failed: {e}")
        
        # Fallback to environment
        token = os.getenv("GITHUB_TOKEN")
        if token:
            print("[GitHub] WARNING: Using GITHUB_TOKEN from .env")
            return token
        
        print("[GitHub] No token available - public API only")
        return None
    
    async def fetch_repository(self, repo: str):
        """Fetch repository data"""
        
        token = await self.get_github_token()
        
        headers = {}
        if token:
            headers["Authorization"] = f"token {token}"
        
        # Use GitHub API
        # ...


# ============================================================================
# Example: Web Search with Vault
# ============================================================================

class WebSearchWithVault:
    """Secure web search with vault-retrieved keys"""
    
    async def search_google(self, query: str):
        """Google search with API key from vault"""
        
        # Get key securely
        api_key = await credential_vault.get_secret("GOOGLE_SEARCH_KEY")
        search_engine_id = await credential_vault.get_secret("GOOGLE_SEARCH_ENGINE_ID")
        
        # Make API request
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "key": api_key,
                    "cx": search_engine_id,
                    "q": query,
                }
            )
            
            return response.json()


# ============================================================================
# Example: Conditional Access (Domain-based)
# ============================================================================

async def get_secret_with_domain_check(secret_name: str, required_domain: str):
    """
    Get secret only if it matches required domain
    Useful for RBAC and security
    """
    
    # Get secret metadata first
    metadata = await credential_vault.get_secret_metadata(secret_name)
    
    # Check domain
    if metadata.get("domain") != required_domain:
        raise PermissionError(
            f"Secret '{secret_name}' not available for domain '{required_domain}'"
        )
    
    # Get actual value
    value = await credential_vault.get_secret(secret_name)
    return value


# ============================================================================
# Example: Startup Initialization
# ============================================================================

async def initialize_service_with_vault():
    """
    Initialize service with secrets from vault
    Call this on startup
    """
    
    print("[Service] Initializing with vault secrets...")
    
    # Load all required secrets
    secrets = {
        "openai": await credential_vault.get_secret("OPENAI_API_KEY"),
        "github": await credential_vault.get_secret("GITHUB_TOKEN"),
        "search": await credential_vault.get_secret("GOOGLE_SEARCH_KEY"),
    }
    
    # Configure services
    import openai
    openai.api_key = secrets["openai"]
    
    print("[Service] ✅ All secrets loaded from vault")
    print("[Service] ✅ Access logged to audit trail")
    
    return secrets


# ============================================================================
# Usage in main.py or service startup
# ============================================================================

# In backend/main.py or serve.py
"""
@app.on_event("startup")
async def startup_event():
    # Initialize vault-based services
    await initialize_service_with_vault()
    
    # Services now have secure access to credentials
    print("[Backend] ✅ Vault-based services initialized")
"""
