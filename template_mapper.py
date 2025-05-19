# Placeholder for categorization/template_mapper.py
from typing import Dict, Any, Optional
import yaml
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class TemplateMapper:
    def __init__(self, config: Dict[str, Any]):
        self.templates = self._load_templates(config['path'])
        self.default_template = config['default']
    
    def _load_templates(self, templates_dir: str) -> Dict[str, str]:
        templates = {}
        templates_path = Path(templates_dir)
        for template_file in templates_path.glob('*.txt'):
            with open(template_file, 'r') as f:
                templates[template_file.stem] = f.read()
        return templates
    
    def get_template(self, category_name: str) -> str:
        if category_name in self.templates:
            return self.templates[category_name]
        lower_name = category_name.lower()
        for name, template in self.templates.items():
            if name.lower() == lower_name:
                return template
        logger.warning(
            f"No template found for category '{category_name}'. Using default."
        )
        return self.templates.get(self.default_template, '')