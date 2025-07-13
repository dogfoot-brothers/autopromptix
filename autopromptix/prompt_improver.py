"""
AutoPromptix Prompt Improver

Handles system prompt parsing, analysis, and improvement based on test results.
"""

import json
import re
import openai
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from .storage import StorageManager

@dataclass
class PromptAnalysis:
    """Analysis results for a prompt"""
    clarity_score: float
    specificity_score: float
    completeness_score: float
    potential_issues: List[str]
    suggested_improvements: List[str]

@dataclass
class PromptImprovement:
    """Represents a prompt improvement"""
    original_prompt: str
    improved_prompt: str
    improvement_reason: str
    confidence_score: float
    expected_performance_gain: float

class PromptImprover:
    """Handles prompt parsing and improvement"""
    
    def __init__(self, storage_manager: StorageManager):
        self.storage = storage_manager
        self.improvement_templates = self._load_improvement_templates()
    
    def _load_improvement_templates(self) -> Dict[str, str]:
        """Load improvement templates for different types of prompts"""
        return {
            'clarity': """
            Improve the clarity of this prompt by:
            1. Making instructions more explicit
            2. Reducing ambiguity
            3. Using clearer language
            4. Adding examples where helpful
            
            Original prompt: {original_prompt}
            Issues identified: {issues}
            """,
            
            'specificity': """
            Make this prompt more specific by:
            1. Adding precise requirements
            2. Specifying output format
            3. Defining constraints
            4. Providing detailed context
            
            Original prompt: {original_prompt}
            Current issues: {issues}
            """,
            
            'completeness': """
            Make this prompt more complete by:
            1. Adding missing context
            2. Including edge case handling
            3. Specifying error handling
            4. Adding validation criteria
            
            Original prompt: {original_prompt}
            Missing elements: {issues}
            """,
            
            'performance': """
            Optimize this prompt for better performance by:
            1. Reducing unnecessary complexity
            2. Improving logical flow
            3. Enhancing focus on key objectives
            4. Streamlining instructions
            
            Original prompt: {original_prompt}
            Performance issues: {issues}
            Test results: {test_results}
            """
        }
    
    def parse_system_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Parse a system prompt and extract key components
        
        Args:
            prompt: The system prompt to parse
            
        Returns:
            Dictionary containing parsed components
        """
        parsed = {
            'raw_prompt': prompt,
            'instructions': self._extract_instructions(prompt),
            'constraints': self._extract_constraints(prompt),
            'examples': self._extract_examples(prompt),
            'context': self._extract_context(prompt),
            'output_format': self._extract_output_format(prompt),
            'roles': self._extract_roles(prompt),
            'complexity_score': self._calculate_complexity(prompt),
            'word_count': len(prompt.split()),
            'character_count': len(prompt)
        }
        
        return parsed
    
    def _extract_instructions(self, prompt: str) -> List[str]:
        """Extract instructions from the prompt"""
        instructions = []
        
        # Look for numbered lists
        numbered_pattern = r'^\d+\.\s*(.+)$'
        for match in re.finditer(numbered_pattern, prompt, re.MULTILINE):
            instructions.append(match.group(1).strip())
        
        # Look for bullet points
        bullet_pattern = r'^[-*•]\s*(.+)$'
        for match in re.finditer(bullet_pattern, prompt, re.MULTILINE):
            instructions.append(match.group(1).strip())
        
        # Look for imperative sentences
        imperative_pattern = r'(?:^|\n)([A-Z][^.!?]*(?:should|must|need to|have to|will|do|create|generate|provide|ensure|make sure)[^.!?]*[.!?])'
        for match in re.finditer(imperative_pattern, prompt, re.IGNORECASE):
            instructions.append(match.group(1).strip())
        
        return instructions
    
    def _extract_constraints(self, prompt: str) -> List[str]:
        """Extract constraints from the prompt"""
        constraints = []
        
        # Look for constraint keywords
        constraint_keywords = ['do not', 'don\'t', 'never', 'avoid', 'cannot', 'must not', 'shouldn\'t', 'restrict', 'limit', 'only', 'except']
        
        for keyword in constraint_keywords:
            pattern = rf'([^.!?]*{re.escape(keyword)}[^.!?]*[.!?])'
            for match in re.finditer(pattern, prompt, re.IGNORECASE):
                constraints.append(match.group(1).strip())
        
        return constraints
    
    def _extract_examples(self, prompt: str) -> List[str]:
        """Extract examples from the prompt"""
        examples = []
        
        # Look for example keywords
        example_patterns = [
            r'(?:for example|e\.g\.|such as|like|including)[^.!?]*[.!?]',
            r'example[^.!?]*[.!?]',
            r'(?:input|output):\s*[^.!?]*[.!?]'
        ]
        
        for pattern in example_patterns:
            for match in re.finditer(pattern, prompt, re.IGNORECASE):
                examples.append(match.group(0).strip())
        
        return examples
    
    def _extract_context(self, prompt: str) -> str:
        """Extract context information from the prompt"""
        context_keywords = ['context', 'background', 'scenario', 'situation', 'given', 'assume', 'role']
        
        for keyword in context_keywords:
            pattern = rf'([^.!?]*{re.escape(keyword)}[^.!?]*[.!?])'
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no explicit context, take first sentence
        sentences = re.split(r'[.!?]+', prompt)
        if sentences:
            return sentences[0].strip()
        
        return ""
    
    def _extract_output_format(self, prompt: str) -> str:
        """Extract output format specifications"""
        format_keywords = ['format', 'structure', 'json', 'xml', 'html', 'markdown', 'table', 'list']
        
        for keyword in format_keywords:
            pattern = rf'([^.!?]*{re.escape(keyword)}[^.!?]*[.!?])'
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_roles(self, prompt: str) -> List[str]:
        """Extract role definitions from the prompt"""
        roles = []
        
        role_patterns = [
            r'you are (?:a|an|the)?\s*([^.!?]*)[.!?]',
            r'act as (?:a|an|the)?\s*([^.!?]*)[.!?]',
            r'role[^.!?]*:\s*([^.!?]*)[.!?]'
        ]
        
        for pattern in role_patterns:
            for match in re.finditer(pattern, prompt, re.IGNORECASE):
                roles.append(match.group(1).strip())
        
        return roles
    
    def _calculate_complexity(self, prompt: str) -> float:
        """Calculate complexity score for the prompt"""
        # Factors that increase complexity
        factors = {
            'word_count': len(prompt.split()) / 100,  # Normalize by 100 words
            'sentence_count': len(re.split(r'[.!?]+', prompt)) / 10,  # Normalize by 10 sentences
            'instruction_count': len(self._extract_instructions(prompt)) / 5,  # Normalize by 5 instructions
            'constraint_count': len(self._extract_constraints(prompt)) / 3,  # Normalize by 3 constraints
            'nested_clauses': len(re.findall(r'\([^)]*\)', prompt)) / 5,  # Parenthetical expressions
            'conditional_statements': len(re.findall(r'\b(?:if|when|unless|provided|given)\b', prompt, re.IGNORECASE)) / 3
        }
        
        # Weighted average
        weights = {
            'word_count': 0.2,
            'sentence_count': 0.2,
            'instruction_count': 0.3,
            'constraint_count': 0.1,
            'nested_clauses': 0.1,
            'conditional_statements': 0.1
        }
        
        complexity = sum(factors[key] * weights[key] for key in factors)
        return min(complexity, 1.0)  # Cap at 1.0
    
    def analyze_prompt(self, prompt: str) -> PromptAnalysis:
        """
        Analyze a prompt and identify potential issues
        
        Args:
            prompt: The prompt to analyze
            
        Returns:
            PromptAnalysis object with scores and suggestions
        """
        parsed = self.parse_system_prompt(prompt)
        
        # Calculate scores
        clarity_score = self._calculate_clarity_score(parsed)
        specificity_score = self._calculate_specificity_score(parsed)
        completeness_score = self._calculate_completeness_score(parsed)
        
        # Identify issues
        issues = []
        suggestions = []
        
        if clarity_score < 0.7:
            issues.append("Prompt lacks clarity and may be ambiguous")
            suggestions.append("Use more specific language and provide examples")
        
        if specificity_score < 0.6:
            issues.append("Prompt is too vague or general")
            suggestions.append("Add specific requirements and constraints")
        
        if completeness_score < 0.5:
            issues.append("Prompt is missing important context or instructions")
            suggestions.append("Provide more complete context and detailed instructions")
        
        if len(parsed['instructions']) == 0:
            issues.append("No clear instructions found")
            suggestions.append("Add explicit step-by-step instructions")
        
        if not parsed['output_format']:
            issues.append("Output format not specified")
            suggestions.append("Specify the expected output format")
        
        return PromptAnalysis(
            clarity_score=clarity_score,
            specificity_score=specificity_score,
            completeness_score=completeness_score,
            potential_issues=issues,
            suggested_improvements=suggestions
        )
    
    def _calculate_clarity_score(self, parsed: Dict[str, Any]) -> float:
        """Calculate clarity score based on parsed components"""
        score = 0.0
        
        # Clear instructions boost score
        if len(parsed['instructions']) > 0:
            score += 0.3
        
        # Examples boost score
        if len(parsed['examples']) > 0:
            score += 0.2
        
        # Clear role definition
        if len(parsed['roles']) > 0:
            score += 0.2
        
        # Not too complex
        if parsed['complexity_score'] < 0.7:
            score += 0.2
        
        # Appropriate length
        if 50 <= parsed['word_count'] <= 300:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_specificity_score(self, parsed: Dict[str, Any]) -> float:
        """Calculate specificity score based on parsed components"""
        score = 0.0
        
        # Specific constraints
        if len(parsed['constraints']) > 0:
            score += 0.3
        
        # Output format specified
        if parsed['output_format']:
            score += 0.3
        
        # Detailed instructions
        if len(parsed['instructions']) >= 3:
            score += 0.2
        
        # Examples provided
        if len(parsed['examples']) > 0:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_completeness_score(self, parsed: Dict[str, Any]) -> float:
        """Calculate completeness score based on parsed components"""
        score = 0.0
        
        # Has context
        if parsed['context']:
            score += 0.25
        
        # Has instructions
        if len(parsed['instructions']) > 0:
            score += 0.25
        
        # Has constraints
        if len(parsed['constraints']) > 0:
            score += 0.25
        
        # Has examples or output format
        if len(parsed['examples']) > 0 or parsed['output_format']:
            score += 0.25
        
        return min(score, 1.0)
    
    def improve_prompt(self, function_id: str, original_prompt: str, 
                      test_results: List[Dict[str, Any]] = None, 
                      improvement_type: str = 'auto') -> PromptImprovement:
        """
        Improve a prompt based on analysis and test results
        
        Args:
            function_id: ID of the function being improved
            original_prompt: The original prompt to improve
            test_results: Recent test results to inform improvements
            improvement_type: Type of improvement ('auto', 'clarity', 'specificity', 'completeness', 'performance')
            
        Returns:
            PromptImprovement object with the improved prompt
        """
        analysis = self.analyze_prompt(original_prompt)
        
        if improvement_type == 'auto':
            # Determine best improvement type based on analysis
            if analysis.clarity_score < 0.6:
                improvement_type = 'clarity'
            elif analysis.specificity_score < 0.6:
                improvement_type = 'specificity'
            elif analysis.completeness_score < 0.5:
                improvement_type = 'completeness'
            else:
                improvement_type = 'performance'
        
        # Get improvement template
        template = self.improvement_templates.get(improvement_type, self.improvement_templates['clarity'])
        
        # Prepare improvement context
        issues = analysis.potential_issues
        test_results_summary = self._summarize_test_results(test_results) if test_results else ""
        
        # Generate improved prompt using the template
        improved_prompt = self._generate_improved_prompt(
            template, original_prompt, issues, test_results_summary
        )
        
        # Calculate confidence and expected performance gain
        confidence_score = self._calculate_improvement_confidence(analysis, improvement_type)
        expected_gain = self._estimate_performance_gain(analysis, improvement_type)
        
        improvement = PromptImprovement(
            original_prompt=original_prompt,
            improved_prompt=improved_prompt,
            improvement_reason=f"Improved {improvement_type} based on analysis",
            confidence_score=confidence_score,
            expected_performance_gain=expected_gain
        )
        
        # Save improvement to storage
        self.storage.save_prompt_improvement(
            function_id, original_prompt, improved_prompt, 
            improvement.improvement_reason, confidence_score
        )
        
        return improvement
    
    def _summarize_test_results(self, test_results: List[Dict[str, Any]]) -> str:
        """Summarize test results for improvement context"""
        if not test_results:
            return ""
        
        total_tests = len(test_results)
        avg_score = sum(r.get('score', 0) for r in test_results) / total_tests
        
        summary = f"Recent test results: {total_tests} tests, average score: {avg_score:.2f}"
        
        # Identify common issues
        low_score_results = [r for r in test_results if r.get('score', 0) < 0.6]
        if low_score_results:
            summary += f"\n{len(low_score_results)} tests scored below 0.6"
        
        return summary
    
    def _generate_improved_prompt(self, template: str, original_prompt: str, 
                                 issues: List[str], test_results: str) -> str:
        """Generate improved prompt using template and context"""
        # Simple template-based improvement
        # In a real implementation, you might use an LLM API here
        
        improved_prompt = original_prompt
        
        # Apply common improvements based on issues
        for issue in issues:
            if "clarity" in issue.lower():
                improved_prompt = self._improve_clarity(improved_prompt)
            elif "vague" in issue.lower():
                improved_prompt = self._improve_specificity(improved_prompt)
            elif "missing" in issue.lower():
                improved_prompt = self._improve_completeness(improved_prompt)
        
        return improved_prompt
    
    def _improve_clarity(self, prompt: str) -> str:
        """Improve prompt clarity"""
        # Add explicit structure if missing
        if not re.search(r'^\d+\.', prompt, re.MULTILINE):
            # Add step-by-step structure
            improved = "Please follow these steps:\n\n"
            improved += "1. " + prompt.replace('\n', '\n   ')
            improved += "\n\n2. Ensure your response is clear and specific."
            return improved
        return prompt
    
    def _improve_specificity(self, prompt: str) -> str:
        """Improve prompt specificity"""
        # Add output format specification if missing
        if not re.search(r'format|structure|json|xml|html', prompt, re.IGNORECASE):
            prompt += "\n\nPlease provide your response in a clear, structured format."
        return prompt
    
    def _improve_completeness(self, prompt: str) -> str:
        """Improve prompt completeness"""
        # Add context if missing
        if not re.search(r'context|background|role|you are', prompt, re.IGNORECASE):
            prompt = "Context: You are a helpful assistant designed to provide accurate and detailed responses.\n\n" + prompt
        return prompt
    
    def _calculate_improvement_confidence(self, analysis: PromptAnalysis, improvement_type: str) -> float:
        """Calculate confidence score for the improvement"""
        base_confidence = 0.5
        
        # Higher confidence for more specific improvements
        if improvement_type == 'clarity' and analysis.clarity_score < 0.5:
            base_confidence += 0.3
        elif improvement_type == 'specificity' and analysis.specificity_score < 0.5:
            base_confidence += 0.3
        elif improvement_type == 'completeness' and analysis.completeness_score < 0.5:
            base_confidence += 0.3
        
        # Boost confidence if multiple issues identified
        if len(analysis.potential_issues) > 2:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _estimate_performance_gain(self, analysis: PromptAnalysis, improvement_type: str) -> float:
        """Estimate expected performance gain from improvement"""
        # Simple heuristic based on current scores
        if improvement_type == 'clarity':
            return max(0.0, 0.8 - analysis.clarity_score)
        elif improvement_type == 'specificity':
            return max(0.0, 0.8 - analysis.specificity_score)
        elif improvement_type == 'completeness':
            return max(0.0, 0.8 - analysis.completeness_score)
        else:
            return 0.1  # Conservative estimate for performance improvements
    
    def get_improvement_history(self, function_id: str) -> List[Dict[str, Any]]:
        """Get improvement history for a function"""
        return self.storage.get_prompt_improvements(function_id) 