"""Analyze the ingestion_service.py for variable scope issues"""
import ast
import sys

# Read the file
with open("backend/ingestion_services/ingestion_service.py", "r") as f:
    source = f.read()

# Parse it
tree = ast.parse(source)

# Find the ingest method
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "ingest":
        print(f"Found ingest method at line {node.lineno}")
        print(f"Method spans lines {node.lineno} to {node.end_lineno}")
        
        # Look for variable assignments and references
        assignments = set()
        references = set()
        
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                if isinstance(child.ctx, ast.Store):
                    assignments.add(child.id)
                elif isinstance(child.ctx, ast.Load):
                    references.add(child.id)
        
        print(f"\nVariables assigned: {sorted(assignments)}")
        print(f"\nVariables referenced: {sorted(references)}")
        
        # Find variables referenced but not assigned
        unassigned = references - assignments - {'self', 'content', 'artifact_type', 'title', 'actor', 'source', 'domain', 'tags', 'metadata'}
        if unassigned:
            print(f"\n⚠️  Variables referenced but never assigned: {sorted(unassigned)}")
        
        break
