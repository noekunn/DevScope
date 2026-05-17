"""
Granite Client for DevScope.

Provides watsonx.ai Granite model integration for:
- Module summarization
- Role-based explanations
- Modernization opportunity detection
- Onboarding guide generation
"""

import os
import json
from typing import List, Dict, Any, Optional
import logging
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GraniteClient:
    """
    Client for IBM watsonx.ai Granite model.
    
    Provides semantic analysis capabilities:
    - Module summarization
    - Role-based code explanations
    - Modernization opportunity detection
    - Onboarding guide generation
    
    Falls back gracefully if credentials are missing.
    """
    
    MODEL_ID = "ibm/granite-3-8b-instruct"
    
    # Token costs (approximate, adjust based on actual pricing)
    INPUT_TOKEN_COST = 0.0001  # per 1K tokens
    OUTPUT_TOKEN_COST = 0.0002  # per 1K tokens
    
    def __init__(self):
        """Initialize Granite client with watsonx.ai credentials."""
        self.api_key = os.getenv('WATSONX_API_KEY', '')
        self.project_id = os.getenv('WATSONX_PROJECT_ID', '')
        self.url = os.getenv('WATSONX_URL', 'https://us-south.ml.cloud.ibm.com')
        
        self.model: Optional[ModelInference] = None
        self.fallback_mode = False
        
        # Token tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        
        # Initialize model
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the Granite model."""
        if not self.api_key or not self.project_id:
            logger.warning("watsonx.ai credentials not found. Using fallback mode.")
            self.fallback_mode = True
            return
        
        try:
            self.model = ModelInference(
                model_id=self.MODEL_ID,
                params={
                    GenParams.DECODING_METHOD: "greedy",
                    GenParams.MAX_NEW_TOKENS: 1000,
                    GenParams.MIN_NEW_TOKENS: 1,
                    GenParams.TEMPERATURE: 0.7,
                    GenParams.TOP_K: 50,
                    GenParams.TOP_P: 1
                },
                credentials={
                    "apikey": self.api_key,
                    "url": self.url
                },
                project_id=self.project_id
            )
            self.fallback_mode = False
            logger.info(f"Initialized Granite model: {self.MODEL_ID}")
        except Exception as e:
            logger.error(f"Failed to initialize Granite model: {e}")
            self.fallback_mode = True
    
    def _generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Generate text using Granite model.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        if self.fallback_mode:
            return "Semantic analysis unavailable (watsonx.ai credentials not configured)"
        
        try:
            # Update max tokens
            self.model.params[GenParams.MAX_NEW_TOKENS] = max_tokens
            
            # Generate
            response = self.model.generate_text(prompt=prompt)
            
            # Track tokens (approximate)
            input_tokens = len(prompt.split()) * 1.3  # Rough estimate
            output_tokens = len(response.split()) * 1.3
            
            self.total_input_tokens += input_tokens
            self.total_output_tokens += output_tokens
            self.total_cost += (input_tokens / 1000 * self.INPUT_TOKEN_COST + 
                              output_tokens / 1000 * self.OUTPUT_TOKEN_COST)
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return f"Error: {str(e)}"
    
    def summarize_module(self, file_contents: List[str]) -> Dict[str, str]:
        """
        Summarize a module from multiple file contents.
        
        Args:
            file_contents: List of file content strings
            
        Returns:
            Dictionary with purpose, architectural_role, patterns_detected, key_insight
        """
        if self.fallback_mode:
            return {
                'purpose': 'Semantic analysis unavailable',
                'architectural_role': 'Unknown',
                'patterns_detected': 'None detected',
                'key_insight': 'Configure watsonx.ai credentials for semantic analysis'
            }
        
        # Combine and truncate file contents
        combined = "\n\n---\n\n".join(file_contents[:5])  # Limit to 5 files
        if len(combined) > 8000:
            combined = combined[:8000] + "\n... (truncated)"
        
        prompt = f"""Analyze this code module and provide a structured summary.

Code:
{combined}

Provide a JSON response with these fields:
- purpose: What this module does (1-2 sentences)
- architectural_role: Its role in the system (e.g., "Data Layer", "API Controller", "Utility")
- patterns_detected: Design patterns used (e.g., "Singleton", "Factory", "Observer")
- key_insight: Most important thing to know about this module (1 sentence)

