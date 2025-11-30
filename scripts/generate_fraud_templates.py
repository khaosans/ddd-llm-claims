#!/usr/bin/env python3
"""
Template Generator - Generate fraud and anomaly test templates using LLM

This script uses LLM to generate new test templates for fraud detection.
It can generate variations of existing templates or create completely new ones.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.model_provider import create_model_provider
from data_templates import CLAIM_TEMPLATES, get_template


class TemplateGenerator:
    """Generate test templates using LLM"""
    
    def __init__(self, model_provider=None):
        """Initialize template generator"""
        self.model_provider = model_provider
    
    async def generate_fraud_template(
        self,
        template_type: str,
        description: str,
        fraud_indicators: List[str],
        severity: str = "medium"
    ) -> str:
        """
        Generate a fraud template using LLM.
        
        Args:
            template_type: Type of fraud (e.g., "stolen_vehicle", "inflated_damage")
            description: Description of the fraud scenario
            fraud_indicators: List of fraud indicators to include
            severity: Severity level (low, medium, high, critical)
        
        Returns:
            Generated template string
        """
        prompt = f"""Generate a realistic insurance claim email that demonstrates {template_type} fraud.

Requirements:
- Type: {template_type}
- Description: {description}
- Fraud Indicators: {', '.join(fraud_indicators)}
- Severity: {severity}

The claim should:
1. Appear realistic but contain subtle fraud indicators
2. Include all standard claim information (date, location, amount, policy number)
3. Contain the specified fraud indicators naturally
4. Be written as an email from a claimant
5. Use realistic names, locations, and details

Output ONLY the email text, no additional explanation or formatting.

Example format:
Subject: [Appropriate Subject]

[Email body with claim details]

