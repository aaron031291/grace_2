"""Tests for AI Coding Agent System"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import tempfile
import os

from backend.code_memory import code_memory, CodePattern
from backend.code_understanding import code_understanding
from backend.code_generator import code_generator
from backend.dev_workflow import dev_workflow
from backend.models import engine, Base, async_session

@pytest.fixture
async def setup_database():
    """Setup test database"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def sample_python_code():
    """Sample Python code for testing"""
    return '''
def calculate_total(price: float, tax_rate: float = 0.1) -> float:
    """Calculate total price with tax
    
    Args:
        price: Base price
        tax_rate: Tax rate (default 10%)
    
    Returns:
        Total price including tax
    """
    return price * (1 + tax_rate)

class UserService:
    """Handle user operations"""
    
    def __init__(self, database):
        self.database = database
    
    def get_user(self, user_id: int):
        """Get user by ID"""
        return self.database.query(user_id)
'''

@pytest.fixture
def temp_code_file(sample_python_code):
    """Create temporary code file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(sample_python_code)
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)

class TestCodeMemory:
    """Test code memory system"""
    
    @pytest.mark.asyncio
    async def test_parse_python_file(self, setup_database, temp_code_file):
        """Test parsing Python file"""
        
        file_path = Path(temp_code_file)
        patterns = await code_memory.parse_file(
            file_path,
            language='python',
            project='test_project'
        )
        
        assert 'functions' in patterns
        assert 'classes' in patterns
        assert len(patterns['functions']) > 0
        assert len(patterns['classes']) > 0
    
    @pytest.mark.asyncio
    async def test_recall_patterns(self, setup_database):
        """Test pattern recall"""
        
        # Create test pattern
        async with async_session() as session:
            pattern = CodePattern(
                pattern_type='function',
                language='python',
                name='test_function',
                signature='def test_function()',
                code_snippet='def test_function():\n    pass',
                tags=['testing', 'example'],
                confidence_score=0.9
            )
            session.add(pattern)
            await session.commit()
        
        # Recall patterns
        patterns = await code_memory.recall_patterns(
            intent='testing function',
            language='python',
            limit=5
        )
        
        assert len(patterns) > 0
        assert patterns[0]['name'] == 'test_function'

class TestCodeUnderstanding:
    """Test code understanding engine"""
    
    @pytest.mark.asyncio
    async def test_analyze_context(self, setup_database, temp_code_file):
        """Test context analysis"""
        
        context = await code_understanding.analyze_current_context(
            file_path=temp_code_file,
            cursor_position={'line': 5, 'column': 10}
        )
        
        assert context['language'] == 'python'
        assert 'structure' in context
        assert context['structure']['function_count'] > 0
    
    @pytest.mark.asyncio
    async def test_understand_intent(self, setup_database):
        """Test intent understanding"""
        
        intent = await code_understanding.understand_intent(
            description="create user authentication API endpoint",
            context={'language': 'python'}
        )
        
        assert intent['intent_type'] == 'create'
        assert 'api' in intent['entities'] or 'authentication' in intent['entities']
        assert len(intent['implementation_steps']) > 0
    
    @pytest.mark.asyncio
    async def test_suggest_next_steps(self, setup_database):
        """Test next step suggestions"""
        
        context = {
            'current_scope': {
                'type': 'function',
                'name': 'test_function',
                'has_docstring': False
            },
            'language': 'python'
        }
        
        suggestions = await code_understanding.suggest_next_steps(context)
        
        assert len(suggestions) > 0
        # Should suggest adding docstring
        assert any(s['type'] == 'add_docstring' for s in suggestions)

class TestCodeGenerator:
    """Test code generator"""
    
    @pytest.mark.asyncio
    async def test_generate_function(self, setup_database):
        """Test function generation"""
        
        spec = {
            'name': 'calculate_discount',
            'description': 'Calculate discount amount',
            'parameters': [
                {'name': 'price', 'type': 'float'},
                {'name': 'discount_rate', 'type': 'float'}
            ],
            'return_type': 'float'
        }
        
        result = await code_generator.generate_function(
            spec=spec,
            language='python',
            use_patterns=False
        )
        
        assert 'code' in result
        assert 'def calculate_discount' in result['code']
        assert 'price: float' in result['code']
    
    @pytest.mark.asyncio
    async def test_generate_class(self, setup_database):
        """Test class generation"""
        
        spec = {
            'name': 'ProductService',
            'description': 'Handle product operations',
            'attributes': [
                {'name': 'db', 'type': 'Database'}
            ],
            'methods': [
                {
                    'name': 'get_product',
                    'params': [{'name': 'product_id', 'type': 'int'}],
                    'return_type': 'Product'
                }
            ]
        }
        
        result = await code_generator.generate_class(
            spec=spec,
            language='python'
        )
        
        assert 'code' in result
        assert 'class ProductService' in result['code']
        assert 'def __init__' in result['code']
        assert 'def get_product' in result['code']
    
    @pytest.mark.asyncio
    async def test_generate_tests(self, setup_database, sample_python_code):
        """Test test generation"""
        
        result = await code_generator.generate_tests(
            code=sample_python_code,
            framework='pytest',
            language='python'
        )
        
        assert 'test_code' in result
        assert 'def test_' in result['test_code']
        assert 'import pytest' in result['test_code']
    
    @pytest.mark.asyncio
    async def test_fix_errors(self, setup_database):
        """Test error fixing"""
        
        code_with_error = "def test():\nundefined_variable"
        errors = [
            {
                'line': 2,
                'message': "name 'undefined_variable' is not defined",
                'type': 'NameError'
            }
        ]
        
        result = await code_generator.fix_errors(
            code=code_with_error,
            errors=errors,
            language='python'
        )
        
        assert 'fixed_code' in result
        assert 'fixes_applied' in result

class TestDevWorkflow:
    """Test development workflow"""
    
    @pytest.mark.asyncio
    async def test_parse_task(self, setup_database):
        """Test task parsing"""
        
        task = await dev_workflow.parse_task(
            natural_language="implement user login API endpoint"
        )
        
        assert 'task_id' in task
        assert 'intent' in task
        assert task['task_type'] in ['implement_api', 'create_feature']
    
    @pytest.mark.asyncio
    async def test_plan_implementation(self, setup_database):
        """Test implementation planning"""
        
        task = {
            'task_id': 'test_task_001',
            'description': 'Create user authentication',
            'task_type': 'implement_api',
            'intent': {
                'intent_type': 'create',
                'entities': ['user', 'authentication', 'api'],
                'implementation_steps': []
            }
        }
        
        plan = await dev_workflow.plan_implementation(task)
        
        assert 'steps' in plan
        assert len(plan['steps']) > 0
        assert 'estimated_duration' in plan
        assert 'risk_level' in plan
    
    @pytest.mark.asyncio
    async def test_track_progress(self, setup_database):
        """Test progress tracking"""
        
        # First create a task
        task = await dev_workflow.parse_task(
            natural_language="create simple function"
        )
        plan = await dev_workflow.plan_implementation(task)
        
        # Track progress
        progress = await dev_workflow.track_progress(task['task_id'])
        
        # Should show no progress initially
        assert 'status' in progress or 'error' in progress

class TestIntegration:
    """Integration tests"""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, setup_database, temp_code_file):
        """Test complete workflow: parse -> understand -> generate -> test"""
        
        # 1. Parse existing code into memory
        file_path = Path(temp_code_file)
        patterns = await code_memory.parse_file(
            file_path,
            language='python',
            project='test'
        )
        
        assert len(patterns['functions']) > 0
        
        # 2. Understand intent
        intent = await code_understanding.understand_intent(
            description="add error handling to calculate_total function"
        )
        
        assert intent['intent_type'] in ['create', 'update', 'fix']
        
        # 3. Generate code
        spec = {
            'name': 'calculate_total_safe',
            'description': 'Calculate total with error handling',
            'parameters': [
                {'name': 'price', 'type': 'float'}
            ],
            'return_type': 'float'
        }
        
        result = await code_generator.generate_function(
            spec=spec,
            language='python'
        )
        
        assert 'code' in result
        
        # 4. Generate tests
        test_result = await code_generator.generate_tests(
            code=result['code'],
            framework='pytest'
        )
        
        assert 'test_code' in test_result
    
    @pytest.mark.asyncio
    async def test_pattern_recall_quality(self, setup_database, sample_python_code):
        """Test that recalled patterns are relevant"""
        
        # Parse sample code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(sample_python_code)
            temp_path = f.name
        
        try:
            patterns = await code_memory.parse_file(
                Path(temp_path),
                language='python',
                project='test'
            )
            
            # Recall patterns related to "calculate price"
            recalled = await code_memory.recall_patterns(
                intent='calculate price with tax',
                language='python',
                limit=5
            )
            
            # Should recall the calculate_total function
            assert len(recalled) > 0
            # Check confidence scores
            for pattern in recalled:
                assert pattern['confidence'] > 0
        
        finally:
            os.unlink(temp_path)

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
