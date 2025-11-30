"""
Test Document Validation

Tests document validation, authenticity checking, and compliance rules
using the generated test documents.
"""

import json
import sys
from pathlib import Path
from uuid import UUID, uuid4

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.compliance.document_compliance_rules import get_compliance_engine
from src.compliance.document_authenticity import get_authenticity_service
from datetime import datetime

from src.domain.claim import Claim, ClaimStatus
from src.domain.claim.claim_summary import ClaimSummary
from src.domain.claim.document import Document, DocumentType, DocumentStatus
from src.storage.document_storage import DocumentStorageService


class TestDocumentValidation:
    """Test suite for document validation"""
    
    def __init__(self):
        """Initialize test suite"""
        self.test_docs_dir = Path(__file__).parent.parent / "data" / "test_documents"
        self.metadata_file = self.test_docs_dir / "metadata.json"
        self.storage_service = DocumentStorageService()
        self.compliance_engine = get_compliance_engine()
        self.authenticity_service = get_authenticity_service()
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> list:
        """Load test document metadata"""
        if not self.metadata_file.exists():
            return []
        
        with open(self.metadata_file) as f:
            return json.load(f)
    
    def test_legitimate_documents(self) -> dict:
        """
        Test that legitimate documents pass validation.
        
        Returns:
            Dict with test results
        """
        results = {
            "passed": 0,
            "failed": 0,
            "errors": [],
        }
        
        legitimate_docs = [doc for doc in self.metadata if doc["category"] == "legitimate"]
        
        print("\n📄 Testing Legitimate Documents:")
        print(f"   Found {len(legitimate_docs)} legitimate documents")
        
        for doc_info in legitimate_docs:
            try:
                doc_path = self.test_docs_dir / doc_info["file"]
                if not doc_path.exists():
                    print(f"   ⚠️  Skipping {doc_info['file']} (file not found)")
                    continue
                
                # Create a test claim
                claim = self._create_test_claim(doc_info)
                
                # Load and add document
                file_content = doc_path.read_bytes()
                document = self.storage_service.store_document(
                    claim_id=claim.claim_id,
                    file_content=file_content,
                    filename=doc_path.name,
                    document_type=DocumentType(doc_info["type"]),
                )
                
                claim.add_document(document)
                
                # Test compliance
                compliance_result = self.compliance_engine.evaluate_compliance(claim)
                
                # Test authenticity
                authenticity_result = self.authenticity_service.check_authenticity(document)
                
                # Check results
                compliance_ok = compliance_result.is_compliant == doc_info["expected_compliance"]
                authenticity_ok = (
                    authenticity_result.authenticity_score >= doc_info["expected_authenticity_score"] - 0.1
                )
                
                if compliance_ok and authenticity_ok:
                    results["passed"] += 1
                    print(f"   ✅ {doc_path.name}: PASSED")
                else:
                    results["failed"] += 1
                    error_msg = f"{doc_path.name}: "
                    if not compliance_ok:
                        error_msg += f"Compliance mismatch (expected {doc_info['expected_compliance']}, got {compliance_result.is_compliant})"
                    if not authenticity_ok:
                        error_msg += f"Authenticity score too low (expected >= {doc_info['expected_authenticity_score']}, got {authenticity_result.authenticity_score})"
                    results["errors"].append(error_msg)
                    print(f"   ❌ {error_msg}")
            
            except Exception as e:
                results["failed"] += 1
                error_msg = f"{doc_info['file']}: {str(e)}"
                results["errors"].append(error_msg)
                print(f"   ❌ {error_msg}")
        
        return results
    
    def test_suspicious_documents(self) -> dict:
        """
        Test that suspicious documents are flagged.
        
        Returns:
            Dict with test results
        """
        results = {
            "passed": 0,
            "failed": 0,
            "errors": [],
        }
        
        suspicious_docs = [doc for doc in self.metadata if doc["category"] == "suspicious"]
        
        print("\n⚠️  Testing Suspicious Documents:")
        print(f"   Found {len(suspicious_docs)} suspicious documents")
        
        for doc_info in suspicious_docs:
            try:
                doc_path = self.test_docs_dir / doc_info["file"]
                if not doc_path.exists():
                    print(f"   ⚠️  Skipping {doc_info['file']} (file not found)")
                    continue
                
                # Create a test claim
                claim = self._create_test_claim(doc_info)
                
                # Load and add document
                file_content = doc_path.read_bytes()
                
                # Skip corrupted files (they will fail to load)
                if "corrupted" in doc_path.name.lower():
                    try:
                        document = self.storage_service.store_document(
                            claim_id=claim.claim_id,
                            file_content=file_content,
                            filename=doc_path.name,
                            document_type=DocumentType(doc_info["type"]),
                        )
                    except Exception:
                        # Expected to fail for corrupted files
                        results["passed"] += 1
                        print(f"   ✅ {doc_path.name}: PASSED (correctly rejected corrupted file)")
                        continue
                
                document = self.storage_service.store_document(
                    claim_id=claim.claim_id,
                    file_content=file_content,
                    filename=doc_path.name,
                    document_type=DocumentType(doc_info["type"]),
                )
                
                claim.add_document(document)
                
                # Test authenticity (suspicious docs should have low scores)
                authenticity_result = self.authenticity_service.check_authenticity(document)
                
                # Check if suspicious document is flagged
                is_suspicious = authenticity_result.is_suspicious
                score_ok = authenticity_result.authenticity_score <= doc_info["expected_authenticity_score"] + 0.2
                
                if is_suspicious or score_ok:
                    results["passed"] += 1
                    print(f"   ✅ {doc_path.name}: PASSED (flagged as suspicious, score: {authenticity_result.authenticity_score:.2f})")
                else:
                    results["failed"] += 1
                    error_msg = f"{doc_path.name}: Not flagged as suspicious (score: {authenticity_result.authenticity_score:.2f}, expected <= {doc_info['expected_authenticity_score']})"
                    results["errors"].append(error_msg)
                    print(f"   ❌ {error_msg}")
            
            except Exception as e:
                # Some suspicious documents may fail to process (which is expected)
                if "corrupted" in str(doc_info.get("file", "")).lower():
                    results["passed"] += 1
                    print(f"   ✅ {doc_info['file']}: PASSED (correctly failed to process corrupted file)")
                else:
                    results["failed"] += 1
                    error_msg = f"{doc_info['file']}: {str(e)}"
                    results["errors"].append(error_msg)
                    print(f"   ❌ {error_msg}")
        
        return results
    
    def test_compliance_rules(self) -> dict:
        """
        Test compliance rules with different claim types.
        
        Returns:
            Dict with test results
        """
        results = {
            "passed": 0,
            "failed": 0,
            "errors": [],
        }
        
        print("\n📋 Testing Compliance Rules:")
        
        # Test 1: Auto claim without police report (should fail)
        try:
            auto_claim = Claim(
                raw_input="Auto accident claim",
                source="email",
            )
            auto_claim.summary = ClaimSummary(
                claim_type="auto",
                incident_date=datetime(2024, 1, 15, 14, 30),
                reported_date=datetime(2024, 1, 16),
                claimed_amount=3500.00,
                currency="USD",
                incident_location="Main Street",
                description="Car accident",
                claimant_name="John Doe",
            )
            
            compliance_result = self.compliance_engine.evaluate_compliance(auto_claim)
            
            if not compliance_result.is_compliant:
                results["passed"] += 1
                print("   ✅ Auto claim without police report: Correctly flagged as non-compliant")
            else:
                results["failed"] += 1
                error_msg = "Auto claim without police report: Should be non-compliant"
                results["errors"].append(error_msg)
                print(f"   ❌ {error_msg}")
        
        except Exception as e:
            results["failed"] += 1
            results["errors"].append(f"Compliance test error: {str(e)}")
            print(f"   ❌ Error: {str(e)}")
        
        # Test 2: Auto claim with police report (should pass)
        try:
            auto_claim_with_doc = Claim(
                raw_input="Auto accident claim",
                source="email",
            )
            auto_claim_with_doc.summary = ClaimSummary(
                claim_type="auto",
                incident_date=datetime(2024, 1, 15, 14, 30),
                reported_date=datetime(2024, 1, 16),
                claimed_amount=3500.00,
                currency="USD",
                incident_location="Main Street",
                description="Car accident",
                claimant_name="John Doe",
            )
            
            # Add police report
            doc_path = self.test_docs_dir / "legitimate" / "auto_claims" / "police_report_valid.pdf"
            if doc_path.exists():
                file_content = doc_path.read_bytes()
                document = self.storage_service.store_document(
                    claim_id=auto_claim_with_doc.claim_id,
                    file_content=file_content,
                    filename=doc_path.name,
                    document_type=DocumentType.POLICE_REPORT,
                )
                auto_claim_with_doc.add_document(document)
                
                compliance_result = self.compliance_engine.evaluate_compliance(auto_claim_with_doc)
                
                if compliance_result.is_compliant:
                    results["passed"] += 1
                    print("   ✅ Auto claim with police report: Correctly marked as compliant")
                else:
                    results["failed"] += 1
                    error_msg = f"Auto claim with police report: Should be compliant (missing: {[dt.value for dt in compliance_result.get_missing_document_types()]})"
                    results["errors"].append(error_msg)
                    print(f"   ❌ {error_msg}")
        
        except Exception as e:
            results["failed"] += 1
            results["errors"].append(f"Compliance test error: {str(e)}")
            print(f"   ❌ Error: {str(e)}")
        
        # Test 3: High-value claim (>$50K) without additional docs (should fail)
        try:
            high_value_claim = Claim(
                raw_input="High value claim",
                source="email",
            )
            high_value_claim.summary = ClaimSummary(
                claim_type="property",
                incident_date=datetime(2024, 1, 10),
                reported_date=datetime(2024, 1, 11),
                claimed_amount=75000.00,  # High value
                currency="USD",
                incident_location="123 Main St",
                description="Property damage",
                claimant_name="Jane Doe",
            )
            
            compliance_result = self.compliance_engine.evaluate_compliance(high_value_claim)
            
            # Should require additional documentation
            missing_docs = compliance_result.get_missing_document_types()
            has_high_value_requirement = any(
                dt in [DocumentType.INVOICE, DocumentType.RECEIPT, DocumentType.APPRAISAL]
                for dt in missing_docs
            )
            
            if has_high_value_requirement:
                results["passed"] += 1
                print("   ✅ High-value claim: Correctly requires additional documentation")
            else:
                results["failed"] += 1
                error_msg = "High-value claim: Should require additional documentation"
                results["errors"].append(error_msg)
                print(f"   ❌ {error_msg}")
        
        except Exception as e:
            results["failed"] += 1
            results["errors"].append(f"Compliance test error: {str(e)}")
            print(f"   ❌ Error: {str(e)}")
        
        return results
    
    def _create_test_claim(self, doc_info: dict) -> Claim:
        """Create a test claim for testing"""
        claim = Claim(
            raw_input="Test claim",
            source="test",
        )
        
        # Determine claim type from document type
        claim_type = "auto"
        if doc_info["type"] in ["medical_record", "prescription"]:
            claim_type = "health"
        elif doc_info["type"] in ["appraisal", "expert_report"]:
            claim_type = "property"
        
        claim.summary = ClaimSummary(
            claim_type=claim_type,
            incident_date=datetime(2024, 1, 15, 14, 30),
            reported_date=datetime(2024, 1, 16),
            claimed_amount=3500.00 if claim_type != "property" else 75000.00,
            currency="USD",
            incident_location="Main Street",
            description="Test claim",
            claimant_name="Test User",
        )
        
        return claim
    
    def run_all_tests(self) -> dict:
        """
        Run all tests.
        
        Returns:
            Dict with overall test results
        """
        print("=" * 60)
        print("Document Validation Test Suite")
        print("=" * 60)
        
        legitimate_results = self.test_legitimate_documents()
        suspicious_results = self.test_suspicious_documents()
        compliance_results = self.test_compliance_rules()
        
        total_passed = (
            legitimate_results["passed"] +
            suspicious_results["passed"] +
            compliance_results["passed"]
        )
        total_failed = (
            legitimate_results["failed"] +
            suspicious_results["failed"] +
            compliance_results["failed"]
        )
        
        all_errors = (
            legitimate_results["errors"] +
            suspicious_results["errors"] +
            compliance_results["errors"]
        )
        
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        print(f"Total Passed: {total_passed}")
        print(f"Total Failed: {total_failed}")
        
        if all_errors:
            print("\nErrors:")
            for error in all_errors:
                print(f"  - {error}")
        
        return {
            "passed": total_passed,
            "failed": total_failed,
            "errors": all_errors,
            "legitimate": legitimate_results,
            "suspicious": suspicious_results,
            "compliance": compliance_results,
        }


def main():
    """Main entry point"""
    from datetime import datetime
    
    tester = TestDocumentValidation()
    results = tester.run_all_tests()
    
    # Exit with error code if tests failed
    if results["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

