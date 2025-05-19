# Placeholder for categorization/categorizer.py
from typing import Dict, Any, List, Optional
import yaml
from pathlib import Path
import logging
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)

@dataclass
class EmailCategory:
    name: str
    keywords: List[str]
    priority: str
    update_sfdc: bool
    response_required: bool
    
    def should_update_sfdc(self) -> bool:
        return self.update_sfdc

class Categorizer:
    def __init__(self, config: Dict[str, Any]):
        self.categories = self._load_categories(config['path'])
    def _load_categories(self, config_path: str) -> List[EmailCategory]:
        with open(config_path, 'r') as f:
            categories_config = yaml.safe_load(f)
        return [
            EmailCategory(
                name=cat['name'],
                keywords=cat['keywords'],
                priority=cat['priority'],
                update_sfdc=cat['update_sfdc'],
                response_required=cat['response_required']
            )
            for cat in categories_config['categories']
        ]
    
    def categorize(self, email_data: Dict[str, Any]) -> EmailCategory:
        email_text = f"{email_data['subject']} {email_data['body']}".lower()
        for category in self.categories:
            if any(
                re.search(r'\b' + re.escape(keyword.lower()) + r'\b', email_text)
                for keyword in category.keywords
            ):
                logger.info(
                    f"Email from {email_data['from']} categorized as {category.name}"
                )
                return category
        logger.info(
            f"No category match for email from {email_data['from']}. Using default."
        )
        return EmailCategory(
            name='unclassified',
            keywords=[],
            priority='low',
            update_sfdc=False,
            response_required=True
        )