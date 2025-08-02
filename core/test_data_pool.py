"""
Test Data Pool Management System

Manages comprehensive test data for AutoPromptix functions with multiple input-output pairs,
edge cases, and negative test scenarios.
"""

import json
import os
import random
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TestCase:
    """Represents a single test case"""
    id: str
    input: str
    expected_output: str
    weight: float = 1.0
    tags: List[str] = None
    description: str = ""
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class TestDataPool:
    """Represents a complete test data pool for a function"""
    function_name: str
    description: str
    category: str
    test_cases: List[TestCase]
    edge_cases: List[TestCase] = None
    negative_cases: List[TestCase] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.edge_cases is None:
            self.edge_cases = []
        if self.negative_cases is None:
            self.negative_cases = []
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def total_cases(self) -> int:
        """Get total number of test cases"""
        return len(self.test_cases) + len(self.edge_cases) + len(self.negative_cases)
    
    @property
    def average_weight(self) -> float:
        """Calculate average weight of all test cases"""
        all_cases = self.test_cases + self.edge_cases + self.negative_cases
        if not all_cases:
            return 0.0
        return sum(case.weight for case in all_cases) / len(all_cases)
    
    def get_cases_by_tag(self, tag: str) -> List[TestCase]:
        """Get all test cases with a specific tag"""
        all_cases = self.test_cases + self.edge_cases + self.negative_cases
        return [case for case in all_cases if tag in case.tags]
    
    def get_random_case(self, include_edge: bool = True, include_negative: bool = True) -> TestCase:
        """Get a random test case"""
        cases = self.test_cases.copy()
        if include_edge:
            cases.extend(self.edge_cases)
        if include_negative:
            cases.extend(self.negative_cases)
        
        if not cases:
            raise ValueError("No test cases available")
        
        # Weighted random selection
        weights = [case.weight for case in cases]
        return random.choices(cases, weights=weights)[0]
    
    def get_cases_by_weight_range(self, min_weight: float, max_weight: float) -> List[TestCase]:
        """Get test cases within a weight range"""
        all_cases = self.test_cases + self.edge_cases + self.negative_cases
        return [case for case in all_cases if min_weight <= case.weight <= max_weight]


class TestDataPoolManager:
    """Manages test data pools for AutoPromptix functions"""
    
    def __init__(self, pools_dir: str = "test_data_pools"):
        self.pools_dir = Path(pools_dir)
        self.pools_dir.mkdir(exist_ok=True)
        self._pools_cache = {}
    
    def create_pool(self, pool: TestDataPool) -> bool:
        """Create a new test data pool"""
        try:
            # Convert to dictionary
            pool_dict = {
                "function_name": pool.function_name,
                "description": pool.description,
                "category": pool.category,
                "test_cases": [
                    {
                        "id": case.id,
                        "input": case.input,
                        "expected_output": case.expected_output,
                        "weight": case.weight,
                        "tags": case.tags,
                        "description": case.description
                    }
                    for case in pool.test_cases
                ],
                "edge_cases": [
                    {
                        "id": case.id,
                        "input": case.input,
                        "expected_output": case.expected_output,
                        "weight": case.weight,
                        "tags": case.tags,
                        "description": case.description
                    }
                    for case in pool.edge_cases
                ],
                "negative_cases": [
                    {
                        "id": case.id,
                        "input": case.input,
                        "expected_output": case.expected_output,
                        "weight": case.weight,
                        "tags": case.tags,
                        "description": case.description
                    }
                    for case in pool.negative_cases
                ],
                "metadata": {
                    **pool.metadata,
                    "total_cases": pool.total_cases,
                    "average_weight": pool.average_weight,
                    "created_date": datetime.now().isoformat(),
                    "version": "1.0"
                }
            }
            
            # Save to file
            file_path = self.pools_dir / f"{pool.function_name}_test_cases.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(pool_dict, f, indent=2, ensure_ascii=False)
            
            # Update cache
            self._pools_cache[pool.function_name] = pool
            
            return True
        except Exception as e:
            print(f"Error creating test data pool: {e}")
            return False
    
    def load_pool(self, function_name: str) -> Optional[TestDataPool]:
        """Load a test data pool by function name"""
        # Check cache first
        if function_name in self._pools_cache:
            return self._pools_cache[function_name]
        
        try:
            file_path = self.pools_dir / f"{function_name}_test_cases.json"
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert to TestDataPool object
            pool = TestDataPool(
                function_name=data["function_name"],
                description=data["description"],
                category=data["category"],
                test_cases=[
                    TestCase(
                        id=case["id"],
                        input=case["input"],
                        expected_output=case["expected_output"],
                        weight=case["weight"],
                        tags=case.get("tags", []),
                        description=case.get("description", "")
                    )
                    for case in data["test_cases"]
                ],
                edge_cases=[
                    TestCase(
                        id=case["id"],
                        input=case["input"],
                        expected_output=case["expected_output"],
                        weight=case["weight"],
                        tags=case.get("tags", []),
                        description=case.get("description", "")
                    )
                    for case in data.get("edge_cases", [])
                ],
                negative_cases=[
                    TestCase(
                        id=case["id"],
                        input=case["input"],
                        expected_output=case["expected_output"],
                        weight=case["weight"],
                        tags=case.get("tags", []),
                        description=case.get("description", "")
                    )
                    for case in data.get("negative_cases", [])
                ],
                metadata=data.get("metadata", {})
            )
            
            # Update cache
            self._pools_cache[function_name] = pool
            
            return pool
        except Exception as e:
            print(f"Error loading test data pool: {e}")
            return None
    
    def list_pools(self) -> List[str]:
        """List all available test data pools"""
        pools = []
        for file_path in self.pools_dir.glob("*_test_cases.json"):
            pool_name = file_path.stem.replace("_test_cases", "")
            pools.append(pool_name)
        return pools
    
    def delete_pool(self, function_name: str) -> bool:
        """Delete a test data pool"""
        try:
            file_path = self.pools_dir / f"{function_name}_test_cases.json"
            if file_path.exists():
                file_path.unlink()
                if function_name in self._pools_cache:
                    del self._pools_cache[function_name]
                return True
            return False
        except Exception as e:
            print(f"Error deleting test data pool: {e}")
            return False
    
    def get_test_case(self, function_name: str, case_id: str) -> Optional[TestCase]:
        """Get a specific test case from a pool"""
        pool = self.load_pool(function_name)
        if not pool:
            return None
        
        all_cases = pool.test_cases + pool.edge_cases + pool.negative_cases
        for case in all_cases:
            if case.id == case_id:
                return case
        return None
    
    def add_test_case(self, function_name: str, test_case: TestCase, 
                     case_type: str = "test_cases") -> bool:
        """Add a test case to a pool"""
        pool = self.load_pool(function_name)
        if not pool:
            return False
        
        try:
            if case_type == "test_cases":
                pool.test_cases.append(test_case)
            elif case_type == "edge_cases":
                pool.edge_cases.append(test_case)
            elif case_type == "negative_cases":
                pool.negative_cases.append(test_case)
            else:
                return False
            
            return self.create_pool(pool)
        except Exception as e:
            print(f"Error adding test case: {e}")
            return False
    
    def get_statistics(self, function_name: str) -> Dict[str, Any]:
        """Get statistics for a test data pool"""
        pool = self.load_pool(function_name)
        if not pool:
            return {}
        
        return {
            "total_cases": pool.total_cases,
            "test_cases": len(pool.test_cases),
            "edge_cases": len(pool.edge_cases),
            "negative_cases": len(pool.negative_cases),
            "average_weight": pool.average_weight,
            "categories": list(set(
                tag for case in pool.test_cases + pool.edge_cases + pool.negative_cases
                for tag in case.tags
            ))
        }


