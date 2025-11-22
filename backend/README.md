# Grace 3.0 - Backend Setup Guide

## Prerequisites

1. **PostgreSQL** (version 12+)
2. **Redis** (version 6+)
3. **Python** (version 3.9+)

---

## Installation Steps

### 1. Install PostgreSQL

**Windows:**
```powershell
# Download from https://www.postgresql.org/download/windows/
# Or use Chocolatey:
choco install postgresql

# Start PostgreSQL service
net start postgresql-x64-14
```

**Create Database:**
```powershell
# Open psql
psql -U postgres

# In psql:
CREATE DATABASE grace_memory;
\q
```

### 2. Install Redis

**Windows:**
```powershell
# Download from https://github.com/microsoftarchive/redis/releases
# Or use Chocolatey:
choco install redis-64

# Start Redis service
redis-server
```

### 3. Set Up Python Environment

```powershell
# Navigate to backend directory
cd c:\Users\aaron\grace_2\backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment

```powershell
# Copy example env file
copy .env.example .env

# Edit .env file with your credentials
notepad .env
```

**Update these values in `.env`:**
```
DATABASE_PASSWORD=your_postgres_password
```

### 5. Initialize Database

```powershell
# Run schema SQL
psql -U postgres -d grace_memory -f database/schema.sql
```

### 6. Start the Backend Server

```powershell
# Make sure virtual environment is activated
.\venv\Scripts\activate

# Run server
python server.py
```

You should see:
```
🚀 Grace 3.0 Librarian API starting on port 5000...
📊 PostgreSQL: grace_memory@localhost
⚡ Redis: localhost:6379
 * Running on http://0.0.0.0:5000
```

---

## API Endpoints

### Health Check
- `GET /api/health` - Check system health

### Lightning Layer (Volatile)
- `POST /api/librarian/lightning` - Add item to Lightning
- `GET /api/librarian/lightning` - Get all Lightning items
- `GET /api/librarian/lightning/<id>` - Get specific Lightning item
- `DELETE /api/librarian/lightning/<id>` - Delete Lightning item

### Fusion Layer (Durable)
- `POST /api/librarian/fusion` - Add item to Fusion
- `GET /api/librarian/fusion` - Get all Fusion items
- `GET /api/librarian/fusion/<id>` - Get specific Fusion item

### Operations
- `POST /api/librarian/promote` - Promote from Lightning to Fusion
- `POST /api/librarian/rename` - Rename artifact
- `GET /api/librarian/stats` - Get statistics

---

## Testing

### 1. Test Health Check
```powershell
curl http://localhost:5000/api/health
```

### 2. Test Lightning Storage
```powershell
curl -X POST http://localhost:5000/api/librarian/lightning `
  -H "Content-Type: application/json" `
  -d '{
    "id": "ART-test-001",
    "name": "test_file.txt",
    "type": "file",
    "layer": "lightning",
    "dna": {
      "artifactId": "ART-test-001",
      "versionId": "VER-test-001",
      "origin": "User",
      "timestamp": "2025-11-22T09:00:00",
      "intent": "Testing",
      "checksum": "abc123",
      "lifecycle": [
        {
          "timestamp": "2025-11-22T09:00:00",
          "action": "Created",
          "actor": "User",
          "description": "Test item"
        }
      ]
    }
  }'
```

### 3. Test Fusion Storage
```powershell
curl http://localhost:5000/api/librarian/fusion
```

---

## Troubleshooting

### PostgreSQL Connection Error
```
Error: could not connect to server
```
**Solution:** Make sure PostgreSQL service is running:
```powershell
net start postgresql-x64-14
```

### Redis Connection Error
```
Error: Error 10061 connecting to localhost:6379
```
**Solution:** Make sure Redis is running:
```powershell
redis-server
```

### Port Already in Use
```
Error: Address already in use
```
**Solution:** Change the port in `.env`:
```
FLASK_PORT=5001
```

---

## Production Deployment

### Using Gunicorn (Linux/Mac)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 server:app
```

### Using Waitress (Windows)
```powershell
pip install waitress
waitress-serve --port=5000 server:app
```

---

## Monitoring

### Check Redis Keys
```powershell
redis-cli
> KEYS lightning:*
> TTL lightning:ART-xxx
```

### Check PostgreSQL Data
```powershell
psql -U postgres -d grace_memory
> SELECT COUNT(*) FROM fusion_artifacts;
> SELECT * FROM lifecycle_events ORDER BY created_at DESC LIMIT 10;
```

---

## Next Steps

1. Start the backend server
2. Update frontend `LibrarianService.ts` to use API endpoints
3. Test the full flow: Lightning → Promotion → Fusion
4. Monitor logs and performance
