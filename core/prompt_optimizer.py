"""
AutoPromptix Prompt Optimizer

Modern prompt optimization engine with AI-based evaluation and smart mutations.
Adapted from the demo repository's autopromptix_efficient.py
"""

import logging
from typing import List, Dict, Optional, Any
import json
import asyncio
from threading import Event

logger = logging.getLogger(__name__)

class PromptOptimizer:
    """AI-powered prompt optimization engine"""
    
    def __init__(self):
        self.max_generations = 1  # Fast optimization
        self.improvement_threshold = 0.05
    
    async def evaluate_prompt(
        self, 
        prompt: str, 
        user_input: str, 
        expected_output: str, 
        keywords: List[str], 
        exclude_keywords: List[str], 
        custom_mutators: List[str] = [], 
        evaluation_weights: Dict = {}
    ) -> float:
        """AI-based prompt evaluation (0-1 score)"""
        try:
            # Import llm module (to be added)
            from .llm_integration import ask_llm
            
            output = await ask_llm(prompt, user_input)
            
            # Weight configuration
            raw_weights = {
                'exclude_keywords': evaluation_weights.get('exclude_keywords', 25),
                'product_name': evaluation_weights.get('product_name', 25), 
                'expected_output': evaluation_weights.get('expected_output', 25),
                'custom_requirements': evaluation_weights.get('custom_requirements', 25)
            }
            
            # Convert to percentages
            total_weight = sum(raw_weights.values())
            if total_weight > 0:
                weights = {key: (value / total_weight) * 100 for key, value in raw_weights.items()}
            else:
                weights = {key: 25 for key in raw_weights.keys()}
            
            logger.info(f"Evaluation weights: {weights}")
            
            # Create AI evaluation prompt
            evaluation_prompt = f"""
Evaluate the following response based on 4 criteria and score from 0-100:

**Response to evaluate:**
{output}

**Evaluation criteria (with weights):**

1. **Exclude Keywords Compliance ({weights['exclude_keywords']} points)**: Are the following words excluded?
   Exclude keywords: {', '.join(exclude_keywords) if exclude_keywords else 'None'}
   - No excluded keywords found: {weights['exclude_keywords']} points
   - 1 excluded keyword found: {weights['exclude_keywords'] * 0.6:.0f} points
   - 2+ excluded keywords found: 0 points

2. **Product/Service Name Inclusion ({weights['product_name']} points)**: Is the following name appropriately included?
   Required: {', '.join(keywords) if keywords else 'None'}
   - Naturally included multiple times: {weights['product_name']} points
   - Included 1-2 times: {weights['product_name'] * 0.6:.0f} points
   - Not included: 0 points

3. **Expected Output Achievement ({weights['expected_output']} points)**: How well does it meet the expected result?
   Expected: {expected_output}
   - Perfectly meets expectations: {weights['expected_output']} points
   - Mostly meets expectations: {weights['expected_output'] * 0.8:.0f} points
   - Partially meets expectations: {weights['expected_output'] * 0.4:.0f} points
   - Does not meet expectations: 0 points

4. **Custom Requirements ({weights['custom_requirements']} points)**: How well are additional requirements reflected?
   Requirements: {', '.join(custom_mutators) if custom_mutators else 'None'}
   - All requirements met: {weights['custom_requirements']} points
   - Most requirements met: {weights['custom_requirements'] * 0.8:.0f} points
   - Some requirements met: {weights['custom_requirements'] * 0.4:.0f} points
   - Requirements not met: 0 points

**Response format:**
{{"score": total_score(0-100), "breakdown": {{"exclude_keywords": score1, "product_name": score2, "expected_output": score3, "custom_requirements": score4}}, "reasoning": "Evaluation reasoning for each criterion"}}

Provide the score in JSON format.
"""
            
            # Execute AI evaluation
            evaluation_response = await ask_llm(evaluation_prompt, "Evaluation request")
            logger.info(f"AI evaluation response: {evaluation_response}")
            
            # Parse JSON response
            try:
                if '{' in evaluation_response and '}' in evaluation_response:
                    start = evaluation_response.find('{')
                    end = evaluation_response.rfind('}') + 1
                    json_str = evaluation_response[start:end]
                    evaluation_result = json.loads(json_str)
                    
                    score = evaluation_result.get('score', 50) / 100.0  # Convert to 0-1 range
                    breakdown = evaluation_result.get('breakdown', {})
                    reasoning = evaluation_result.get('reasoning', '')
                    
                    logger.info(f"AI Evaluation - Score: {score*100:.1f}/100")
                    logger.info(f"Breakdown: {breakdown}")
                    logger.info(f"Reasoning: {reasoning}")
                    
                    return max(0.0, min(1.0, score))  # Ensure 0-1 range
                    
            except Exception as parse_error:
                logger.error(f"Failed to parse AI evaluation: {parse_error}")
            
            # Fallback to basic evaluation
            logger.info("Falling back to basic evaluation")
            from .scorer import composite_score, final_score_with_forbidden_check
            base_score = composite_score(output, expected_output, keywords)
            final_score = final_score_with_forbidden_check(base_score, output, exclude_keywords)
            
            logger.info(f"Fallback score: {final_score}")
            return final_score
            
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return 0.5  # Default score
    
    def should_continue(self, current_score: float, best_score: float, generation: int) -> bool:
        """Determine if optimization should continue"""
        if generation >= self.max_generations:
            return False
        if best_score > 0.85:
            return False
        return True
    
    async def optimize_prompt_simple(
        self,
        user_input: str,
        expected_output: str,
        product_name: str,
        exclude_keywords: List[str],
        custom_mutators: List[str] = [],
        evaluation_weights: Dict = {}
    ) -> Dict:
        """Simple prompt optimization"""
        logger.info(f"Starting simple optimization for: {user_input}")
        
        # Base prompt
        base_prompt = f"""User request: {user_input}

Expected result: {expected_output}

Please provide a specific and practical response that addresses the request."""
        
        # Keywords setup
        keywords = [product_name] if product_name else []
        
        # Analyze user input
        logger.info("=== Analyzing user input ===")
        analysis = await self.analyze_user_input(user_input)
        logger.info(f"Analysis result: {analysis}")
        
        # Generate smart mutations
        base_mutations = await self.generate_smart_mutations(
            base_prompt, user_input, analysis, custom_mutators, 
            exclude_keywords, product_name
        )
        logger.info(f"Generated mutations: {[name for name, _ in base_mutations]}")
        
        # Generation 0: Smart mutations
        logger.info("=== Generation 0 (Smart Mutations) ===")
        gen0_results = {}
        for name, prompt in base_mutations:
            score = await self.evaluate_prompt(
                prompt, user_input, expected_output, keywords, 
                exclude_keywords, custom_mutators, evaluation_weights
            )
            gen0_results[name] = score
            logger.info(f"Gen 0 | {name} | score={score}")
        
        # Select best score
        best_gen0 = max(gen0_results.items(), key=lambda x: x[1])
        current_best_score = best_gen0[1]
        best_prompt = base_mutations[0][1]  # Default
        
        # Find prompt for best score
        for name, prompt in base_mutations:
            if name == best_gen0[0]:
                best_prompt = prompt
                break
        
        logger.info(f"Adopt => {best_gen0[0]} ({current_best_score})")
        
        # Skip generation 2 for speed
        generation = 1
        total_evaluations = len(gen0_results)
        
        initial_score = gen0_results["base"]
        improvement = current_best_score - initial_score
        
        logger.info(f"Final: {initial_score} -> {current_best_score} (+{improvement:.3f})")
        logger.info(f"Total evaluations: {total_evaluations}, Generations: {generation}")
        
        # Import llm module
        from .llm_integration import ask_llm
        
        # Generate final output
        return {
            "best_prompt": best_prompt,
            "best_output": await ask_llm(best_prompt, user_input),
            "best_score": round(current_best_score, 3),
            "all_trials": [
                {
                    "name": name, 
                    "prompt": prompt_tuple[1], 
                    "score": score, 
                    "output": await ask_llm(prompt_tuple[1], user_input)
                }
                for name, score in gen0_results.items()
                for prompt_tuple in base_mutations if prompt_tuple[0] == name
            ],
            "total_evaluations": total_evaluations,
            "generations_completed": generation,
            "best_variant": best_gen0[0],
            "improvement_achieved": improvement > 0,
            "score_improvement": round(improvement, 3),
        }

    async def analyze_user_input(self, user_input: str) -> Dict[str, str]:
        """Analyze user input to determine optimization strategy"""
        try:
            from .llm_integration import ask_llm
            
            analysis_prompt = f"""
            Analyze the following user request and suggest the best prompt improvement direction:
            
            User request: {user_input}
            
            Choose the most suitable direction from:
            1. Structure (documents, plans, reports)
            2. Expertise (technical terms, data, analysis)
            3. Specificity (numbers, examples, step-by-step)
            4. Persuasiveness (for investors, customers)
            5. Actionability (executable action plans)
            
            Respond in JSON format:
            {{"direction": "chosen direction", "instructions": "specific instructions"}}
            """
            
            response = await ask_llm(analysis_prompt, "Analysis request")
            
            # Parse JSON
            try:
                if '{' in response and '}' in response:
                    start = response.find('{')
                    end = response.rfind('}') + 1
                    json_str = response[start:end]
                    result = json.loads(json_str)
                    return result
            except:
                pass
            
            # Default fallback
            return {"direction": "Specificity", "instructions": "Include specific numbers and examples"}
            
        except Exception as e:
            logger.error(f"Input analysis failed: {e}")
            return {"direction": "Specificity", "instructions": "Include specific numbers and examples"}

    async def generate_smart_mutations(
        self, 
        base_prompt: str, 
        user_input: str, 
        analysis: Dict[str, str], 
        custom_mutators: List[str] = [], 
        exclude_keywords: List[str] = [], 
        product_name: str = ""
    ) -> List[tuple]:
        """Generate smart mutations based on input analysis"""
        
        direction = analysis.get("direction", "Specificity")
        instructions = analysis.get("instructions", "Include specific content")
        
        # Prepare common text additions
        exclude_text = ""
        if exclude_keywords:
            exclude_text = f"\n\nImportant: Do not use these words: {', '.join(exclude_keywords)}"
        
        product_text = ""
        if product_name:
            product_text = f"\n\nProduct/Service name: '{product_name}' - include naturally in the response."
        
        custom_text = ""
        if custom_mutators:
            custom_instructions = "\n".join([f"- {mutator}" for mutator in custom_mutators])
            custom_text = f"\n\nAdditional requirements:\n{custom_instructions}"
        
        # Base mutation
        mutations = [("base", base_prompt + product_text + custom_text + exclude_text)]
        
        # Custom mutation (high priority)
        mutations.append(("custom", base_prompt + product_text + custom_text + exclude_text + 
                         f"\n\nEnhanced user-centric approach applied"))
        
        # Direction-based mutations
        if "structure" in direction.lower() or "document" in direction.lower():
            mutations.append(("structure", base_prompt + product_text + custom_text + exclude_text +
                            f"\n\nResponse must be structured as follows:\n{instructions}"))
        
        elif "expertise" in direction.lower() or "technical" in direction.lower():
            mutations.append(("professional", base_prompt + product_text + custom_text + exclude_text +
                            f"\n\nResponse must meet these requirements:\n{instructions}"))
        
        elif "specific" in direction.lower() or "number" in direction.lower():
            mutations.append(("specific", base_prompt + product_text + custom_text + exclude_text +
                            f"\n\nResponse must include these elements:\n{instructions}"))
        
        elif "persuasive" in direction.lower() or "investor" in direction.lower():
            mutations.append(("persuasive", base_prompt + product_text + custom_text + exclude_text +
                            f"\n\nResponse must be written from this perspective:\n{instructions}"))
        
        elif "action" in direction.lower() or "executable" in direction.lower():
            mutations.append(("actionable", base_prompt + product_text + custom_text + exclude_text +
                            f"\n\nResponse must be presented in this format:\n{instructions}"))
        
        # Default mutations if needed
        if len(mutations) == 2:  # Only base and custom
            mutations.extend([
                ("tone", base_prompt + product_text + custom_text + exclude_text +
                 f"\n\nResponse must be written in this format:\n1. Professional and persuasive tone\n2. Include specific numbers and data\n3. Prioritize key information for investors/customers\n4. Clear headings and summaries for each section"),
                ("format", base_prompt + product_text + custom_text + exclude_text +
                 f"\n\nResponse must follow this structure:\n- Title: [Clear title]\n- Summary: [Key points in 2-3 lines]\n- Details: [Numbered steps with bullets]\n- Conclusion: [Actionable next steps]\n- Appendix: [References or additional info]")
            ])
        
        return mutations


