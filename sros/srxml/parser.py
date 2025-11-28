import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, Union
import os

class SRXMLParser:
    """
    Parses SRXML files into Python dictionaries or typed objects.
    """
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parses an SRXML file and returns a dictionary representation.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"SRXML file not found: {file_path}")
            
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        return {
            "tag": root.tag.split('}')[-1],
            **self._element_to_dict(root)
        }
    
    def parse_to_object(self, file_path: str) -> Union['SRXAgent', 'SR8Workflow', 'GovernancePolicy']:
        """
        Parses an SRXML file and returns a typed Python object.
        """
        from .models import SRXAgent, SR8Workflow, GovernancePolicy, SRXMLLocks
        
        data = self.parse(file_path)
        tag = data.get('tag')
        
        # Extract locks
        locks = SRXMLLocks(
            one_pass_lock=data.get('@one_pass_lock', 'false').lower() == 'true',
            drift_lock=data.get('@drift_lock', 'false').lower() == 'true',
            seed_lock=data.get('@seed_lock', 'false').lower() == 'true',
            seed=data.get('@seed')
        )
        
        # Common fields
        common = {
            'id': data.get('@id', ''),
            'version': data.get('@version', '1.0.0'),
            'tenant': data.get('@tenant', 'default'),
            'runtime': data.get('@runtime'),
            'locks': locks,
        }
        
        if tag == 'srx_agent_prompt' or tag == 'agent':
            identity_data = data.get('identity', {})
            return SRXAgent(
                **common,
                role=data.get('@role', ''),
                mode=data.get('@mode', ''),
                identity={
                    'system_name': identity_data.get('system_name', {}).get('#text', ''),
                    'purpose': identity_data.get('purpose', {}).get('#text', ''),
                },
                inputs=self._extract_items(data.get('inputs', {})),
                objectives=self._extract_items(data.get('objectives', {})),
            )
        elif tag == 'sr8_workflow' or tag == 'workflow':
            identity_data = data.get('identity', {})
            workflow_data = data.get('workflow', {})
            
            # Handle both nested 'workflow/step' and direct 'task' children
            steps_data = []
            if 'step' in workflow_data:
                steps_data = workflow_data.get('step', [])
            elif 'step' in data:
                steps_data = data.get('step', [])
            elif 'task' in data:
                steps_data = data.get('task', [])
            
            if not isinstance(steps_data, list):
                steps_data = [steps_data]
            
            steps = []
            for step in steps_data:
                # Handle both SR8 'step' and simple 'task' formats
                step_id = step.get('@id', '')
                agent = step.get('@agent') or step.get('agent', {}).get('#text')
                
                instruction = step.get('#text', '')
                if not instruction:
                    # Try instruction tag
                    inst_tag = step.get('instruction', {})
                    if isinstance(inst_tag, dict):
                        instruction = inst_tag.get('#text', '')
                    
                if not instruction:
                    # Try input/prompt structure
                    inp = step.get('input', {})
                    if isinstance(inp, dict):
                        instruction = inp.get('prompt', {}).get('#text', '') or inp.get('#text', '')
                
                steps.append({
                    'id': step_id,
                    'order': int(step.get('@order', 0)),
                    'instruction': instruction,
                    'agent': agent,
                })
            
            return SR8Workflow(
                **common,
                role=data.get('@role', ''),
                mode=data.get('@mode', ''),
                identity={
                    'system_name': identity_data.get('system_name', {}).get('#text', ''),
                    'purpose': identity_data.get('purpose', {}).get('#text', ''),
                },
                context=self._extract_items(data.get('context', {})),
                inputs=self._extract_items(data.get('inputs', {})),
                objectives=self._extract_items(data.get('objectives', {})),
                steps=steps,
                checks=self._extract_items(data.get('checks', {})),
                output_contract=self._extract_items(data.get('output_contract', {})),
            )
        elif tag == 'governance_policy':
            return GovernancePolicy(
                **common,
                name=data.get('name', {}).get('#text', ''),
                description=data.get('description', {}).get('#text', ''),
            )
        else:
            raise ValueError(f"Unknown SRXML document type: {tag}")
    
    def _extract_items(self, container: Dict) -> list:
        """Extract list of items from container element."""
        items = container.get('item', [])
        if not isinstance(items, list):
            items = [items]
        return [item.get('#text', '') if isinstance(item, dict) else str(item) for item in items]

    def _element_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        result = {}
        
        # Attributes
        for key, value in element.attrib.items():
            result[f"@{key}"] = value
            
        # Text content
        if element.text and element.text.strip():
            result["#text"] = element.text.strip()
            
        # Children
        for child in element:
            child_data = self._element_to_dict(child)
            tag = child.tag.split('}')[-1] # Strip namespace if present
            
            if tag in result:
                if isinstance(result[tag], list):
                    result[tag].append(child_data)
                else:
                    result[tag] = [result[tag], child_data]
            else:
                result[tag] = child_data
                
        return result

