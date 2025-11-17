"""
Creative Problem Solver Agent
Advanced reasoning: reverse engineering, outside-the-box thinking, terminology extraction
"""

import logging
import re
from typing import Dict, Any, List
from datetime import datetime
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)


class CreativeProblemSolver:
    """
    Advanced problem-solving agent that:
    - Reverse engineers problems from goal to solution
    - Generates multiple alternative approaches
    - Extracts terminology and iteratively searches
    - Thinks creatively and avoids fixation
    """
    
    def __init__(self):
        self.playbook = None
        self.problems_solved = 0
        self.approaches_tried = 0
        self.alternatives_found = 0
        self.terms_extracted = 0
        self._initialized = False
        self.known_terms = set()  # Build vocabulary over time
        self.failed_approaches = {}  # Remember what didn't work
        
    async def initialize(self):
        """Load problem-solving playbook"""
        if self._initialized:
            return
            
        try:
            playbook_path = Path(__file__).parent.parent.parent / "playbooks" / "advanced_problem_solving_playbook.yaml"
            if playbook_path.exists():
                with open(playbook_path, 'r', encoding='utf-8') as f:
                    # Load all documents and merge (YAML file has multiple --- separators)
                    docs = list(yaml.safe_load_all(f))
                    self.playbook = docs[0] if docs else {}
                logger.info("[CREATIVE-SOLVER] Loaded advanced problem-solving playbook")
            else:
                logger.warning(f"[CREATIVE-SOLVER] Playbook not found: {playbook_path}")
        except Exception as e:
            logger.error(f"[CREATIVE-SOLVER] Failed to load playbook: {e}")
        
        self._initialized = True
    
    async def extract_terminology(
        self,
        text: str,
        context: str = "general"
    ) -> Dict[str, Any]:
        """
        Extract technical terms, acronyms, error codes, metadata from text
        
        Returns:
            {
                'technical_terms': [...],
                'error_codes': [...],
                'file_formats': [...],
                'version_numbers': [...],
                'unknown_terms': [...]  # Terms not in known_terms yet
            }
        """
        results = {
            'technical_terms': [],
            'error_codes': [],
            'file_formats': [],
            'version_numbers': [],
            'acronyms': [],
            'unknown_terms': [],
            'all_terms': set()
        }
        
        # Extract error codes
        error_patterns = [
            r'\b[45]\d{2}\b',  # HTTP codes (400-599)
            r'\bE[A-Z]+\b',  # Unix error codes (ECONNREFUSED, etc.)
            r'\berrno\s*:\s*\d+',  # errno codes
            r'\b[A-Z_]{5,}\b',  # All caps codes
        ]
        
        for pattern in error_patterns:
            matches = re.findall(pattern, text)
            results['error_codes'].extend(matches)
            results['all_terms'].update(matches)
        
        # Extract file formats
        file_format_pattern = r'\.\w{2,5}\b'
        formats = re.findall(file_format_pattern, text)
        results['file_formats'] = list(set(formats))
        results['all_terms'].update(formats)
        
        # Extract version numbers
        version_pattern = r'\b\d+\.\d+(?:\.\d+)?(?:\.\d+)?\b'
        versions = re.findall(version_pattern, text)
        results['version_numbers'] = list(set(versions))
        
        # Extract acronyms (3-6 uppercase letters)
        acronym_pattern = r'\b[A-Z]{3,6}\b'
        acronyms = re.findall(acronym_pattern, text)
        results['acronyms'] = list(set(acronyms))
        results['all_terms'].update(acronyms)
        
        # Extract technical terms (CamelCase, snake_case with tech keywords)
        tech_keywords = [
            'API', 'HTTP', 'REST', 'JSON', 'XML', 'SQL', 'DB', 'database',
            'async', 'sync', 'thread', 'process', 'server', 'client',
            'auth', 'token', 'key', 'session', 'cache', 'queue'
        ]
        
        words = re.findall(r'\b\w+\b', text)
        for word in words:
            # CamelCase
            if re.match(r'^[A-Z][a-z]+[A-Z]', word):
                results['technical_terms'].append(word)
                results['all_terms'].add(word)
            
            # Contains tech keywords
            elif any(kw in word.lower() for kw in tech_keywords):
                results['technical_terms'].append(word)
                results['all_terms'].add(word)
        
        # Identify unknown terms (not in our vocabulary yet)
        for term in results['all_terms']:
            if term.lower() not in self.known_terms:
                results['unknown_terms'].append(term)
        
        self.terms_extracted += len(results['all_terms'])
        
        # Update known terms
        self.known_terms.update(term.lower() for term in results['all_terms'])
        
        return results
    
    async def iterative_terminology_search(
        self,
        initial_terms: List[str],
        max_depth: int = 3
    ) -> Dict[str, Any]:
        """
        Iteratively search terms, extract new terms from results, search deeper
        
        This is the core of Grace's learning expansion
        """
        from backend.services.google_search_service import google_search_service
        
        all_findings = {
            'depth_0': {'terms': initial_terms, 'results': []},
            'learned_concepts': {},
            'related_terms': set(),
            'solution_hints': []
        }
        
        current_terms = initial_terms
        
        for depth in range(max_depth):
            logger.info(f"[CREATIVE-SOLVER] Depth {depth}: Searching {len(current_terms)} terms")
            
            depth_results = []
            new_terms = set()
            
            for term in current_terms[:5]:  # Limit to prevent explosion
                try:
                    # Search the term
                    search_results = await google_search_service.search(
                        query=term,
                        num_results=3
                    )
                    
                    depth_results.extend(search_results)
                    
                    # Extract terminology from search results
                    for result in search_results:
                        snippet = result.get('snippet', '')
                        title = result.get('title', '')
                        combined_text = f"{title} {snippet}"
                        
                        extracted = await self.extract_terminology(combined_text)
                        new_terms.update(extracted['unknown_terms'])
                        
                        # Learn the concept
                        all_findings['learned_concepts'][term] = {
                            'definition': snippet[:200],
                            'source': result.get('url'),
                            'trust_score': result.get('trust_score', 0.5)
                        }
                
                except Exception as e:
                    logger.warning(f"[CREATIVE-SOLVER] Search failed for '{term}': {e}")
            
            all_findings[f'depth_{depth}'] = {
                'terms_searched': current_terms,
                'results_found': len(depth_results),
                'new_terms_discovered': list(new_terms)
            }
            
            all_findings['related_terms'].update(new_terms)
            
            # Use new terms for next depth
            current_terms = list(new_terms)[:10]  # Limit expansion
            
            if not current_terms:
                logger.info(f"[CREATIVE-SOLVER] Stopped at depth {depth}: No new terms found")
                break
        
        return all_findings
    
    async def reverse_engineer_problem(
        self,
        problem_description: str,
        desired_outcome: str
    ) -> Dict[str, Any]:
        """
        Reverse engineer: Start from goal, work backwards to current state
        
        Returns action plan with multiple approaches
        """
        logger.info(f"[CREATIVE-SOLVER] Reverse engineering problem")
        logger.info(f"[CREATIVE-SOLVER] Goal: {desired_outcome}")
        
        plan = {
            'goal': desired_outcome,
            'current_state': problem_description,
            'gap_analysis': {},
            'requirements': [],
            'approaches': [],
            'terminology_extracted': {},
            'recommended_approach': None
        }
        
        # Extract terminology from problem
        problem_terms = await self.extract_terminology(problem_description)
        goal_terms = await self.extract_terminology(desired_outcome)
        
        plan['terminology_extracted'] = {
            'from_problem': problem_terms,
            'from_goal': goal_terms
        }
        
        # Identify gap (what's missing/needed)
        plan['gap_analysis'] = {
            'description': f"Bridge from '{problem_description}' to '{desired_outcome}'",
            'missing_elements': [],  # To be filled by search
            'blockers': []
        }
        
        # Extract error codes/issues
        if problem_terms['error_codes']:
            plan['gap_analysis']['blockers'] = problem_terms['error_codes']
        
        # Search to understand what's needed
        from backend.services.google_search_service import google_search_service
        
        # Search the goal to understand requirements
        try:
            goal_search = await google_search_service.search(
                query=f"how to {desired_outcome}",
                num_results=5
            )
            
            requirements_hints = []
            for result in goal_search:
                snippet = result.get('snippet', '')
                # Extract requirements from snippets
                if 'need' in snippet.lower() or 'require' in snippet.lower():
                    requirements_hints.append(snippet[:150])
            
            plan['requirements'] = requirements_hints
        
        except Exception as e:
            logger.warning(f"[CREATIVE-SOLVER] Goal search failed: {e}")
        
        # Generate multiple approaches
        plan['approaches'] = await self.generate_alternative_approaches(
            problem_description,
            desired_outcome,
            problem_terms
        )
        
        # Recommend best approach (first one, but Grace can try others if it fails)
        if plan['approaches']:
            plan['recommended_approach'] = plan['approaches'][0]
        
        return plan
    
    async def generate_alternative_approaches(
        self,
        problem: str,
        goal: str,
        extracted_terms: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate 3+ alternative approaches to solve the problem
        Never fixate on just one solution
        """
        from backend.services.google_search_service import google_search_service
        
        approaches = []
        
        # Approach 1: Direct/conventional solution
        approaches.append({
            'name': 'Direct Approach',
            'description': f"Solve '{problem}' directly using standard methods",
            'search_query': f"{goal} standard solution",
            'rationale': 'Try the most common/documented approach first'
        })
        
        # Approach 2: Alternative technology/library
        approaches.append({
            'name': 'Alternative Technology',
            'description': f"Use different tools/libraries to achieve '{goal}'",
            'search_query': f"{goal} alternative methods",
            'rationale': 'Different tools might work better for this specific case'
        })
        
        # Approach 3: Workaround/indirect path
        approaches.append({
            'name': 'Workaround Approach',
            'description': f"Achieve '{goal}' indirectly or via different path",
            'search_query': f"{goal} workaround",
            'rationale': 'Sometimes the indirect path is more elegant'
        })
        
        # If error codes present, add error-specific approach
        if extracted_terms.get('error_codes'):
            error_code = extracted_terms['error_codes'][0]
            approaches.append({
                'name': 'Error-Specific Solution',
                'description': f"Fix specific error: {error_code}",
                'search_query': f"{error_code} fix solution",
                'rationale': f'Directly address the error blocking progress'
            })
        
        # Research each approach to add details
        for approach in approaches:
            try:
                search_results = await google_search_service.search(
                    query=approach['search_query'],
                    num_results=2
                )
                
                approach['research_results'] = search_results
                approach['feasibility'] = 'high' if search_results else 'unknown'
                
                if search_results:
                    approach['example_solution'] = search_results[0].get('snippet', '')
            
            except Exception as e:
                logger.warning(f"[CREATIVE-SOLVER] Approach research failed: {e}")
                approach['feasibility'] = 'unknown'
        
        self.approaches_tried += len(approaches)
        
        return approaches
    
    async def solve_problem_creatively(
        self,
        problem: str,
        context: Dict[str, Any] = None,
        test_in_sandbox: bool = True
    ) -> Dict[str, Any]:
        """
        Main method: Apply full creative problem-solving process
        
        Process:
        1. Extract terminology from problem
        2. Iteratively search terms to build understanding
        3. Reverse engineer from goal to current state
        4. Generate multiple alternative approaches
        5. Test approaches in sandbox (if enabled)
        6. Return comprehensive solution plan
        """
        if not self._initialized:
            await self.initialize()
        
        logger.info(f"[CREATIVE-SOLVER] 🧠 Creative problem-solving initiated")
        logger.info(f"[CREATIVE-SOLVER] Problem: {problem[:100]}...")
        
        solution = {
            'problem': problem,
            'timestamp': datetime.utcnow().isoformat(),
            'process': {},
            'solution_plan': {},
            'alternatives': [],
            'learned_terminology': {}
        }
        
        # Step 1: Extract terminology
        logger.info("[CREATIVE-SOLVER] Step 1: Extracting terminology...")
        extracted = await self.extract_terminology(problem)
        solution['learned_terminology'] = extracted
        
        # Step 2: Iterative terminology search
        logger.info("[CREATIVE-SOLVER] Step 2: Iteratively searching terms...")
        if extracted['unknown_terms']:
            terminology_expansion = await self.iterative_terminology_search(
                extracted['unknown_terms'][:5],  # Start with top 5 unknown terms
                max_depth=2
            )
            solution['process']['terminology_expansion'] = terminology_expansion
        
        # Step 3: Determine goal (if not explicit in problem)
        goal = context.get('goal', 'solve this problem') if context else 'solve this problem'
        
        # Step 4: Reverse engineer
        logger.info("[CREATIVE-SOLVER] Step 3: Reverse engineering solution...")
        reverse_plan = await self.reverse_engineer_problem(problem, goal)
        solution['solution_plan'] = reverse_plan
        
        # Step 5: Record alternatives
        solution['alternatives'] = reverse_plan.get('approaches', [])
        
        # Step 6: Provide recommendation
        solution['recommendation'] = {
            'primary_approach': reverse_plan.get('recommended_approach'),
            'fallback_approaches': reverse_plan.get('approaches', [])[1:],
            'rationale': 'Try primary first; if fails after 3 attempts, switch to fallback'
        }
        
        self.problems_solved += 1
        self.alternatives_found += len(solution['alternatives'])
        
        logger.info(f"[CREATIVE-SOLVER] ✅ Generated solution with {len(solution['alternatives'])} approaches")
        
        # Step 7: Test in sandbox (knowledge + application)
        if test_in_sandbox and solution.get('solution_plan', {}).get('recommended_approach'):
            logger.info("[CREATIVE-SOLVER] Step 4: Testing approach in sandbox...")
            try:
                sandbox_result = await self._test_solution_in_sandbox(
                    problem=problem,
                    solution_plan=solution['solution_plan'],
                    approach=solution['solution_plan']['recommended_approach']
                )
                solution['sandbox_testing'] = sandbox_result
                
                if sandbox_result.get('passed'):
                    logger.info("[CREATIVE-SOLVER] ✅ Sandbox test PASSED - solution validated!")
                else:
                    logger.warning("[CREATIVE-SOLVER] ⚠️ Sandbox test failed - trying alternative...")
                    # Try first alternative approach
                    if len(solution['alternatives']) > 1:
                        alternative = solution['alternatives'][1]
                        alt_test = await self._test_solution_in_sandbox(
                            problem=problem,
                            solution_plan=solution['solution_plan'],
                            approach=alternative
                        )
                        solution['alternative_sandbox_test'] = alt_test
                        if alt_test.get('passed'):
                            solution['recommendation']['primary_approach'] = alternative
                            logger.info("[CREATIVE-SOLVER] ✅ Alternative approach PASSED!")
            except Exception as e:
                logger.warning(f"[CREATIVE-SOLVER] Sandbox testing failed: {e}")
                solution['sandbox_testing'] = {'error': str(e), 'passed': False}
        
        return solution
    
    async def _test_solution_in_sandbox(
        self,
        problem: str,
        solution_plan: Dict[str, Any],
        approach: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Test a solution approach in sandbox
        Combines knowledge acquisition with practical application
        """
        from backend.knowledge.knowledge_application_sandbox import knowledge_sandbox
        
        # Create testable code/scenario from approach
        approach_desc = approach.get('description', '')
        example = approach.get('example_solution', '')
        
        test_code = f"""
# Problem: {problem[:200]}
# Approach: {approach_desc}
# Test implementation

{example[:500] if example else '# No example code provided'}

# Validation
result = "test passed"
assert result == "test passed"
"""
        
        # Test in sandbox
        sandbox_result = await knowledge_sandbox.test_learned_code(
            code=test_code,
            source_id=f"creative-solver-{datetime.utcnow().timestamp()}",
            source_url=approach.get('research_results', [{}])[0].get('url', 'creative_solution'),
            context=f"Testing solution for: {problem[:100]}"
        )
        
        return sandbox_result
    
    async def record_failure(
        self,
        approach: str,
        problem: str,
        reason: str
    ):
        """
        Record failed approaches to avoid repeating them
        Learn from failures
        """
        failure_key = f"{problem[:50]}_{approach}"
        
        if failure_key not in self.failed_approaches:
            self.failed_approaches[failure_key] = []
        
        self.failed_approaches[failure_key].append({
            'timestamp': datetime.utcnow().isoformat(),
            'reason': reason,
            'approach': approach
        })
        
        logger.info(f"[CREATIVE-SOLVER] 📝 Recorded failure: {approach} - {reason}")
        logger.info(f"[CREATIVE-SOLVER] Will try alternative approach next time")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get problem-solving metrics"""
        return {
            'problems_solved': self.problems_solved,
            'approaches_tried': self.approaches_tried,
            'alternatives_found': self.alternatives_found,
            'terms_extracted': self.terms_extracted,
            'vocabulary_size': len(self.known_terms),
            'failed_approaches_learned': len(self.failed_approaches),
            'playbook_loaded': self.playbook is not None,
            'initialized': self._initialized
        }


# Global instance
creative_problem_solver = CreativeProblemSolver()
