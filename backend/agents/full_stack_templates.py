"""
Full-Stack Project Templates
Provides scaffolding for common application stacks.
"""

from typing import Dict, List
from pathlib import Path

class ProjectTemplate:
    """Base class for project templates"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def get_structure(self) -> Dict[str, str]:
        """Returns dict of {file_path: content}"""
        raise NotImplementedError
    
    def get_dependencies(self) -> Dict[str, List[str]]:
        """Returns dict of {package_manager: [packages]}"""
        raise NotImplementedError
    
    def get_run_command(self) -> str:
        """Returns command to start the app"""
        raise NotImplementedError

class PythonCLITemplate(ProjectTemplate):
    """Simple Python CLI application"""
    
    def __init__(self):
        super().__init__("python-cli", "Python command-line application")
    
    def get_structure(self) -> Dict[str, str]:
        return {
            "main.py": '''#!/usr/bin/env python3
"""
CLI Application
"""

def main():
    print("Hello from Grace!")
    
if __name__ == "__main__":
    main()
''',
            "requirements.txt": "# Add dependencies here\n",
            "README.md": "# Python CLI App\n\nBuilt by Grace AI\n"
        }
    
    def get_dependencies(self) -> Dict[str, List[str]]:
        return {"pip": []}
    
    def get_run_command(self) -> str:
        return "python main.py"

class ReactFastAPITemplate(ProjectTemplate):
    """React frontend + FastAPI backend"""
    
    def __init__(self):
        super().__init__("react-fastapi", "Full-stack web app with React + FastAPI")
    
    def get_structure(self) -> Dict[str, str]:
        return {
            # Backend
            "backend/main.py": '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Grace App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.get("/api/data")
async def get_data():
    return {"message": "Hello from Grace!"}
''',
            "backend/requirements.txt": "fastapi\nuvicorn[standard]\n",
            
            # Frontend
            "frontend/package.json": '''{
  "name": "grace-app",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.0.0",
    "vite": "^4.3.0"
  }
}''',
            "frontend/index.html": '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grace App</title>
</head>
<body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
</body>
</html>''',
            "frontend/src/main.jsx": '''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)''',
            "frontend/src/App.jsx": '''import { useState, useEffect } from 'react'

function App() {
  const [data, setData] = useState(null)
  
  useEffect(() => {
    fetch('http://localhost:8000/api/data')
      .then(r => r.json())
      .then(setData)
  }, [])
  
  return (
    <div style={{ padding: '2rem' }}>
      <h1>Grace App</h1>
      <p>{data ? data.message : 'Loading...'}</p>
    </div>
  )
}

export default App''',
            "frontend/vite.config.js": '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: { port: 3000 }
})''',
            "README.md": '''# Full-Stack App

Built by Grace AI

## Setup
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```
'''
        }
    
    def get_dependencies(self) -> Dict[str, List[str]]:
        return {
            "pip": ["fastapi", "uvicorn[standard]"],
            "npm": ["react", "react-dom", "vite", "@vitejs/plugin-react"]
        }
    
    def get_run_command(self) -> str:
        return "cd backend && uvicorn main:app --reload --port 8000 & cd frontend && npm run dev"

class BlockchainTemplate(ProjectTemplate):
    """Simple blockchain implementation"""
    
    def __init__(self):
        super().__init__("blockchain", "Basic blockchain with proof-of-work")
    
    def get_structure(self) -> Dict[str, str]:
        return {
            "blockchain.py": '''import hashlib
import json
from time import time
from typing import List, Dict, Any

class Blockchain:
    def __init__(self):
        self.chain: List[Dict] = []
        self.current_transactions: List[Dict] = []
        # Create genesis block
        self.new_block(previous_hash='1', proof=100)
    
    def new_block(self, proof: int, previous_hash: str = None) -> Dict:
        """Create a new block"""
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        return block
    
    def new_transaction(self, sender: str, recipient: str, amount: float) -> int:
        """Add a new transaction"""
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block['index'] + 1
    
    @staticmethod
    def hash(block: Dict) -> str:
        """Hash a block"""
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    @property
    def last_block(self) -> Dict:
        return self.chain[-1]
    
    def proof_of_work(self, last_proof: int) -> int:
        """Simple proof of work"""
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof
    
    @staticmethod
    def valid_proof(last_proof: int, proof: int) -> bool:
        """Validate proof"""
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

# Demo
if __name__ == "__main__":
    blockchain = Blockchain()
    blockchain.new_transaction("Alice", "Bob", 10)
    blockchain.new_transaction("Bob", "Charlie", 5)
    
    last_proof = blockchain.last_block['proof']
    proof = blockchain.proof_of_work(last_proof)
    blockchain.new_block(proof)
    
    print("Blockchain:")
    for block in blockchain.chain:
        print(f"Block {block['index']}: {len(block['transactions'])} transactions")
''',
            "README.md": "# Blockchain\n\nBuilt by Grace AI\n\nRun: `python blockchain.py`\n"
        }
    
    def get_dependencies(self) -> Dict[str, List[str]]:
        return {"pip": []}
    
    def get_run_command(self) -> str:
        return "python blockchain.py"

class FlaskAPITemplate(ProjectTemplate):
    """Simple Flask REST API"""
    
    def __init__(self):
        super().__init__("flask-api", "Flask REST API with SQLite")
    
    def get_structure(self) -> Dict[str, str]:
        return {
            "app.py": '''from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

def get_db():
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS items
                    (id INTEGER PRIMARY KEY, name TEXT, value TEXT)""")
    conn.commit()
    conn.close()

@app.route('/api/items', methods=['GET'])
def get_items():
    conn = get_db()
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()
    return jsonify([dict(item) for item in items])

@app.route('/api/items', methods=['POST'])
def create_item():
    data = request.json
    conn = get_db()
    cursor = conn.execute('INSERT INTO items (name, value) VALUES (?, ?)',
                         (data['name'], data['value']))
    conn.commit()
    item_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': item_id}), 201

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
''',
            "requirements.txt": "flask\nflask-cors\n",
            "README.md": "# Flask API\n\nBuilt by Grace AI\n\nRun: `python app.py`\n"
        }
    
    def get_dependencies(self) -> Dict[str, List[str]]:
        return {"pip": ["flask", "flask-cors"]}
    
    def get_run_command(self) -> str:
        return "python app.py"

# Template registry
TEMPLATES = {
    "python-cli": PythonCLITemplate(),
    "react-fastapi": ReactFastAPITemplate(),
    "blockchain": BlockchainTemplate(),
    "flask-api": FlaskAPITemplate(),
}

def get_template(name: str) -> ProjectTemplate:
    """Get a template by name"""
    return TEMPLATES.get(name)

def list_templates() -> List[str]:
    """List available templates"""
    return list(TEMPLATES.keys())
