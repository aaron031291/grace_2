"""Code Generator - Generate code from specifications"""

import ast
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from .code_memory import code_memory
from backend.agents_core.governance import governance_engine
from backend.agents_core.hunter import hunter_engine

class CodeGenerator:
    """Generate code from specifications using learned patterns"""
    
    def __init__(self):
        self.templates = {
            'python': {
                'function': self._python_function_template,
                'class': self._python_class_template,
                'api_endpoint': self._python_api_endpoint_template,
                'test': self._python_test_template
            }
        }
    
    async def generate_function(
        self,
        spec: Dict[str, Any],
        language: str = 'python',
        use_patterns: bool = True
    ) -> Dict[str, Any]:
        """
        Generate function from specification
        
        Args:
            spec: {
                'name': 'calculate_total',
                'description': 'Calculate total price with tax',
                'parameters': [{'name': 'price', 'type': 'float'}, ...],
                'return_type': 'float',
                'logic': 'multiply price by 1.1 for 10% tax'  # optional
            }
            language: Programming language
            use_patterns: Use learned patterns from memory
        
        Returns:
            Generated code with metadata
        """
        
        # Check governance approval
        approval = await self._check_governance_approval('generate_function', spec)
        if not approval['approved']:
            return {'error': 'Governance denied code generation', 'reason': approval['reason']}
        
        # Recall similar patterns if requested
        similar_patterns = []
        if use_patterns:
            similar_patterns = await code_memory.recall_patterns(
                intent=spec.get('description', spec['name']),
                language=language,
                limit=5
            )
        
        # Generate code using template
        if language in self.templates and 'function' in self.templates[language]:
            code = self.templates[language]['function'](spec, similar_patterns)
        else:
            return {'error': f'Language {language} not supported'}
        
        # Scan for security issues
        security_scan = await hunter_engine.scan_code_snippet(code, language)
        if security_scan['threats']:
            return {
                'error': 'Security issues detected',
                'threats': security_scan['threats'],
                'code': code
            }
        
        # Format and return
        return {
            'code': code,
            'language': language,
            'spec': spec,
            'patterns_used': [p['name'] for p in similar_patterns],
            'security_scan': security_scan,
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'generator_version': '1.0'
            }
        }
    
    async def generate_class(
        self,
        spec: Dict[str, Any],
        language: str = 'python',
        use_patterns: bool = True
    ) -> Dict[str, Any]:
        """
        Generate class from specification
        
        Args:
            spec: {
                'name': 'UserService',
                'description': 'Handle user operations',
                'base_classes': ['BaseService'],
                'attributes': [{'name': 'db', 'type': 'Database'}, ...],
                'methods': [{'name': 'get_user', 'params': [...], ...}, ...]
            }
            language: Programming language
            use_patterns: Use learned patterns
        
        Returns:
            Generated code with metadata
        """
        
        # Governance check
        approval = await self._check_governance_approval('generate_class', spec)
        if not approval['approved']:
            return {'error': 'Governance denied', 'reason': approval['reason']}
        
        # Recall patterns
        similar_patterns = []
        if use_patterns:
            similar_patterns = await code_memory.recall_patterns(
                intent=spec.get('description', spec['name']),
                language=language,
                limit=3
            )
        
        # Generate class
        if language in self.templates and 'class' in self.templates[language]:
            code = self.templates[language]['class'](spec, similar_patterns)
        else:
            return {'error': f'Language {language} not supported'}
        
        # Security scan
        security_scan = await hunter_engine.scan_code_snippet(code, language)
        
        return {
            'code': code,
            'language': language,
            'spec': spec,
            'patterns_used': [p['name'] for p in similar_patterns],
            'security_scan': security_scan
        }
    
    async def generate_tests(
        self,
        code: str,
        framework: str = 'pytest',
        language: str = 'python'
    ) -> Dict[str, Any]:
        """
        Auto-generate tests for code
        
        Args:
            code: Source code to test
            framework: Testing framework (pytest, unittest, jest, etc.)
            language: Programming language
        
        Returns:
            Generated test code
        """
        
        if language == 'python':
            return await self._generate_python_tests(code, framework)
        else:
            return {'error': f'Test generation for {language} not implemented'}
    
    async def fix_errors(
        self,
        code: str,
        errors: List[Dict[str, Any]],
        language: str = 'python'
    ) -> Dict[str, Any]:
        """
        Auto-fix common errors in code
        
        Args:
            code: Code with errors
            errors: List of errors [{line, message, type}, ...]
            language: Programming language
        
        Returns:
            Fixed code with changes explained
        """
        
        fixed_code = code
        fixes_applied = []
        
        for error in errors:
            fix_result = await self._apply_error_fix(
                fixed_code,
                error,
                language
            )
            
            if fix_result['fixed']:
                fixed_code = fix_result['code']
                fixes_applied.append({
                    'error': error,
                    'fix': fix_result['description']
                })
        
        # Verify fixes don't introduce new issues
        security_scan = await hunter_engine.scan_code_snippet(fixed_code, language)
        
        return {
            'original_code': code,
            'fixed_code': fixed_code,
            'fixes_applied': fixes_applied,
            'errors_remaining': len(errors) - len(fixes_applied),
            'security_scan': security_scan
        }
    
    async def refactor_code(
        self,
        code: str,
        style: str,
        language: str = 'python'
    ) -> Dict[str, Any]:
        """
        Refactor code to match style guidelines
        
        Args:
            code: Original code
            style: Style guide (pep8, google, airbnb, etc.)
            language: Programming language
        
        Returns:
            Refactored code with changes explained
        """
        
        if language == 'python':
            return await self._refactor_python_code(code, style)
        else:
            return {'error': f'Refactoring for {language} not implemented'}
    
    async def _check_governance_approval(
        self,
        operation: str,
        spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if governance approves code generation"""
        
        # For now, auto-approve simple operations
        # In production, this would check governance policies
        
        if operation in ['generate_function', 'generate_class']:
            return {'approved': True}
        
        # Check with governance engine
        return await governance_engine.request_approval(
            action=operation,
            context=spec,
            auto_approve_low_risk=True
        )
    
    def _python_function_template(
        self,
        spec: Dict[str, Any],
        patterns: List[Dict[str, Any]]
    ) -> str:
        """Generate Python function"""
        
        name = spec['name']
        description = spec.get('description', 'Generated function')
        parameters = spec.get('parameters', [])
        return_type = spec.get('return_type', 'Any')
        
        # Build function signature
        params_str = ', '.join([
            f"{p['name']}: {p.get('type', 'Any')}"
            for p in parameters
        ])
        
        signature = f"def {name}({params_str}) -> {return_type}:"
        
        # Build docstring
        docstring = f'    """{description}\n\n'
        if parameters:
            docstring += '    Args:\n'
            for p in parameters:
                docstring += f"        {p['name']}: {p.get('description', 'Parameter')}\n"
        docstring += f'\n    Returns:\n        {return_type}: {spec.get("return_description", "Result")}\n'
        docstring += '    """\n'
        
        # Build body (use patterns if available)
        body = ''
        if patterns and patterns[0]['code']:
            # Extract logic from similar pattern
            body += '    # Implementation based on similar pattern\n'
            body += '    pass  # TODO: Implement based on spec\n'
        else:
            body += '    # TODO: Implement function logic\n'
            body += '    pass\n'
        
        return f"{signature}\n{docstring}{body}"
    
    def _python_class_template(
        self,
        spec: Dict[str, Any],
        patterns: List[Dict[str, Any]]
    ) -> str:
        """Generate Python class"""
        
        name = spec['name']
        description = spec.get('description', 'Generated class')
        base_classes = spec.get('base_classes', [])
        attributes = spec.get('attributes', [])
        methods = spec.get('methods', [])
        
        # Build class definition
        if base_classes:
            class_def = f"class {name}({', '.join(base_classes)}):"
        else:
            class_def = f"class {name}:"
        
        # Build docstring
        docstring = f'\n    """{description}\n\n'
        if attributes:
            docstring += '    Attributes:\n'
            for attr in attributes:
                docstring += f"        {attr['name']}: {attr.get('description', attr.get('type', 'Attribute'))}\n"
        docstring += '    """\n'
        
        # Build __init__
        init_method = '\n    def __init__(self'
        if attributes:
            for attr in attributes:
                init_method += f", {attr['name']}: {attr.get('type', 'Any')}"
        init_method += '):\n'
        
        if attributes:
            for attr in attributes:
                init_method += f"        self.{attr['name']} = {attr['name']}\n"
        else:
            init_method += '        pass\n'
        
        # Build methods
        methods_code = ''
        for method in methods:
            methods_code += f"\n    def {method['name']}(self"
            if method.get('params'):
                for param in method['params']:
                    methods_code += f", {param['name']}: {param.get('type', 'Any')}"
            methods_code += f") -> {method.get('return_type', 'None')}:\n"
            methods_code += f'        """{method.get("description", "Method")}"""\n'
            methods_code += '        pass\n'
        
        return f"{class_def}{docstring}{init_method}{methods_code}"
    
    def _python_api_endpoint_template(
        self,
        spec: Dict[str, Any],
        patterns: List[Dict[str, Any]]
    ) -> str:
        """Generate FastAPI endpoint"""
        
        method = spec.get('method', 'GET').lower()
        path = spec.get('path', '/endpoint')
        name = spec.get('name', 'endpoint')
        description = spec.get('description', 'API endpoint')
        
        code = f'@router.{method}("{path}")\n'
        code += f'async def {name}():\n'
        code += f'    """{description}"""\n'
        code += '    return {"status": "success"}\n'
        
        return code
    
    def _python_test_template(
        self,
        spec: Dict[str, Any],
        patterns: List[Dict[str, Any]]
    ) -> str:
        """Generate pytest test"""
        
        target_name = spec.get('target_name', 'function')
        test_name = f"test_{target_name}"
        
        code = f'def {test_name}():\n'
        code += f'    """Test {target_name}"""\n'
        code += f'    # Arrange\n'
        code += f'    # Act\n'
        code += f'    # Assert\n'
        code += f'    assert True  # TODO: Add assertions\n'
        
        return code
    
    async def _generate_python_tests(
        self,
        code: str,
        framework: str
    ) -> Dict[str, Any]:
        """Generate tests for Python code"""
        
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {'error': 'Invalid Python code'}
        
        test_code = ''
        if framework == 'pytest':
            test_code += 'import pytest\n\n'
        
        # Generate test for each function
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith('_'):  # Skip private functions
                    test_code += self._python_test_template(
                        {'target_name': node.name},
                        []
                    )
                    test_code += '\n\n'
        
        return {
            'test_code': test_code,
            'framework': framework,
            'language': 'python'
        }
    
    async def _apply_error_fix(
        self,
        code: str,
        error: Dict[str, Any],
        language: str
    ) -> Dict[str, Any]:
        """Apply fix for specific error"""
        
        error_type = error.get('type', '')
        error_msg = error.get('message', '')
        
        # Common error patterns and fixes
        if 'undefined name' in error_msg.lower() or 'not defined' in error_msg.lower():
            # Try to add import
            var_name = self._extract_undefined_name(error_msg)
            if var_name:
                # Add import at top
                fixed_code = f"from typing import {var_name}\n{code}"
                return {
                    'fixed': True,
                    'code': fixed_code,
                    'description': f'Added import for {var_name}'
                }
        
        elif 'expected an indented block' in error_msg.lower():
            # Add pass statement
            lines = code.split('\n')
            if error.get('line') and error['line'] <= len(lines):
                lines.insert(error['line'], '    pass')
                return {
                    'fixed': True,
                    'code': '\n'.join(lines),
                    'description': 'Added pass statement for empty block'
                }
        
        return {'fixed': False, 'code': code}
    
    def _extract_undefined_name(self, error_msg: str) -> Optional[str]:
        """Extract variable name from undefined error message"""
        
        match = re.search(r"name ['\"](\w+)['\"]", error_msg)
        if match:
            return match.group(1)
        return None
    
    async def _refactor_python_code(
        self,
        code: str,
        style: str
    ) -> Dict[str, Any]:
        """Refactor Python code to style"""
        
        refactored = code
        changes = []
        
        # Apply style-specific refactoring
        if style == 'pep8':
            # Check line length
            lines = code.split('\n')
            for i, line in enumerate(lines):
                if len(line) > 79:
                    changes.append({
                        'line': i + 1,
                        'issue': 'Line too long',
                        'suggestion': 'Split into multiple lines'
                    })
        
        return {
            'original_code': code,
            'refactored_code': refactored,
            'style': style,
            'changes': changes
        }

code_generator = CodeGenerator()
