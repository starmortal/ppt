"""
Strategist Agent - Handles the 8 confirmations workflow
Follows skills/ppt-master/references/strategist.md
"""
from typing import Dict, Any
from pathlib import Path
import json
import logging

from .base_agent import BaseAgent
from ..models.session import SessionRole, SessionStage

logger = logging.getLogger(__name__)


class StrategistAgent(BaseAgent):
    """
    Strategist role agent
    Responsible for:
    1. Eight confirmations workflow
    2. Generating design_spec.md
    3. Generating spec_lock.md
    """
    
    CONFIRMATIONS = [
        "canvas_format",      # 1. Canvas format (ppt169, ppt43, etc.)
        "design_style",       # 2. Design style (dark, light, magazine, etc.)
        "color_scheme",       # 3. Color scheme
        "content_structure",  # 4. Content structure and page count
        "typography",         # 5. Typography preferences
        "image_requirements", # 6. Image requirements
        "chart_requirements", # 7. Chart/data visualization requirements
        "special_elements"    # 8. Special elements (icons, diagrams, etc.)
    ]
    
    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """
        Load strategist system prompt
        In production, this should load from:
        skills/ppt-master/references/strategist.md
        """
        # Simplified version - in production load from file
        return """You are the Strategist for PPT Master.

Your role is to conduct the Eight Confirmations with the user:

1. **Canvas Format**: Confirm PPT format (16:9, 4:3, etc.)
2. **Design Style**: Confirm visual style (dark, light, magazine, tech, nature, etc.)
3. **Color Scheme**: Confirm primary and accent colors
4. **Content Structure**: Confirm page count and content flow
5. **Typography**: Confirm font preferences
6. **Image Requirements**: Identify images needed (existing or to generate)
7. **Chart Requirements**: Identify data visualizations needed
8. **Special Elements**: Confirm icons, diagrams, or special layouts

After all confirmations:
- Generate design_spec.md with detailed specifications
- Generate spec_lock.md with locked design parameters
- Hand off to Image_Generator (if images needed) or Executor

Be conversational but thorough. Confirm one item at a time.
Track confirmations in your responses using JSON format:
{"confirmed": ["item1", "item2"], "pending": ["item3"]}
"""
    
    def process_message(
        self,
        session_id: str,
        user_message: str
    ) -> Dict[str, Any]:
        """Process user message in strategist role"""
        
        # Get session and context
        session = self.session_manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        context = session.context
        
        # Build conversation context
        conversation_context = self.build_conversation_context(session_id)
        
        # Get system prompt
        system_prompt = self.get_system_prompt(context)
        
        # Call LLM
        ai_response = self.call_llm(
            system_prompt,
            user_message,
            conversation_context
        )
        
        # Parse response for confirmations
        confirmations_status = self._extract_confirmations(ai_response, context)
        
        # Check if all confirmations complete
        all_confirmed = self._check_all_confirmed(confirmations_status)
        
        result = {
            "content": ai_response,
            "actions": [],
            "context_updates": {
                "confirmations": confirmations_status
            },
            "role_switch": None,
            "stage_switch": None
        }
        
        # If all confirmed, generate specs
        if all_confirmed and not context.get("specs_generated"):
            self.log_action("All confirmations complete", confirmations_status)
            
            # Generate design_spec.md and spec_lock.md
            spec_result = self._generate_specs(session_id, confirmations_status)
            
            result["actions"].append({
                "type": "generate_specs",
                "result": spec_result
            })
            
            result["context_updates"]["specs_generated"] = True
            result["context_updates"]["design_spec_path"] = spec_result.get("design_spec_path")
            result["context_updates"]["spec_lock_path"] = spec_result.get("spec_lock_path")
            
            # Determine next role
            if confirmations_status.get("image_requirements", {}).get("needs_generation"):
                result["role_switch"] = SessionRole.IMAGE_GENERATOR
                result["stage_switch"] = SessionStage.IMAGE_GEN
                result["content"] += "\n\n✅ All confirmations complete! Switching to Image Generator to create required images."
            else:
                result["role_switch"] = SessionRole.EXECUTOR
                result["stage_switch"] = SessionStage.EXECUTION
                result["content"] += "\n\n✅ All confirmations complete! Switching to Executor to generate slides."
        
        return result
    
    def _extract_confirmations(
        self,
        ai_response: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract confirmation status from AI response
        This is simplified - in production, use structured output
        """
        current_confirmations = context.get("confirmations", {})
        
        # Try to extract JSON from response
        try:
            # Look for JSON in response
            if "{" in ai_response and "}" in ai_response:
                start = ai_response.index("{")
                end = ai_response.rindex("}") + 1
                json_str = ai_response[start:end]
                parsed = json.loads(json_str)
                
                if "confirmed" in parsed:
                    for item in parsed["confirmed"]:
                        if item in self.CONFIRMATIONS:
                            current_confirmations[item] = {"confirmed": True}
        except:
            pass
        
        return current_confirmations
    
    def _check_all_confirmed(self, confirmations: Dict[str, Any]) -> bool:
        """Check if all required confirmations are complete"""
        for item in self.CONFIRMATIONS:
            if item not in confirmations or not confirmations[item].get("confirmed"):
                return False
        return True
    
    def _generate_specs(
        self,
        session_id: str,
        confirmations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate design_spec.md and spec_lock.md
        
        In production, this should:
        1. Use LLM to generate detailed design_spec.md
        2. Extract parameters for spec_lock.md
        3. Save both files to project directory
        """
        session = self.session_manager.get_session(session_id)
        project_id = session.project_id
        
        if not project_id:
            raise ValueError("No project linked to session")
        
        # Get project path
        project_path = Path(self.script_executor.projects_dir) / project_id
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Generate design_spec.md
        design_spec_content = self._create_design_spec(confirmations)
        design_spec_path = project_path / "design_spec.md"
        design_spec_path.write_text(design_spec_content, encoding='utf-8')
        
        # Generate spec_lock.md
        spec_lock_content = self._create_spec_lock(confirmations)
        spec_lock_path = project_path / "spec_lock.md"
        spec_lock_path.write_text(spec_lock_content, encoding='utf-8')
        
        self.log_action("Generated specs", {
            "design_spec": str(design_spec_path),
            "spec_lock": str(spec_lock_path)
        })
        
        return {
            "design_spec_path": str(design_spec_path),
            "spec_lock_path": str(spec_lock_path)
        }
    
    def _create_design_spec(self, confirmations: Dict[str, Any]) -> str:
        """Create design_spec.md content"""
        # Simplified version - in production use LLM to generate
        content = "# Design Specification\n\n"
        
        for key, value in confirmations.items():
            content += f"## {key.replace('_', ' ').title()}\n\n"
            content += f"{value}\n\n"
        
        return content
    
    def _create_spec_lock(self, confirmations: Dict[str, Any]) -> str:
        """Create spec_lock.md content"""
        # Simplified version - in production extract from confirmations
        canvas = confirmations.get("canvas_format", {})
        colors = confirmations.get("color_scheme", {})
        typography = confirmations.get("typography", {})
        
        content = f"""# Design Lock Specification

## Canvas
- Format: {canvas.get('format', 'ppt169')}
- Width: {canvas.get('width', 1280)}
- Height: {canvas.get('height', 720)}

## Colors
- Primary: {colors.get('primary', '#000000')}
- Accent: {colors.get('accent', '#FF0000')}
- Background: {colors.get('background', '#FFFFFF')}

## Typography
- Heading Font: {typography.get('heading_font', 'Arial')}
- Body Font: {typography.get('body_font', 'Arial')}
- Heading Size: {typography.get('heading_size', 32)}
- Body Size: {typography.get('body_size', 18)}

---
**DO NOT MODIFY** - This file is locked after strategist confirmation.
"""
        return content
