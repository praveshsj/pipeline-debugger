"""
Claude API integration for AI-powered incident analysis.

This service:
1. Formats incident evidence for Claude
2. Sends analysis requests to Claude API
3. Parses Claude's response for root cause and fixes
4. Updates incident records with results
"""

from typing import Dict, List, Optional
from datetime import datetime
from anthropic import Anthropic
from loguru import logger

from app.core.config import settings
from app.models.incident import Incident, Evidence, Fix


class ClaudeAnalysisService:
    """
    Service for analyzing pipeline failures using Claude AI.
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL
    
    def analyze_incident(self, incident: Incident, evidence_list: List[Evidence]) -> Dict:
        """
        Analyze an incident using Claude API.
        
        Args:
            incident: The Incident object
            evidence_list: List of Evidence objects
        
        Returns:
            Dict with analysis results:
            {
                "root_cause": str,
                "confidence": float,
                "explanation": str,
                "recommended_fixes": List[Dict],
                "blast_radius": Dict
            }
        """
        logger.info(f"Analyzing incident {incident.id} with Claude")
        
        # Format evidence for Claude
        evidence_text = self._format_evidence(evidence_list)
        
        # Create analysis prompt
        prompt = self._create_analysis_prompt(incident, evidence_text)
        
        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.1,  # Low temperature for more deterministic analysis
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse response
            analysis_text = response.content[0].text
            analysis = self._parse_analysis_response(analysis_text)
            
            logger.info(f"Claude analysis completed for incident {incident.id}")
            logger.debug(f"Root cause: {analysis['root_cause']}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            raise
    
    def _format_evidence(self, evidence_list: List[Evidence]) -> str:
        """
        Format evidence into a structured text for Claude.
        """
        sections = []
        
        # Group evidence by type
        evidence_by_type = {}
        for ev in evidence_list:
            if ev.evidence_type not in evidence_by_type:
                evidence_by_type[ev.evidence_type] = []
            evidence_by_type[ev.evidence_type].append(ev)
        
        # Format each type
        for ev_type, items in evidence_by_type.items():
            sections.append(f"\n## {ev_type.upper()}\n")
            for item in items:
                sections.append(f"### Source: {item.source or 'Unknown'}")
                sections.append(f"Collected: {item.collected_at}")
                if item.relevance_score:
                    sections.append(f"Relevance: {item.relevance_score:.2f}")
                sections.append(f"\n{item.content}\n")
                sections.append("---\n")
        
        return "\n".join(sections)
    
    def _create_analysis_prompt(self, incident: Incident, evidence_text: str) -> str:
        """
        Create the analysis prompt for Claude.
        """
        prompt = f"""You are an expert data engineer debugging a pipeline failure. 
Analyze the following incident and determine the root cause.

# INCIDENT DETAILS
- Pipeline: {incident.dag_id}
- Task: {incident.task_id}
- Execution Date: {incident.execution_date}
- Orchestrator: {incident.orchestrator}
- Error Message: {incident.error_message or 'Not provided'}

# COLLECTED EVIDENCE
{evidence_text}

# YOUR TASK
Analyze this incident and provide:

1. **ROOT CAUSE** (one sentence summary)
2. **CONFIDENCE** (0.0 to 1.0, how confident are you?)
3. **DETAILED EXPLANATION** (step-by-step reasoning)
4. **RECOMMENDED FIXES** (specific code changes or actions)
5. **BLAST RADIUS** (what else might be affected?)

# OUTPUT FORMAT
Please structure your response as JSON:

```json
{{
  "root_cause": "Brief summary of root cause",
  "confidence": 0.95,
  "explanation": "Detailed step-by-step explanation...",
  "recommended_fixes": [
    {{
      "type": "sql_patch|python_patch|config_change|manual_instruction",
      "description": "What this fix does",
      "code": "Actual code or SQL",
      "priority": 1,
      "confidence": 0.9
    }}
  ],
  "blast_radius": {{
    "affected_tasks": ["task1", "task2"],
    "data_gap_hours": 4.5,
    "estimated_backfill_cost_usd": 120.50
  }}
}}
```

Focus on providing actionable, specific fixes with actual code when possible.
Consider schema changes, dependency issues, data quality problems, and configuration errors.
"""
        return prompt
    
    def _parse_analysis_response(self, response_text: str) -> Dict:
        """
        Parse Claude's response into structured data.
        
        Expects JSON in markdown code block.
        """
        import json
        import re
        
        # Extract JSON from markdown code block
        json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON without code block
            json_str = response_text
        
        try:
            analysis = json.loads(json_str)
            return analysis
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response as JSON: {str(e)}")
            logger.debug(f"Response text: {response_text}")
            
            # Fallback: return basic structure
            return {
                "root_cause": "Unable to parse AI response",
                "confidence": 0.0,
                "explanation": response_text,
                "recommended_fixes": [],
                "blast_radius": {}
            }
    
    def generate_fix_with_context(
        self,
        incident: Incident,
        root_cause: str,
        additional_context: Optional[str] = None
    ) -> List[Dict]:
        """
        Generate specific fixes given a root cause.
        
        This can be called to generate alternative fixes or
        regenerate if the first fix didn't work.
        """
        prompt = f"""Given this pipeline failure root cause, generate specific fixes.

# INCIDENT
- Pipeline: {incident.dag_id}
- Task: {incident.task_id}
- Root Cause: {root_cause}

{f"# ADDITIONAL CONTEXT\n{additional_context}\n" if additional_context else ""}

Generate 2-3 alternative fix strategies with actual code:

1. **Quick Fix** - Fastest solution (may not be optimal)
2. **Proper Fix** - Best long-term solution
3. **Workaround** - Temporary solution if proper fix is complex

Format as JSON:
```json
[
  {{
    "type": "sql_patch|python_patch|config_change",
    "name": "Quick Fix: Revert schema change",
    "description": "...",
    "code": "...",
    "pros": ["Fast", "Low risk"],
    "cons": ["Not optimal"],
    "estimated_time_minutes": 15,
    "confidence": 0.85
  }}
]
```
"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text
            
            # Parse JSON
            import json
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
            if json_match:
                fixes = json.loads(json_match.group(1))
                return fixes
            
            return []
            
        except Exception as e:
            logger.error(f"Error generating fixes: {str(e)}")
            return []
