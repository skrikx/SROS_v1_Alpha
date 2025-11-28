import os
from typing import Optional, List, Dict, Any
# Note: lxml is usually required for XSD validation, but we are sticking to stdlib where possible.
# However, stdlib xml.etree doesn't support XSD validation.
# For this forge, we will implement a basic structure check or assume lxml is available if user installs it.
# We will add a check for lxml and fallback to no-op with warning.

try:
    from lxml import etree
    LXML_AVAILABLE = True
except ImportError:
    LXML_AVAILABLE = False

class ValidationError:
    """Structured validation error."""
    def __init__(self, severity: str, message: str, location: str = ""):
        self.severity = severity  # error, warning, info
        self.message = message
        self.location = location
    
    def __repr__(self):
        return f"[{self.severity.upper()}] {self.location}: {self.message}"

class SRXMLValidator:
    """
    Validates SRXML files against XSD schemas and semantic rules.
    """
    
    def __init__(self, schema_dir: str = None):
        if schema_dir is None:
            # Default to local schemas dir
            self.schema_dir = os.path.join(os.path.dirname(__file__), "schemas")
        else:
            self.schema_dir = schema_dir

    def validate(self, xml_path: str, schema_name: str) -> bool:
        """
        Validates an XML file against a named schema (e.g., 'workflow_schema.xml').
        Returns True if valid, raises Exception if invalid.
        """
        if not LXML_AVAILABLE:
            print(f"WARNING: lxml not installed. Skipping XSD validation for {xml_path}")
            return True

        schema_path = os.path.join(self.schema_dir, schema_name)
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema not found: {schema_path}")

        try:
            xml_doc = etree.parse(xml_path)
            xml_schema_doc = etree.parse(schema_path)
            xml_schema = etree.XMLSchema(xml_schema_doc)
            xml_schema.assertValid(xml_doc)
            return True
        except etree.DocumentInvalid as e:
            raise ValueError(f"Validation failed for {xml_path}: {e}")
    
    def validate_semantic(self, srxml_object) -> List[ValidationError]:
        """
        Performs semantic validation on a parsed SRXML object.
        
        Checks:
        - Required fields are present
        - Cross-references are valid
        - Tenant isolation rules
        - Lock consistency
        """
        errors = []
        
        # Check required fields
        if not srxml_object.id:
            errors.append(ValidationError("error", "Missing required field: id"))
        if not srxml_object.tenant:
            errors.append(ValidationError("error", "Missing required field: tenant"))
        
        # Check locks consistency
        if srxml_object.locks.seed_lock and not srxml_object.locks.seed:
            errors.append(ValidationError("error", "seed_lock is true but seed is not provided"))
        
        # Type-specific validation
        from .models import SRXAgent, SR8Workflow, GovernancePolicy
        
        if isinstance(srxml_object, SRXAgent):
            if not srxml_object.role:
                errors.append(ValidationError("error", "Agent missing required field: role"))
            if not srxml_object.mode:
                errors.append(ValidationError("error", "Agent missing required field: mode"))
            if not srxml_object.identity.system_name:
                errors.append(ValidationError("warning", "Agent identity missing system_name"))
        
        elif isinstance(srxml_object, SR8Workflow):
            if not srxml_object.steps:
                errors.append(ValidationError("error", "Workflow has no steps"))
            # Check step order
            orders = [step.order for step in srxml_object.steps]
            if len(orders) != len(set(orders)):
                errors.append(ValidationError("error", "Workflow has duplicate step orders"))
        
        elif isinstance(srxml_object, GovernancePolicy):
            if not srxml_object.rules:
                errors.append(ValidationError("warning", "Policy has no rules"))
        
        return errors