# Create singleton instance
_optimizer = PromptOptimizer()

# Exported functions for compatibility
async def optimize_prompt_simple(*args, **kwargs):
    """Simple prompt optimization function"""
    return await _optimizer.optimize_prompt_simple(*args, **kwargs)

async def optimize_prompt_streaming(
    user_input: str,
    expected_output: str,
    product_name: str,
    exclude_keywords: List[str],
    custom_mutators: List[str] = [],
    evaluation_weights: Dict = {},
    stop_event: Optional[Event] = None
):
    """Streaming version of prompt optimization"""
    optimizer = PromptOptimizer()
    
    # Send initial status
    yield {
        "type": "status",
        "data": {
            "message": "Starting prompt optimization...",
            "step": "init"
        }
    }
    await asyncio.sleep(0)
    
    # Setup
    keywords = [product_name] if product_name else []
    
    # Prepare base prompt with all requirements
    exclude_text = ""
    if exclude_keywords:
        exclude_text = f"\n\nImportant: Do not use these words: {', '.join(exclude_keywords)}"
    
    product_text = ""
    if product_name:
        product_text = f"\n\nProduct/Service name: '{product_name}' - include naturally in the response."
    
    custom_text = ""
    if custom_mutators:
        custom_instructions = "\n".join([f"- {mutator}" for mutator in custom_mutators])
        custom_text = f"\n\nAdditional requirements:\n{custom_instructions}"
    
    base_prompt = f"""User request: {user_input}

Expected result: {expected_output}

Please provide a specific and practical response that addresses the request.{product_text}{custom_text}{exclude_text}"""
    
    # Analyze user input
    yield {
        "type": "status",
        "data": {
            "message": "Analyzing user input...",
            "step": "analysis"
        }
    }
    
    analysis = await optimizer.analyze_user_input(user_input)
    
    yield {
        "type": "analysis",
        "data": {
            "analysis": analysis,
            "message": f"Analysis complete: {analysis.get('direction', 'Unknown')}"
        }
    }
    await asyncio.sleep(0)
    
    # Generate mutations
    yield {
        "type": "status",
        "data": {
            "message": "Generating prompt variations...",
            "step": "mutation"
        }
    }
    
    base_mutations = await optimizer.generate_smart_mutations(
        base_prompt, user_input, analysis, custom_mutators, exclude_keywords, product_name
    )
    
    yield {
        "type": "mutations",
        "data": {
            "mutations": [{"name": name, "prompt": prompt} for name, prompt in base_mutations],
            "message": f"Generated {len(base_mutations)} variations"
        }
    }
    await asyncio.sleep(0)
    
    # Start evaluation
    yield {
        "type": "status",
        "data": {
            "message": "Evaluating prompt variations...",
            "step": "evaluation"
        }
    }
    
    gen0_results = {}
    all_trials = []
    
    # Process variations
    for i, (name, prompt) in enumerate(base_mutations):
        # Check for stop signal
        if stop_event and stop_event.is_set():
            logger.info("Stop signal received, breaking optimization loop")
            return
            
        # Send evaluation start
        yield {
            "type": "evaluation_start",
            "data": {
                "name": name,
                "index": i,
                "total": len(base_mutations),
                "message": f"Evaluating variation {i+1}/{len(base_mutations)}: {name}"
            }
        }
        await asyncio.sleep(0)
        
        try:
            # Generate output
            from .llm_integration import ask_llm
            output = await ask_llm(prompt, user_input)
            
            # Send LLM response
            yield {
                "type": "llm_response",
                "data": {
                    "name": name,
                    "prompt": prompt,
                    "output": output,
                    "message": f"Generated response for '{name}'"
                }
            }
            await asyncio.sleep(0)
            
            # Evaluate
            score = await optimizer.evaluate_prompt(
                prompt, user_input, expected_output, keywords, 
                exclude_keywords, custom_mutators, evaluation_weights
            )
            gen0_results[name] = score
            
            trial_result = {
                "name": name,
                "prompt": prompt,
                "score": score,
                "output": output
            }
            all_trials.append(trial_result)
            
            # Send evaluation result
            yield {
                "type": "evaluation_result",
                "data": {
                    "trial": trial_result,
                    "message": f"Variation '{name}' scored {score:.3f}"
                }
            }
            await asyncio.sleep(0)
            
        except Exception as e:
            logger.error(f"Error processing variation {name}: {e}")
            continue
    
    # Select best result
    if not gen0_results:
        logger.error("No results generated - all variations failed")
        return
        
    best_gen0 = max(gen0_results.items(), key=lambda x: x[1])
    current_best_score = best_gen0[1]
    
    # Find best prompt
    best_prompt = base_mutations[0][1]
    for name, prompt in base_mutations:
        if name == best_gen0[0]:
            best_prompt = prompt
            break
    
    initial_score = gen0_results.get("base", 0.5)
    improvement = current_best_score - initial_score
    
    # Send final results
    from .llm_integration import ask_llm
    yield {
        "type": "final_results",
        "data": {
            "best_prompt": best_prompt,
            "best_output": await ask_llm(best_prompt, user_input),
            "best_score": round(current_best_score, 3),
            "all_trials": all_trials,
            "total_evaluations": len(gen0_results),
            "generations_completed": 1,
            "best_variant": best_gen0[0],
            "improvement_achieved": improvement > 0,
            "score_improvement": round(improvement, 3),
            "initial_score": round(initial_score, 3),
            "message": f"Optimization complete! Best score: {current_best_score:.3f} (improvement: {improvement:.3f})"
        }
    }