def create_greeting_test_pool() -> TestDataPool:
    """Create a sample greeting test data pool"""
    test_cases = [
        TestCase(
            id="greeting_001",
            input="Hello, how are you?",
            expected_output="Hello! I'm doing well, thank you for asking. How can I help you today?",
            weight=1.0,
            tags=["basic", "greeting"],
            description="Basic greeting test case"
        ),
        TestCase(
            id="greeting_002",
            input="Good morning!",
            expected_output="Good morning! I hope you're having a wonderful day. How can I assist you?",
            weight=1.0,
            tags=["basic", "greeting", "morning"],
            description="Morning greeting test case"
        ),
        TestCase(
            id="greeting_003",
            input="Hi there!",
            expected_output="Hi there! Nice to meet you. What can I help you with today?",
            weight=1.0,
            tags=["basic", "greeting", "casual"],
            description="Casual greeting test case"
        )
    ]
    
    edge_cases = [
        TestCase(
            id="greeting_edge_001",
            input="",
            expected_output="Hello! I didn't catch that. Could you please say something?",
            weight=1.5,
            tags=["edge", "empty"],
            description="Empty input edge case"
        ),
        TestCase(
            id="greeting_edge_002",
            input="   ",
            expected_output="Hello! I didn't catch that. Could you please say something?",
            weight=1.5,
            tags=["edge", "whitespace"],
            description="Whitespace only edge case"
        )
    ]
    
    negative_cases = [
        TestCase(
            id="greeting_neg_001",
            input="12345",
            expected_output="Hello! I received your message: '12345'. How can I help you today?",
            weight=1.0,
            tags=["negative", "numbers"],
            description="Numbers input negative case"
        ),
        TestCase(
            id="greeting_neg_002",
            input="!@#$%",
            expected_output="Hello! I received your message: '!@#$%'. How can I help you today?",
            weight=1.0,
            tags=["negative", "symbols"],
            description="Symbols input negative case"
        )
    ]
    
    return TestDataPool(
        function_name="greeting",
        description="Test data pool for greeting function with various input scenarios",
        category="communication",
        test_cases=test_cases,
        edge_cases=edge_cases,
        negative_cases=negative_cases,
        metadata={
            "version": "1.0",
            "created_by": "AutoPromptix",
            "tags": ["greeting", "communication", "basic"]
        }
    )


def create_sentiment_test_pool() -> TestDataPool:
    """Create a sample sentiment analysis test data pool"""
    test_cases = [
        TestCase(
            id="sentiment_001",
            input="I love this amazing product!",
            expected_output="This text appears to be positive because it contains enthusiastic language and positive sentiment.",
            weight=1.0,
            tags=["basic", "positive"],
            description="Positive sentiment test case"
        ),
        TestCase(
            id="sentiment_002",
            input="This is terrible and I hate it.",
            expected_output="This text appears to be negative because it contains negative language and expresses dissatisfaction.",
            weight=1.0,
            tags=["basic", "negative"],
            description="Negative sentiment test case"
        )
    ]
    
    return TestDataPool(
        function_name="analyze_sentiment",
        description="Test data pool for sentiment analysis function",
        category="analysis",
        test_cases=test_cases,
        edge_cases=[],
        negative_cases=[],
        metadata={
            "version": "1.0",
            "created_by": "AutoPromptix",
            "tags": ["sentiment", "analysis", "nlp"]
        }
    ) 