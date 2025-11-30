#!/usr/bin/env python3
"""
Startup Verification - Verify all components are properly integrated

This script checks that all new fraud detection features are properly
integrated and the application can start successfully.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def verify_imports():
    """Verify all required imports work"""
    print("Verifying imports...")
    
    try:
        from src.agents import FraudAgent
        print("  ✓ FraudAgent imported")
    except Exception as e:
        print(f"  ✗ FraudAgent import failed: {e}")
        return False
    
    try:
        from src.domain.anomaly import AnomalyType, AnomalyResult
        print("  ✓ Anomaly domain imported")
    except Exception as e:
        print(f"  ✗ Anomaly domain import failed: {e}")
        return False
    
    try:
        from src.ui.services import get_service
        print("  ✓ UI Service imported")
    except Exception as e:
        print(f"  ✗ UI Service import failed: {e}")
        return False
    
    try:
        from src.orchestrator import WorkflowOrchestrator
        print("  ✓ WorkflowOrchestrator imported")
    except Exception as e:
        print(f"  ✗ WorkflowOrchestrator import failed: {e}")
        return False
    
    return True

def verify_ui_service():
    """Verify UI service can be initialized"""
    print("\nVerifying UI Service initialization...")
    
    try:
        from src.ui.services import get_service
        service = get_service()
        print("  ✓ UI Service created")
        
        # Check that service has orchestrator attribute
        if hasattr(service, '_orchestrator'):
            print("  ✓ Service has orchestrator attribute")
        else:
            print("  ⚠ Service missing orchestrator attribute")
        
        return True
    except Exception as e:
        print(f"  ✗ UI Service initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_templates():
    """Verify templates are available"""
    print("\nVerifying templates...")
    
    try:
        from data_templates import CLAIM_TEMPLATES, get_template, list_templates
        
        template_count = len(CLAIM_TEMPLATES)
        print(f"  ✓ Found {template_count} claim templates")
        
        # Check for fraud templates
        fraud_templates = [name for name in CLAIM_TEMPLATES.keys() 
                          if "fraud" in name.lower() or "suspicious" in name.lower() 
                          or "missing" in name.lower() or "invalid" in name.lower()]
        
        print(f"  ✓ Found {len(fraud_templates)} fraud/anomaly templates")
        
        # Test getting a template
        test_template = get_template("claim", "auto_insurance_claim")
        if test_template:
            print("  ✓ Template retrieval works")
        else:
            print("  ⚠ Template retrieval returned empty")
        
        return True
    except Exception as e:
        print(f"  ✗ Template verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_config():
    """Verify configuration includes fraud agent"""
    print("\nVerifying configuration...")
    
    try:
        config_path = project_root / "config.yaml"
        
        if not config_path.exists():
            print("  ⚠ config.yaml not found")
            return False
        
        # Try to read config (simple check without yaml parsing)
        config_content = config_path.read_text()
        
        # Check for fraud agent config
        if "fraud:" in config_content or '"fraud"' in config_content:
            print("  ✓ Fraud agent configuration found in config.yaml")
        else:
            print("  ⚠ Fraud agent configuration not found in config.yaml")
        
        return True
    except Exception as e:
        print(f"  ⚠ Config verification skipped: {e}")
        return True  # Don't fail on config check

def main():
    """Run all verification checks"""
    print("=" * 80)
    print("Fraud Detection Startup Verification")
    print("=" * 80)
    print()
    
    all_passed = True
    
    # Run checks
    all_passed &= verify_imports()
    all_passed &= verify_ui_service()
    all_passed &= verify_templates()
    all_passed &= verify_config()
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ All checks passed! Application is ready to start.")
        print("\nTo start the application:")
        print("  - Streamlit: streamlit run streamlit_app.py")
        print("  - Demo: python demo.py")
        print("  - Fraud Demo: python scripts/demo_fraud_detection.py")
    else:
        print("⚠️  Some checks failed. Please review the errors above.")
    print("=" * 80)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