JSON Response:"""
        
        response = self._generate(prompt, max_tokens=500)
        
        # Parse JSON response
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                return result
            else:
                # Fallback if JSON parsing fails
                return {
                    'purpose': response[:200],
                    'architectural_role': 'Unknown',
                    'patterns_detected': 'Analysis in progress',
                    'key_insight': 'See full analysis'
                }
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response from Granite")
            return {
                'purpose': response[:200],
                'architectural_role': 'Unknown',
                'patterns_detected': 'Analysis in progress',
                'key_insight': 'See full analysis'
            }
    
    def explain_for_role(self, file_content: str, role: str) -> str:
        """
        Generate role-specific explanation of code.
        
        Args:
            file_content: Source code content
            role: Target role (e.g., "developer", "frontend", "backend", "devops")
            
        Returns:
            Plain-language explanation tailored to the role
        """
        if self.fallback_mode:
            return "Semantic analysis unavailable (watsonx.ai credentials not configured)"
        
        # Truncate if too long
        if len(file_content) > 6000:
            file_content = file_content[:6000] + "\n... (truncated)"
        
        role_contexts = {
            'developer': 'a software developer who needs to understand and modify this code',
            'frontend': 'a frontend developer focusing on UI/UX aspects',
            'backend': 'a backend developer focusing on data and business logic',
            'devops': 'a DevOps engineer focusing on deployment and operations',
            'architect': 'a software architect focusing on design patterns and structure',
            'junior': 'a junior developer new to the codebase'
        }
        
        context = role_contexts.get(role.lower(), 'a developer')
        
        prompt = f"""Explain this code for {context}.

Code:
{file_content}

Provide a clear, concise explanation that:
1. Describes what the code does
2. Highlights aspects most relevant to a {role}
3. Points out important patterns or conventions
4. Mentions any gotchas or important details

Explanation:"""
        
        return self._generate(prompt, max_tokens=800)
    
    def detect_modernization_opportunities(self, file_content: str) -> List[Dict[str, Any]]:
        """
        Detect modernization opportunities in code.
        
        Args:
            file_content: Source code content
            
        Returns:
            List of opportunities with issue, severity, suggestion, effort_estimate
        """
        if self.fallback_mode:
            return [{
                'issue': 'Semantic analysis unavailable',
                'severity': 'info',
                'suggestion': 'Configure watsonx.ai credentials',
                'effort_estimate': 'N/A'
            }]
        
        # Truncate if too long
        if len(file_content) > 6000:
            file_content = file_content[:6000] + "\n... (truncated)"
        
        prompt = f"""Analyze this code for modernization opportunities.

Code:
{file_content}

Identify issues and provide suggestions. Return a JSON array with objects containing:
- issue: Description of the problem
- severity: "low", "medium", or "high"
- suggestion: How to fix it
- effort_estimate: "small" (< 1 day), "medium" (1-3 days), or "large" (> 3 days)

Focus on:
- Deprecated patterns or libraries
- Performance improvements
- Security concerns
- Code maintainability
- Modern best practices

JSON Response:"""
        
        response = self._generate(prompt, max_tokens=800)
        
        # Parse JSON response
        try:
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                return result
            else:
                return [{
                    'issue': 'Analysis in progress',
                    'severity': 'info',
                    'suggestion': response[:200],
                    'effort_estimate': 'unknown'
                }]
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response from Granite")
            return [{
                'issue': 'Analysis in progress',
                'severity': 'info',
                'suggestion': response[:200],
                'effort_estimate': 'unknown'
            }]
    
    def generate_onboarding_section(self, context: Dict[str, Any]) -> str:
        """
        Generate a markdown section for onboarding guide.
        
        Args:
            context: Dictionary with module info (name, files, purpose, etc.)
            
        Returns:
            Markdown formatted section
        """
        if self.fallback_mode:
            return f"""## {context.get('name', 'Module')}

*Semantic analysis unavailable. Configure watsonx.ai credentials for detailed insights.*

**Files**: {len(context.get('files', []))}
"""
        
        prompt = f"""Generate an onboarding guide section for this module.

Module Information:
{json.dumps(context, indent=2)}

Create a markdown section that includes:
1. Module overview (what it does)
2. Key files and their purposes
3. Important concepts to understand
4. Common tasks developers perform here
5. Tips for working with this module

Use clear, friendly language suitable for new team members.

Markdown Section:"""
        
        return self._generate(prompt, max_tokens=1000)
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get token usage and cost statistics.
        
        Returns:
            Dictionary with usage stats
        """
        return {
            'total_input_tokens': int(self.total_input_tokens),
            'total_output_tokens': int(self.total_output_tokens),
            'total_tokens': int(self.total_input_tokens + self.total_output_tokens),
            'estimated_cost_usd': round(self.total_cost, 4),
            'fallback_mode': self.fallback_mode
        }
    
    def reset_usage_stats(self):
        """Reset token usage and cost tracking."""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0


# Example usage
if __name__ == "__main__":
    client = GraniteClient()
    
    if not client.fallback_mode:
        print("✓ Connected to watsonx.ai Granite")
        
        # Test summarization
        sample_code = ["""
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price
    return total
"""]
        
        summary = client.summarize_module(sample_code)
        print("\nModule Summary:")
        print(json.dumps(summary, indent=2))
        
        # Print usage stats
        stats = client.get_usage_stats()
        print("\nUsage Stats:")
        print(json.dumps(stats, indent=2))
    else:
        print("✗ Using fallback mode (credentials not configured)")

# Made with Bob
