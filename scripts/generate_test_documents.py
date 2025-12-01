"""
Test Document Generator

Generates legitimate and suspicious test documents for testing document
validation, authenticity checking, and compliance rules.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFont
    import piexif
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False


class TestDocumentGenerator:
    """Generator for test documents"""
    
    def __init__(self, output_dir: str = "data/test_documents"):
        """
        Initialize the generator.
        
        Args:
            output_dir: Base directory for test documents
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metadata = []
    
    def generate_all(self) -> None:
        """Generate all test documents"""
        print("Generating test documents...")
        
        # Generate legitimate documents
        self.generate_legitimate_documents()
        
        # Generate suspicious documents
        self.generate_suspicious_documents()
        
        # Save metadata
        self.save_metadata()
        
        # Create README
        self.create_readme()
        
        print(f"\n✅ Test documents generated in {self.output_dir}")
        print(f"   Total documents: {len(self.metadata)}")
    
    def generate_legitimate_documents(self) -> None:
        """Generate legitimate test documents"""
        print("\n📄 Generating legitimate documents...")
        
        # Auto claims
        self._generate_police_report_valid()
        self._generate_accident_photo_valid()
        self._generate_repair_estimate_valid()
        self._generate_invoice_valid()
        
        # Property claims
        self._generate_damage_photo_valid()
        self._generate_inspection_report_valid()
        self._generate_contractor_estimate_valid()
        
        # Health claims
        self._generate_medical_record_valid()
        self._generate_prescription_valid()
        
        # High-value claims
        self._generate_appraisal_valid()
        self._generate_expert_report_valid()
    
    def generate_suspicious_documents(self) -> None:
        """Generate suspicious test documents"""
        print("\n⚠️  Generating suspicious documents...")
        
        # Tampered images
        self._generate_photo_no_exif()
        self._generate_photo_edited()
        self._generate_photo_wrong_timestamp()
        self._generate_photo_low_resolution()
        
        # Fake documents
        self._generate_police_report_fake()
        self._generate_invoice_fake()
        
        # Incomplete/invalid
        self._generate_photo_corrupted()
        self._generate_document_corrupted()
    
    def _generate_police_report_valid(self) -> None:
        """Generate valid police report PDF"""
        if not REPORTLAB_AVAILABLE:
            print("  ⚠️  reportlab not available, skipping PDF generation")
            return
        
        output_path = self.output_dir / "legitimate" / "auto_claims" / "police_report_valid.pdf"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        story.append(Paragraph("POLICE ACCIDENT REPORT", styles['Title']))
        story.append(Spacer(1, 0.2*inch))
        
        # Report details
        incident_date = datetime(2024, 1, 15, 14, 30)
        report_data = [
            ['Report Number:', 'PR-2024-001234'],
            ['Date of Incident:', incident_date.strftime('%Y-%m-%d %H:%M')],
            ['Location:', 'Main Street and Oak Avenue'],
            ['Officer:', 'Officer J. Smith'],
            ['Badge Number:', '12345'],
        ]
        
        table = Table(report_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, (0, 0, 0)),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        # Incident description
        story.append(Paragraph("INCIDENT DESCRIPTION", styles['Heading2']))
        story.append(Paragraph(
            "Rear-end collision occurred at intersection. Vehicle A was stopped at red light. "
            "Vehicle B failed to stop and collided with rear of Vehicle A. No injuries reported. "
            "Damage estimated at $3,500.",
            styles['Normal']
        ))
        
        doc.build(story)
        
        # Add metadata
        self._add_pdf_metadata(
            output_path,
            title="Police Accident Report",
            author="Police Department",
            subject="Traffic Accident Report",
            creation_date=incident_date,
        )
        
        self.metadata.append({
            "file": str(output_path.relative_to(self.output_dir)),
            "type": "police_report",
            "category": "legitimate",
            "expected_compliance": True,
            "expected_authenticity_score": 0.9,
            "description": "Valid police report with proper metadata and dates matching claim",
        })
        print(f"  ✅ Created: {output_path.name}")
    
    def _generate_accident_photo_valid(self) -> None:
        """Generate valid accident photo with EXIF data"""
        if not PILLOW_AVAILABLE:
            print("  ⚠️  Pillow not available, skipping image generation")
            return
        
        output_path = self.output_dir / "legitimate" / "auto_claims" / "accident_photo_valid.jpg"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create a realistic-looking accident scene image
        img = Image.new('RGB', (1920, 1080), color='lightgray')
        draw = ImageDraw.Draw(img)
        
        # Draw a simple scene (road, cars, etc.)
        # Road
        draw.rectangle([0, 400, 1920, 680], fill='darkgray')
        # Car 1 (rear-ended)
        draw.rectangle([800, 450, 1000, 550], fill='blue')
        # Car 2 (rear)
        draw.rectangle([1000, 450, 1200, 550], fill='red')
        
        # Add EXIF data
        incident_date = datetime(2024, 1, 15, 14, 30)
        exif_dict = {
            "0th": {
                piexif.ImageIFD.Make: b"Canon",
                piexif.ImageIFD.Model: b"Canon EOS 5D Mark IV",
                piexif.ImageIFD.DateTime: incident_date.strftime("%Y:%m:%d %H:%M:%S").encode(),
            },
            "Exif": {
                piexif.ExifIFD.DateTimeOriginal: incident_date.strftime("%Y:%m:%d %H:%M:%S").encode(),
                piexif.ExifIFD.DateTimeDigitized: incident_date.strftime("%Y:%m:%d %H:%M:%S").encode(),
            },
        }
        
        exif_bytes = piexif.dump(exif_dict)
        img.save(str(output_path), "JPEG", exif=exif_bytes, quality=95)
        
        self.metadata.append({
            "file": str(output_path.relative_to(self.output_dir)),
            "type": "photo",
            "category": "legitimate",
            "expected_compliance": True,
            "expected_authenticity_score": 0.95,
            "description": "Valid accident photo with EXIF metadata (camera info, timestamp)",
        })
        print(f"  ✅ Created: {output_path.name}")
    
    def _generate_repair_estimate_valid(self) -> None:
        """Generate valid repair estimate PDF"""
        if not REPORTLAB_AVAILABLE:
            return
        
        output_path = self.output_dir / "legitimate" / "auto_claims" / "repair_estimate_valid.pdf"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        story.append(Paragraph("AUTO REPAIR ESTIMATE", styles['Title']))
        story.append(Spacer(1, 0.2*inch))
        
        estimate_data = [
            ['Item', 'Description', 'Amount'],
            ['Body Work', 'Rear bumper repair and paint', '$2,500.00'],
            ['Parts', 'Bumper assembly', '$800.00'],
            ['Labor', '8 hours @ $50/hour', '$400.00'],
            ['', 'TOTAL', '$3,700.00'],
        ]
        
        table = Table(estimate_data, colWidths=[1.5*inch, 3*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
            ('TEXTCOLOR', (0, 0), (-1, 0), (0, 0, 0)),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, (0, 0, 0)),
            ('FONTNAME', (-1, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        story.append(table)
        
        doc.build(story)
        
        incident_date = datetime(2024, 1, 15, 14, 30)
        self._add_pdf_metadata(
            output_path,
            title="Auto Repair Estimate",
            author="ABC Auto Repair",
            subject="Vehicle Repair Estimate",
            creation_date=incident_date + timedelta(days=1),
        )
        
        self.metadata.append({
            "file": str(output_path.relative_to(self.output_dir)),
            "type": "estimate",
            "category": "legitimate",
            "expected_compliance": True,
            "expected_authenticity_score": 0.85,
            "description": "Valid repair estimate with proper formatting and dates",
        })
        print(f"  ✅ Created: {output_path.name}")
    
    def _generate_invoice_valid(self) -> None:
        """Generate valid invoice PDF"""
        if not REPORTLAB_AVAILABLE:
            return
        
        output_path = self.output_dir / "legitimate" / "auto_claims" / "invoice_valid.pdf"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        story.append(Paragraph("INVOICE", styles['Title']))
        story.append(Spacer(1, 0.2*inch))
        
        invoice_data = [
            ['Invoice #:', 'INV-2024-001234'],
            ['Date:', '2024-01-20'],
            ['Customer:', 'John Doe'],
            ['Service:', 'Vehicle Repair'],
            ['Amount:', '$3,500.00'],
        ]
        
        table = Table(invoice_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, (0, 0, 0)),
        ]))
        story.append(table)
        
        doc.build(story)
        
        self._add_pdf_metadata(
            output_path,
            title="Invoice",
            author="ABC Auto Repair",
            subject="Service Invoice",
            creation_date=datetime(2024, 1, 20),
        )
        
        self.metadata.append({
            "file": str(output_path.relative_to(self.output_dir)),
            "type": "invoice",
            "category": "legitimate",
            "expected_compliance": True,
            "expected_authenticity_score": 0.85,
            "description": "Valid invoice with proper formatting and dates",
        })
        print(f"  ✅ Created: {output_path.name}")
    
    def _generate_damage_photo_valid(self) -> None:
        """Generate valid property damage photo"""
        if not PILLOW_AVAILABLE:
            return
        
        output_path = self.output_dir / "legitimate" / "property_claims" / "damage_photo_valid.jpg"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        img = Image.new('RGB', (1920, 1080), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # Draw property damage scene
        draw.rectangle([200, 200, 800, 600], fill='brown', outline='black', width=3)
        draw.rectangle([300, 300, 400, 500], fill='darkblue')  # Window
        draw.polygon([(200, 200), (500, 100), (800, 200)], fill='darkred')  # Roof
        
        incident_date = datetime(2024, 1, 10, 10, 0)
        exif_dict = {
            "0th": {
                piexif.ImageIFD.Make: b"Nikon",
                piexif.ImageIFD.Model: b"Nikon D850",
                piexif.ImageIFD.DateTime: incident_date.strftime("%Y:%m:%d %H:%M:%S").encode(),
            },
            "Exif": {
                piexif.ExifIFD.DateTimeOriginal: incident_date.strftime("%Y:%m:%d %H:%M:%S").encode(),
            },
        }
        
        exif_bytes = piexif.dump(exif_dict)
        img.save(str(output_path), "JPEG", exif=exif_bytes, quality=95)
        
        self.metadata.append({
            "file": str(output_path.relative_to(self.output_dir)),
            "type": "photo",
            "category": "legitimate",
            "expected_compliance": True,
            "expected_authenticity_score": 0.95,
            "description": "Valid property damage photo with EXIF metadata",
        })
        print(f"  ✅ Created: {output_path.name}")
    
    def _generate_inspection_report_valid(self) -> None:
        """Generate valid inspection report PDF"""
        if not REPORTLAB_AVAILABLE:
            return
        
        output_path = self.output_dir / "legitimate" / "property_claims" / "inspection_report_valid.pdf"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        story.append(Paragraph("PROPERTY INSPECTION REPORT", styles['Title']))
        story.append(Spacer(1, 0.2*inch))
        
        report_text = """
        Property Address: 123 Main Street
        
        Inspection Date: 2024-01-12
        
        Inspector: John Smith, Licensed Inspector #12345
        
        Findings:
        - Water damage to kitchen ceiling
        - Estimated repair cost: $5,000
        - Cause: Pipe leak in upstairs bathroom
        
        Recommendations:
        - Immediate repair of leaking pipe
        - Ceiling replacement required
        - Professional contractor recommended
        """
        
        story.append(Paragraph(report_text, styles['Normal']))
        doc.build(story)
        
        self._add_pdf_metadata(
            output_path,
            title="Property Inspection Report",
            author="ABC Inspections",
            subject="Property Damage Inspection",
            creation_date=datetime(2024, 1, 12),
        )
        
        self.metadata.append({
            "file": str(output_path.relative_to(self.output_dir)),
            "type": "other",
            "category": "legitimate",
            "expected_compliance": True,
            "expected_authenticity_score": 0.85,
            "description": "Valid inspection report with proper metadata",
        })
        print(f"  ✅ Created: {output_path.name}")
    
    def _generate_contractor_estimate_valid(self) -> None:
        """Generate valid contractor estimate PDF"""
        if not REPORTLAB_AVAILABLE:
            return
        
        output_path = self.output_dir / "legitimate" / "property_claims" / "contractor_estimate_valid.pdf"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        story.append(Paragraph("CONTRACTOR ESTIMATE", styles['Title']))
        story.append(Spacer(1, 0.2*inch))
        
        estimate_text = """
        Estimate Date: 2024-01-13
        
        Work Description: Ceiling repair and replacement
        
        Estimated Cost: $4,500
        
        Valid for 30 days
        """
        
        story.append(Paragraph(estimate_text, styles['Normal']))
        doc.build(story)
        
        self._add_pdf_metadata(
            output_path,
            title="Contractor Estimate",
            author="XYZ Contractors",
            subject="Repair Estimate",
            creation_date=datetime(2024, 1, 13),
        )
        
        self.metadata.append({
            "file": str(output_path.relative_to(self.output_dir)),
            "type": "estimate",
            "category": "legitimate",
            "expected_compliance": True,
            "expected_authenticity_score": 0.85,
            "description": "Valid contractor estimate",
        })
        print(f"  ✅ Created: {output_path.name}")
    
    def _generate_medical_record_valid(self) -> None:
        """Generate valid medical record PDF"""
        if not REPORTLAB_AVAILABLE:
            return
        
        output_path = self.output_dir / "legitimate" / "health_claims" / "medical_record_valid.pdf"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        story.append(Paragraph("MEDICAL RECORD", styles['Title']))
        story.append(Spacer(1, 0.2*inch))
        
        record_text = """
        Patient: Jane Doe
        Date of Service: 2024-01-08
        Provider: Dr. Smith, MD
        Diagnosis: Sprained ankle
        Treatment: X-ray, splint, medication
        Cost: $1,200
        """
        
        story.append(Paragraph(record_text, styles['Normal']))
        doc.build(story)
        
        self._add_pdf_metadata(
            output_path,
            title="Medical Record",
            author="Medical Center",
            subject="Patient Medical Record",
            creation_date=datetime(2024, 1, 8),
        )
        
        self.metadata.append({
            "file": str(output_path.relative_to(self.output_dir)),
            "type": "medical_record",
            "category": "legitimate",
            "expected_compliance": True,
            "expected_authenticity_score": 0.9,
            "description": "Valid medical record with proper formatting",
        })
        print(f"  ✅ Created: {output_path.name}")
    
    def _generate_prescription_valid(self) -> None:
        """Generate valid prescription PDF"""
        if not REPORTLAB_AVAILABLE:
            return
        
        output_path = self.output_dir / "legitimate" / "health_claims" / "prescription_valid.pdf"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        story.append(Paragraph("PRESCRIPTION", styles['Title']))
        story.append(Spacer(1, 0.2*inch))
        
        prescription_text = """
        Patient: Jane Doe
        Date: 2024-01-08
        Prescribed by: Dr. Smith, MD
        Medication: Ibuprofen 200mg
        Quantity: 30 tablets
        """
        
        story.append(Paragraph(prescription_text, styles['Normal']))
        doc.build(story)
        
        self._add_pdf_metadata(
            output_path,
            title="Prescription",
            author="Medical Center",
            subject="Prescription",
            creation_date=datetime(2024, 1, 8),
        )
        
        self.metadata.append({
            "file": str(output_path.relative_to(self.output_dir)),
            "type": "other",
            "category": "legitimate",
            "expected_compliance": True,
            "expected_authenticity_score": 0.9,
            "description": "Valid prescription document",
        })
        print(f"  ✅ Created: {output_path.name}")
    
    def _generate_appraisal_valid(self) -> None:
        """Generate valid appraisal PDF"""
        if not REPORTLAB_AVAILABLE:
            return
        
        output_path = self.output_dir / "legitimate" / "high_value_claims" / "appraisal_valid.pdf"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        story.append(Paragraph("PROFESSIONAL APPRAISAL", styles['Title']))
        story.append(Spacer(1, 0.2*inch))
        
        appraisal_text = """
        Item: Antique Jewelry Collection
        Appraised Value: $75,000
        Appraiser: Certified Appraiser #12345
        Date: 2024-01-05
        
        Detailed appraisal report with photographs and descriptions.
        """
        
        story.append(Paragraph(appraisal_text, styles['Normal']))
        doc.build(story)
        
        self._add_pdf_metadata(
            output_path,
            title="Professional Appraisal",
            author="ABC Appraisals",
            subject="Property Appraisal",
            creation_date=datetime(2024, 1, 5),
        )
        
        self.metadata.append({
            "file": str(output_path.relative_to(self.output_dir)),
            "type": "appraisal",
            "category": "legitimate",
            "expected_compliance": True,
            "expected_authenticity_score": 0.9,
            "description": "Valid appraisal document for high-value claim",
        })
        print(f"  ✅ Created: {output_path.name}")
    
    def _generate_expert_report_valid(self) -> None:
        """Generate valid expert report PDF"""
        if not REPORTLAB_AVAILABLE:
            return
        
        output_path = self.output_dir / "legitimate" / "high_value_claims" / "expert_report_valid.pdf"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        story.append(Paragraph("EXPERT ASSESSMENT REPORT", styles['Title']))
        story.append(Spacer(1, 0.2*inch))
        
        report_text = """
        Expert: Dr. Expert, PhD
        Date: 2024-01-06
        Subject: Damage Assessment
        
        Expert analysis and assessment of damages.
        Estimated value: $60,000
        """
        
        story.append(Paragraph(report_text, styles['Normal']))
        doc.build(story)
        
        self._add_pdf_metadata(
            output_path,
            title="Expert Assessment Report",
            author="Expert Services",
            subject="Damage Assessment",
            creation_date=datetime(2024, 1, 6),
        )
        
        self.metadata.append({
            "file": str(output_path.relative_to(self.output_dir)),
            "type": "other",
            "category": "legitimate",
            "expected_compliance": True,
            "expected_authenticity_score": 0.9,
            "description": "Valid expert report for high-value claim",
        })
        print(f"  ✅ Created: {output_path.name}")
    
    def _generate_photo_no_exif(self) -> None:
        """Generate photo without EXIF data (suspicious)"""
        if not PILLOW_AVAILABLE:
            return
        
        output_path = self.output_dir / "suspicious" / "tampered_images" / "photo_no_exif.jpg"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        img = Image.new('RGB', (1920, 1080), color='lightgray')
        draw = ImageDraw.Draw(img)
        draw.rectangle([800, 400, 1200, 800], fill='blue')
        
        # Save without EXIF data
        img.save(str(output_path), "JPEG", quality=95)
        
        self.metadata.append({
            "file": str(output_path.relative_to(self.output_dir)),
            "type": "photo",
            "category": "suspicious",
            "expected_compliance": True,
            "expected_authenticity_score": 0.6,
            "description": "Photo with EXIF data stripped (suspicious)",
        })
        print(f"  ⚠️  Created: {output_path.name}")
    
    def _generate_photo_edited(self) -> None:
        """Generate photo edited with Photoshop (detectable)"""
        if not PILLOW_AVAILABLE:
            return
        
        output_path = self.output_dir / "suspicious" / "tampered_images" / "photo_edited.jpg"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        img = Image.new('RGB', (1920, 1080), color='lightgray')
        draw = ImageDraw.Draw(img)
        draw.rectangle([800, 400, 1200, 800], fill='red')
        
        # Add EXIF indicating editing software
        exif_dict = {
            "0th": {
                piexif.ImageIFD.Make: b"Canon",
                piexif.ImageIFD.Model: b"Canon EOS 5D",
                piexif.ImageIFD.Software: b"Adobe Photoshop CC 2024",
            },
        }
        
        exif_bytes = piexif.dump(exif_dict)
        img.save(str(output_path), "JPEG", exif=exif_bytes, quality=95)
        
        self.metadata.append({
            "file": str(output_path.relative_to(self.output_dir)),
            "type": "photo",
            "category": "suspicious",
            "expected_compliance": True,
            "expected_authenticity_score": 0.7,
            "description": "Photo edited with Photoshop (detectable in EXIF)",
        })
        print(f"  ⚠️  Created: {output_path.name}")
    
    def _generate_photo_wrong_timestamp(self) -> None:
        """Generate photo with wrong timestamp (future date)"""
        if not PILLOW_AVAILABLE:
            return
        
        output_path = self.output_dir / "suspicious" / "tampered_images" / "photo_wrong_timestamp.jpg"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        img = Image.new('RGB', (1920, 1080), color='lightgray')
        draw = ImageDraw.Draw(img)
        draw.rectangle([800, 400, 1200, 800], fill='green')
        
        # Future timestamp (suspicious)
        future_date = datetime(2025, 12, 31, 23, 59)
        exif_dict = {
            "0th": {
                piexif.ImageIFD.DateTime: future_date.strftime("%Y:%m:%d %H:%M:%S").encode(),
            },
            "Exif": {
                piexif.ExifIFD.DateTimeOriginal: future_date.strftime("%Y:%m:%d %H:%M:%S").encode(),
            },
        }
        
        exif_bytes = piexif.dump(exif_dict)
        img.save(str(output_path), "JPEG", exif=exif_bytes, quality=95)
        
        self.metadata.append({
            "file": str(output_path.relative_to(self.output_dir)),
            "type": "photo",
            "category": "suspicious",
            "expected_compliance": True,
            "expected_authenticity_score": 0.5,
            "description": "Photo with timestamp in future (suspicious)",
        })
        print(f"  ⚠️  Created: {output_path.name}")
    
    def _generate_photo_low_resolution(self) -> None:
        """Generate low-resolution photo (suspicious)"""
        if not PILLOW_AVAILABLE:
            return
        
        output_path = self.output_dir / "suspicious" / "tampered_images" / "photo_low_resolution.jpg"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Very small image (suspicious)
        img = Image.new('RGB', (100, 100), color='lightgray')
        draw = ImageDraw.Draw(img)
        draw.rectangle([20, 20, 80, 80], fill='red')
        
        img.save(str(output_path), "JPEG", quality=50)
        
        self.metadata.append({
            "file": str(output_path.relative_to(self.output_dir)),
            "type": "photo",
            "category": "suspicious",
            "expected_compliance": True,
            "expected_authenticity_score": 0.4,
            "description": "Low-resolution photo (too small, suspicious)",
        })
        print(f"  ⚠️  Created: {output_path.name}")
    
    def _generate_police_report_fake(self) -> None:
        """Generate fake police report with inconsistent metadata"""
        if not REPORTLAB_AVAILABLE:
            return
        
        output_path = self.output_dir / "suspicious" / "fake_documents" / "police_report_fake.pdf"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        story.append(Paragraph("POLICE ACCIDENT REPORT", styles['Title']))
        story.append(Paragraph("Report Number: PR-2024-001234", styles['Normal']))
        story.append(Paragraph("Date of Incident: 2024-01-15", styles['Normal']))
        
        doc.build(story)
        
        # Add metadata with creation date AFTER incident (suspicious)
        incident_date = datetime(2024, 1, 15)
        creation_date = incident_date + timedelta(days=30)  # Created 30 days after incident
        
        self._add_pdf_metadata(
            output_path,
            title="Police Accident Report",
            author="Unknown",
            subject="Traffic Accident Report",
            creation_date=creation_date,  # Suspicious: created after incident
        )
        
        self.metadata.append({
            "file": str(output_path.relative_to(self.output_dir)),
            "type": "police_report",
            "category": "suspicious",
            "expected_compliance": True,
            "expected_authenticity_score": 0.5,
            "description": "Police report with creation date after incident (suspicious)",
        })
        print(f"  ⚠️  Created: {output_path.name}")
    
    def _generate_invoice_fake(self) -> None:
        """Generate fake invoice with suspicious formatting"""
        if not REPORTLAB_AVAILABLE:
            return
        
        output_path = self.output_dir / "suspicious" / "fake_documents" / "invoice_fake.pdf"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        story.append(Paragraph("INVOICE", styles['Title']))
        story.append(Paragraph("Amount: $10,000", styles['Normal']))
        story.append(Paragraph("Date: 2024-01-15", styles['Normal']))
        # Suspicious: minimal information, no company details
        
        doc.build(story)
        
        self._add_pdf_metadata(
            output_path,
            title="Invoice",
            author="",  # Missing author
            subject="",
            creation_date=datetime(2024, 1, 15),
        )
        
        self.metadata.append({
            "file": str(output_path.relative_to(self.output_dir)),
            "type": "invoice",
            "category": "suspicious",
            "expected_compliance": True,
            "expected_authenticity_score": 0.6,
            "description": "Invoice with suspicious formatting and missing metadata",
        })
        print(f"  ⚠️  Created: {output_path.name}")
    
    def _generate_photo_corrupted(self) -> None:
        """Generate corrupted image file"""
        output_path = self.output_dir / "suspicious" / "incomplete" / "photo_corrupted.jpg"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create a file that looks like JPEG but is corrupted
        with open(output_path, 'wb') as f:
            f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF')  # JPEG header
            f.write(b'\x00' * 100)  # Corrupted data
            f.write(b'\xff\xd9')  # JPEG footer
        
        self.metadata.append({
            "file": str(output_path.relative_to(self.output_dir)),
            "type": "photo",
            "category": "suspicious",
            "expected_compliance": False,
            "expected_authenticity_score": 0.0,
            "description": "Corrupted image file",
        })
        print(f"  ⚠️  Created: {output_path.name}")
    
    def _generate_document_corrupted(self) -> None:
        """Generate corrupted PDF file"""
        output_path = self.output_dir / "suspicious" / "incomplete" / "document_corrupted.pdf"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create a file that looks like PDF but is corrupted
        with open(output_path, 'wb') as f:
            f.write(b'%PDF-1.4\n')  # PDF header
            f.write(b'%Corrupted data\n')
            f.write(b'%%EOF')  # PDF footer
        
        self.metadata.append({
            "file": str(output_path.relative_to(self.output_dir)),
            "type": "other",
            "category": "suspicious",
            "expected_compliance": False,
            "expected_authenticity_score": 0.0,
            "description": "Corrupted PDF file",
        })
        print(f"  ⚠️  Created: {output_path.name}")
    
    def _add_pdf_metadata(
        self,
        pdf_path: Path,
        title: str,
        author: str,
        subject: str,
        creation_date: datetime,
    ) -> None:
        """Add metadata to PDF file"""
        if not PYPDF2_AVAILABLE:
            return
        
        try:
            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                pdf_writer = PyPDF2.PdfWriter()
                
                # Copy all pages
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)
                
                # Add metadata
                pdf_writer.add_metadata({
                    '/Title': title,
                    '/Author': author,
                    '/Subject': subject,
                    '/CreationDate': creation_date.strftime("D:%Y%m%d%H%M%S"),
                })
                
                # Write back
                with open(pdf_path, 'wb') as out_f:
                    pdf_writer.write(out_f)
        except Exception as e:
            print(f"  ⚠️  Warning: Could not add metadata to {pdf_path.name}: {e}")
    
    def save_metadata(self) -> None:
        """Save metadata JSON file"""
        metadata_path = self.output_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)
        print(f"\n  ✅ Saved metadata to {metadata_path.name}")
    
    def create_readme(self) -> None:
        """Create README documentation"""
        readme_path = self.output_dir / "README.md"
        
        readme_content = """# Test Documents

This directory contains test documents for validating document processing, authenticity checking, and compliance rules.

## Structure

- `legitimate/` - Valid documents that should pass validation
- `suspicious/` - Documents with issues that should be flagged
- `metadata.json` - Expected validation results for each document

## Usage

These documents can be used for:
1. Manual testing via UI (upload in process_claim.py)
2. Automated testing (test_document_validation.py)
3. Demo purposes (showing legitimate vs suspicious examples)
4. Training/documentation

## Document Categories

### Legitimate Documents

These documents should pass validation and authenticity checks:

- **Auto Claims**: Police reports, accident photos, repair estimates, invoices
- **Property Claims**: Damage photos, inspection reports, contractor estimates
- **Health Claims**: Medical records, prescriptions
- **High-Value Claims**: Appraisals, expert reports

### Suspicious Documents

These documents should be flagged by the system:

- **Tampered Images**: Missing EXIF, edited photos, wrong timestamps, low resolution
- **Fake Documents**: Inconsistent metadata, suspicious formatting
- **Corrupted Files**: Invalid file formats

## Expected Results

See `metadata.json` for expected validation results for each document.

## Generating Documents

Run the generator script:

```bash
python scripts/generate_test_documents.py
```

This will generate all test documents in the proper directory structure.
"""
        
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        print(f"  ✅ Created README.md")


def main():
    """Main entry point"""
    generator = TestDocumentGenerator()
    generator.generate_all()


if __name__ == "__main__":
    main()


