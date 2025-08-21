"""
AutoPromptix Scorer Module

Scoring functions for prompt evaluation based on various metrics.
Adapted from the demo repository's scorer_simple.py
"""

import logging
import re
from typing import List, Dict, Any
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    from rapidfuzz import fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    logger.warning("rapidfuzz not available, using basic string matching")

try:
    from rouge_score import rouge_scorer
    ROUGE_AVAILABLE = True
except ImportError:
    ROUGE_AVAILABLE = False
    logger.warning("rouge_score not available, using basic similarity")

def cosine_similarity(text1: str, text2: str) -> float:
    """Calculate cosine similarity between two texts"""
    if RAPIDFUZZ_AVAILABLE:
        # Use rapidfuzz for better performance
        return fuzz.ratio(text1, text2) / 100.0
    else:
        # Fallback to basic similarity
        return SequenceMatcher(None, text1, text2).ratio()

def rouge_l_score(text1: str, text2: str) -> float:
    """Calculate ROUGE-L score between two texts"""
    if ROUGE_AVAILABLE:
        scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
        scores = scorer.score(text1, text2)
        return scores['rougeL'].fmeasure
    else:
        # Fallback to longest common subsequence ratio
        return _lcs_ratio(text1, text2)

def _lcs_ratio(text1: str, text2: str) -> float:
    """Calculate longest common subsequence ratio"""
    words1 = text1.lower().split()
    words2 = text2.lower().split()
    
    if not words1 or not words2:
        return 0.0
    
    # Simple LCS implementation
    m, n = len(words1), len(words2)
    lcs = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if words1[i-1] == words2[j-1]:
                lcs[i][j] = lcs[i-1][j-1] + 1
            else:
                lcs[i][j] = max(lcs[i-1][j], lcs[i][j-1])
    
    lcs_length = lcs[m][n]
    return (2 * lcs_length) / (m + n) if (m + n) > 0 else 0.0

def keyword_coverage(text: str, keywords: List[str]) -> float:
    """Calculate keyword coverage score"""
    if not keywords:
        return 1.0
    
    text_lower = text.lower()
    found = sum(1 for keyword in keywords if keyword.lower() in text_lower)
    return found / len(keywords)

def structure_score(text: str) -> float:
    """Evaluate text structure quality"""
    score = 0.0
    
    # Check for sections/headings
    if re.search(r'^\s*#+\s+', text, re.MULTILINE) or re.search(r'^\s*\d+\.\s+', text, re.MULTILINE):
        score += 0.3
    
    # Check for bullet points
    if re.search(r'^\s*[-*•]\s+', text, re.MULTILINE):
        score += 0.2
    
    # Check for paragraphs
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    if len(paragraphs) > 1:
        score += 0.2
    
    # Check for reasonable length
    word_count = len(text.split())
    if 50 <= word_count <= 500:
        score += 0.3
    elif word_count > 500:
        score += 0.2
    elif word_count > 20:
        score += 0.1
    
    return min(score, 1.0)

def composite_score(
    output: str, 
    expected_output: str, 
    keywords: List[str] = None,
    weights: Dict[str, float] = None
) -> float:
    """Calculate composite score using multiple metrics"""
    
    if weights is None:
        weights = {
            'cosine': 0.3,
            'rouge': 0.3,
            'keywords': 0.2,
            'structure': 0.2
        }
    
    scores = {}
    
    # Cosine similarity
    scores['cosine'] = cosine_similarity(output, expected_output)
    
    # ROUGE-L score
    scores['rouge'] = rouge_l_score(output, expected_output)
    
    # Keyword coverage
    scores['keywords'] = keyword_coverage(output, keywords or [])
    
    # Structure score
    scores['structure'] = structure_score(output)
    
    # Calculate weighted average
    total_weight = sum(weights.values())
    if total_weight > 0:
        final_score = sum(scores[metric] * weights.get(metric, 0) for metric in scores) / total_weight
    else:
        final_score = sum(scores.values()) / len(scores)
    
    logger.debug(f"Score breakdown: {scores}")
    logger.debug(f"Final composite score: {final_score}")
    
    return final_score

def final_score_with_forbidden_check(
    base_score: float, 
    output: str, 
    forbidden_words: List[str]
) -> float:
    """Apply penalty for forbidden words"""
    if not forbidden_words:
        return base_score
    
    output_lower = output.lower()
    forbidden_count = 0
    
    for word in forbidden_words:
        if word.lower() in output_lower:
            forbidden_count += 1
            logger.info(f"Forbidden word found: {word}")
    
    if forbidden_count == 0:
        return base_score
    elif forbidden_count == 1:
        penalty = 0.3
    else:
        penalty = 0.6
    
    final_score = max(0, base_score - penalty)
    logger.info(f"Applied forbidden word penalty: {base_score} -> {final_score}")
    
    return final_score

def evaluate_prompt_quality(
    prompt: str,
    output: str,
    expected_output: str,
    keywords: List[str] = None,
    forbidden_words: List[str] = None,
    custom_criteria: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Comprehensive prompt quality evaluation"""
    
    # Base composite score
    base_score = composite_score(output, expected_output, keywords)
    
    # Apply forbidden word penalty
    final_score = final_score_with_forbidden_check(base_score, output, forbidden_words or [])
    
    # Additional custom criteria evaluation
    custom_scores = {}
    if custom_criteria:
        for criterion, requirement in custom_criteria.items():
            if criterion == "min_length":
                custom_scores[criterion] = 1.0 if len(output.split()) >= requirement else 0.5
            elif criterion == "max_length":
                custom_scores[criterion] = 1.0 if len(output.split()) <= requirement else 0.5
            elif criterion == "contains_phrase":
                custom_scores[criterion] = 1.0 if requirement.lower() in output.lower() else 0.0
    
    # Aggregate custom scores
    if custom_scores:
        custom_avg = sum(custom_scores.values()) / len(custom_scores)
        final_score = (final_score * 0.8) + (custom_avg * 0.2)
    
    return {
        'final_score': final_score,
        'base_score': base_score,
        'components': {
            'cosine_similarity': cosine_similarity(output, expected_output),
            'rouge_l': rouge_l_score(output, expected_output),
            'keyword_coverage': keyword_coverage(output, keywords or []),
            'structure': structure_score(output),
            'forbidden_penalty': base_score - final_score if forbidden_words else 0
        },
        'custom_criteria': custom_scores
    }
