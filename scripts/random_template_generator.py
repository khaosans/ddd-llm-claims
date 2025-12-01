#!/usr/bin/env python3
"""
Random Template Generator - Generate random variations of templates

This utility generates random variations of existing templates for testing.
It can be used to create diverse test datasets.
"""

import random
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data_templates import CLAIM_TEMPLATES, get_template


class RandomTemplateGenerator:
    """Generate random template variations"""
    
    def __init__(self):
        """Initialize generator"""
        self.first_names = [
            "John", "Jane", "Michael", "Sarah", "David", "Emily",
            "Robert", "Jessica", "William", "Ashley", "James", "Amanda",
            "Christopher", "Melissa", "Daniel", "Michelle", "Matthew", "Lisa"
        ]
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
            "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez",
            "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson"
        ]
        self.streets = [
            "Main Street", "Oak Avenue", "Elm Street", "Park Avenue",
            "Maple Drive", "Cedar Lane", "Pine Road", "First Street",
            "Second Avenue", "Highway 101", "State Route 45"
        ]
        self.cities = [
            "Anytown", "Springfield", "Riverside", "Franklin", "Georgetown",
            "Madison", "Washington", "Jefferson", "Lincoln", "Jackson"
        ]
        self.states = ["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI"]
    
    def generate_variation(
        self,
        base_template_name: str,
        variation_level: str = "moderate"
    ) -> str:
        """
        Generate a random variation of a template.
        
        Args:
            base_template_name: Name of template to vary
            variation_level: Level of variation (minor, moderate, major)
        
        Returns:
            Varied template string
        """
        base_template = get_template("claim", base_template_name)
        if not base_template:
            raise ValueError(f"Template '{base_template_name}' not found")
        
        # Extract key information
        template_lower = base_template.lower()
        
        # Generate random replacements
        name = f"{random.choice(self.first_names)} {random.choice(self.last_names)}"
        email = f"{name.lower().replace(' ', '.')}@email.com"
        phone = f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"
        
        # Random date (within last 6 months)
        days_ago = random.randint(1, 180)
        incident_date = datetime.now() - timedelta(days=days_ago)
        reported_date = incident_date + timedelta(days=random.randint(0, 7))
        
        # Random location
        location = f"{random.randint(100, 9999)} {random.choice(self.streets)}, {random.choice(self.cities)}, {random.choice(self.states)} {random.randint(10000, 99999)}"
        
        # Random amount (based on variation level)
        if variation_level == "minor":
            base_amount = random.uniform(1000, 10000)
        elif variation_level == "moderate":
            base_amount = random.uniform(5000, 50000)
        else:  # major
            base_amount = random.uniform(10000, 150000)
        
        amount = f"${base_amount:,.2f}"
        
        # Apply replacements
        variation = base_template
        
        # Replace names
        if "john doe" in template_lower:
            variation = variation.replace("John Doe", name)
            variation = variation.replace("john.doe@email.com", email)
        elif "jane smith" in template_lower:
            variation = variation.replace("Jane Smith", name)
            variation = variation.replace("jane.smith@email.com", email)
        else:
            # Find and replace any name pattern
            import re
            name_pattern = r"[A-Z][a-z]+ [A-Z][a-z]+"
            variation = re.sub(name_pattern, name, variation, count=1)
        
        # Replace dates
        date_patterns = [
            r"January \d{1,2}, \d{4}",
            r"February \d{1,2}, \d{4}",
            r"March \d{1,2}, \d{4}",
            r"April \d{1,2}, \d{4}",
            r"May \d{1,2}, \d{4}",
            r"June \d{1,2}, \d{4}",
            r"July \d{1,2}, \d{4}",
            r"August \d{1,2}, \d{4}",
            r"September \d{1,2}, \d{4}",
            r"October \d{1,2}, \d{4}",
            r"November \d{1,2}, \d{4}",
            r"December \d{1,2}, \d{4}",
            r"\d{4}-\d{2}-\d{2}",
        ]
        
        incident_date_str = incident_date.strftime("%B %d, %Y")
        reported_date_str = reported_date.strftime("%B %d, %Y")
        
        for pattern in date_patterns:
            import re
            matches = list(re.finditer(pattern, variation))
            if matches:
                variation = re.sub(pattern, incident_date_str, variation, count=1)
                break
        
        # Replace amounts
        amount_patterns = [
            r"\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?",
            r"\$\d+(?:\.\d{2})?",
        ]
        
        for pattern in amount_patterns:
            import re
            if re.search(pattern, variation):
                variation = re.sub(pattern, amount, variation, count=1)
                break
        
        # Replace locations
        location_patterns = [
            r"\d+ [A-Z][a-z]+ (?:Street|Avenue|Drive|Road|Lane)",
            r"[A-Z][a-z]+ (?:Street|Avenue|Drive|Road|Lane) and [A-Z][a-z]+ (?:Street|Avenue|Drive|Road|Lane)",
        ]
        
        for pattern in location_patterns:
            import re
            if re.search(pattern, variation):
                variation = re.sub(pattern, location, variation, count=1)
                break
        
        # Replace emails
        email_pattern = r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}"
        import re
        if re.search(email_pattern, variation):
            variation = re.sub(email_pattern, email, variation)
        
        # Replace phone numbers
        phone_patterns = [
            r"\+1-\d{3}-\d{3}-\d{4}",
            r"\(\d{3}\) \d{3}-\d{4}",
            r"\d{3}-\d{3}-\d{4}",
        ]
        
        for pattern in phone_patterns:
            import re
            if re.search(pattern, variation):
                variation = re.sub(pattern, phone, variation, count=1)
                break
        
        return variation
    
    def generate_batch(
        self,
        template_name: str,
        count: int,
        variation_level: str = "moderate"
    ) -> List[Dict[str, str]]:
        """
        Generate a batch of variations.
        
        Args:
            template_name: Base template name
            count: Number of variations to generate
            variation_level: Level of variation
        
        Returns:
            List of variation dictionaries
        """
        variations = []
        for i in range(count):
            variation = self.generate_variation(template_name, variation_level)
            variations.append({
                "name": f"{template_name}_variation_{i+1}",
                "content": variation,
                "base_template": template_name,
                "variation_level": variation_level,
                "generated_at": datetime.now().isoformat()
            })
        return variations


def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate random template variations")
    parser.add_argument("template", help="Base template name")
    parser.add_argument("-n", "--count", type=int, default=5, help="Number of variations")
    parser.add_argument("-l", "--level", choices=["minor", "moderate", "major"], default="moderate", help="Variation level")
    parser.add_argument("-o", "--output", help="Output directory", default="generated_templates")
    
    args = parser.parse_args()
    
    generator = RandomTemplateGenerator()
    
    print(f"Generating {args.count} variations of '{args.template}'...")
    variations = generator.generate_batch(args.template, args.count, args.level)
    
    # Save variations
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)
    
    for variation in variations:
        output_file = output_dir / f"{variation['name']}.txt"
        output_file.write_text(variation['content'])
        print(f"✓ Saved: {output_file}")
    
    print(f"\n✓ Generated {len(variations)} variations")


if __name__ == "__main__":
    main()