[Claimant name and contact info]"""

        if not self.model_provider:
            # Fallback to mock template
            return self._generate_mock_template(template_type, description, fraud_indicators)
        
        response = await self.model_provider.generate(
            prompt=prompt,
            system_prompt="You are an expert at creating realistic insurance claim scenarios for testing fraud detection systems.",
            temperature=0.7
        )
        
        return response.strip()
    
    async def generate_variation(
        self,
        base_template_name: str,
        variation_type: str = "minor",
        changes: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Generate a variation of an existing template.
        
        Args:
            base_template_name: Name of template to vary
            variation_type: Type of variation (minor, moderate, major)
            changes: Specific changes to make (e.g., {{"amount": "50000", "location": "New York"}})
        
        Returns:
            Generated variation template
        """
        base_template = get_template("claim", base_template_name)
        
        if not base_template:
            raise ValueError(f"Template '{base_template_name}' not found")
        
        variation_instructions = {
            "minor": "Make minor changes: adjust dates, names, or amounts slightly",
            "moderate": "Modify key details: change location, amount, or incident type",
            "major": "Significantly alter the claim while keeping the same fraud pattern"
        }
        
        instructions = variation_instructions.get(variation_type, variation_instructions["minor"])
        
        change_text = ""
        if changes:
            change_text = f"\nSpecific changes requested:\n"
            for key, value in changes.items():
                change_text += f"- {key}: {value}\n"
        
        prompt = f"""Create a variation of this insurance claim template:

ORIGINAL TEMPLATE:
{base_template}

VARIATION TYPE: {variation_type}
INSTRUCTIONS: {instructions}
{change_text}

Generate a new claim email that:
1. Follows the same fraud pattern as the original
2. Applies the requested variation
3. Maintains realism and natural language
4. Includes all necessary claim details

Output ONLY the email text, no additional explanation."""
        
        if not self.model_provider:
            return self._generate_mock_variation(base_template, changes)
        
        response = await self.model_provider.generate(
            prompt=prompt,
            system_prompt="You are an expert at creating variations of insurance claim templates for testing.",
            temperature=0.8
        )
        
        return response.strip()
    
    async def generate_random_template(
        self,
        fraud_type: Optional[str] = None,
        include_anomalies: bool = True
    ) -> Dict[str, str]:
        """
        Generate a random fraud/anomaly template.
        
        Args:
            fraud_type: Specific fraud type (optional, random if None)
            include_anomalies: Whether to include data quality anomalies
        
        Returns:
            Dictionary with template name and content
        """
        fraud_types = [
            "stolen_vehicle",
            "inflated_damage",
            "suspicious_timing",
            "duplicate_claim",
            "missing_documentation",
            "inconsistent_story",
        ]
        
        anomaly_types = [
            "missing_fields",
            "invalid_dates",
            "invalid_amounts",
            "policy_mismatch",
        ]
        
        selected_type = fraud_type or fraud_types[hash(str(datetime.now())) % len(fraud_types)]
        
        fraud_indicators = {
            "stolen_vehicle": ["Suspicious timing", "Location inconsistencies", "Quick reporting"],
            "inflated_damage": ["Unusually high costs", "Minor incident, major damage", "Unrealistic estimates"],
            "suspicious_timing": ["Claim immediately after policy start", "Very quick reporting", "Suspicious dates"],
            "duplicate_claim": ["Same incident multiple times", "Overlapping claims", "Repeated details"],
            "missing_documentation": ["No evidence", "Missing police report", "Insufficient details"],
            "inconsistent_story": ["Contradictory details", "Changing facts", "Unclear timeline"],
        }
        
        template = await self.generate_fraud_template(
            template_type=selected_type,
            description=f"Random {selected_type} fraud scenario",
            fraud_indicators=fraud_indicators.get(selected_type, []),
            severity="high"
        )
        
        template_name = f"generated_{selected_type}_{int(datetime.now().timestamp())}"
        
        return {
            "name": template_name,
            "content": template,
            "type": selected_type,
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_mock_template(
        self,
        template_type: str,
        description: str,
        fraud_indicators: List[str]
    ) -> str:
        """Generate a mock template when LLM is not available"""
        return f"""Subject: {template_type.replace('_', ' ').title()} Claim

Dear Insurance Company,

{description}

This claim demonstrates the following fraud indicators:
{chr(10).join(f'- {indicator}' for indicator in fraud_indicators)}

INCIDENT DETAILS:
- Date: January 15, 2024
- Location: Main Street
- Amount: $5,000.00
- Policy: POL-2024-001234

Please process this claim.

Thank you,
Test Claimant
test@email.com"""

    def _generate_mock_variation(
        self,
        base_template: str,
        changes: Optional[Dict[str, str]]
    ) -> str:
        """Generate a mock variation when LLM is not available"""
        variation = base_template
        if changes:
            for key, value in changes.items():
                variation = variation.replace(key, value)
        return variation


async def generate_templates_interactive():
    """Interactive template generation"""
    print("=" * 80)
    print("Fraud Detection Template Generator")
    print("=" * 80)
    print()
    
    # Try to initialize model provider
    try:
        provider = create_model_provider("ollama", "llama3.2:3b")
        print("✓ Using Ollama for template generation")
    except Exception as e:
        print(f"⚠️  Ollama not available: {e}")
        print("   Using mock template generation")
        provider = None
    
    generator = TemplateGenerator(provider)
    
    while True:
        print("\nOptions:")
        print("1. Generate new fraud template")
        print("2. Generate variation of existing template")
        print("3. Generate random template")
        print("4. Batch generate multiple templates")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            template_type = input("Template type (e.g., stolen_vehicle, inflated_damage): ").strip()
            description = input("Description: ").strip()
            indicators_input = input("Fraud indicators (comma-separated): ").strip()
            indicators = [i.strip() for i in indicators_input.split(",")]
            severity = input("Severity (low/medium/high/critical) [medium]: ").strip() or "medium"
            
            print("\nGenerating template...")
            template = await generator.generate_fraud_template(
                template_type, description, indicators, severity
            )
            print("\nGenerated Template:")
            print("-" * 80)
            print(template)
            print("-" * 80)
            
            save = input("\nSave template? (y/n): ").strip().lower()
            if save == "y":
                name = input("Template name: ").strip()
                save_template(name, template)
        
        elif choice == "2":
            print("\nAvailable templates:")
            for i, name in enumerate(CLAIM_TEMPLATES.keys(), 1):
                print(f"  {i}. {name}")
            
            template_name = input("\nTemplate name to vary: ").strip()
            variation_type = input("Variation type (minor/moderate/major) [minor]: ").strip() or "minor"
            
            print("\nGenerating variation...")
            variation = await generator.generate_variation(template_name, variation_type)
            print("\nGenerated Variation:")
            print("-" * 80)
            print(variation)
            print("-" * 80)
            
            save = input("\nSave variation? (y/n): ").strip().lower()
            if save == "y":
                name = input("Variation name: ").strip()
                save_template(name, variation)
        
        elif choice == "3":
            fraud_type = input("Fraud type (optional, press Enter for random): ").strip() or None
            print("\nGenerating random template...")
            result = await generator.generate_random_template(fraud_type)
            print("\nGenerated Template:")
            print("-" * 80)
            print(f"Name: {result['name']}")
            print(f"Type: {result['type']}")
            print(f"\nContent:\n{result['content']}")
            print("-" * 80)
            
            save = input("\nSave template? (y/n): ").strip().lower()
            if save == "y":
                save_template(result['name'], result['content'])
        
        elif choice == "4":
            count = int(input("Number of templates to generate [5]: ").strip() or "5")
            fraud_type = input("Fraud type (optional, press Enter for random): ").strip() or None
            
            print(f"\nGenerating {count} templates...")
            templates = []
            for i in range(count):
                print(f"  Generating template {i+1}/{count}...")
                result = await generator.generate_random_template(fraud_type)
                templates.append(result)
            
            print(f"\nGenerated {len(templates)} templates:")
            for template in templates:
                print(f"  - {template['name']} ({template['type']})")
            
            save_all = input("\nSave all templates? (y/n): ").strip().lower()
            if save_all == "y":
                for template in templates:
                    save_template(template['name'], template['content'])
                print(f"✓ Saved {len(templates)} templates")
        
        elif choice == "5":
            print("\nExiting...")
            break
        
        else:
            print("Invalid option")


def save_template(name: str, content: str):
    """Save template to file"""
    templates_dir = project_root / "generated_templates"
    templates_dir.mkdir(exist_ok=True)
    
    template_file = templates_dir / f"{name}.txt"
    template_file.write_text(content)
    print(f"✓ Saved to {template_file}")


async def main():
    """Main entry point"""
    await generate_templates_interactive()


if __name__ == "__main__":
    asyncio.run(main())

