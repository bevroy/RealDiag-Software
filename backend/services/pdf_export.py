"""
PDF Report Generation Service
=============================

Generate professional PDF reports for diagnostic findings, workup plans,
and clinical decision support results.
"""

from io import BytesIO
from datetime import datetime
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


class PDFReportGenerator:
    """Generate PDF reports for diagnostic results."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#00796b'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#00796b'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Clinical pearl style
        self.styles.add(ParagraphStyle(
            name='ClinicalPearl',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=HexColor('#92400e'),
            leftIndent=20,
            rightIndent=20,
            spaceAfter=6,
            borderColor=HexColor('#f59e0b'),
            borderWidth=1,
            borderPadding=10,
            backColor=HexColor('#fef3c7')
        ))
    
    def generate_diagnosis_report(
        self,
        diagnosis: Dict[str, Any],
        patient_info: Optional[Dict[str, Any]] = None,
        clinical_context: Optional[str] = None
    ) -> BytesIO:
        """
        Generate PDF report for a single diagnosis.
        
        Args:
            diagnosis: Diagnosis data from RulesEngine
            patient_info: Optional patient demographics
            clinical_context: Optional clinical context/notes
            
        Returns:
            BytesIO buffer containing PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        story = []
        
        # Header
        story.append(Paragraph("RealDiag Clinical Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Report metadata
        report_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        story.append(Paragraph(f"<b>Report Generated:</b> {report_date}", self.styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        
        # Patient information (if provided)
        if patient_info:
            story.append(Paragraph("Patient Information", self.styles['SectionHeader']))
            patient_data = [
                ['Patient ID:', patient_info.get('id', 'N/A')],
                ['Name:', patient_info.get('name', 'N/A')],
                ['DOB:', patient_info.get('dob', 'N/A')],
                ['Age:', str(patient_info.get('age', 'N/A'))],
            ]
            patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
            patient_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(patient_table)
            story.append(Spacer(1, 0.2*inch))
        
        # Clinical context
        if clinical_context:
            story.append(Paragraph("Clinical Context", self.styles['SectionHeader']))
            story.append(Paragraph(clinical_context, self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Diagnosis
        story.append(Paragraph("Diagnosis", self.styles['SectionHeader']))
        story.append(Paragraph(f"<b>{diagnosis.get('label', 'Unknown')}</b>", self.styles['Heading3']))
        story.append(Paragraph(f"<i>Family:</i> {diagnosis.get('family', 'N/A').title()}", self.styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        
        # ICD-10 and SNOMED codes
        if diagnosis.get('icd10'):
            icd_text = "<b>ICD-10 Codes:</b> " + ", ".join(diagnosis['icd10'])
            story.append(Paragraph(icd_text, self.styles['Normal']))
        if diagnosis.get('snomed'):
            snomed_text = "<b>SNOMED CT:</b> " + ", ".join(str(s) for s in diagnosis['snomed'])
            story.append(Paragraph(snomed_text, self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Clinical Presentations
        if diagnosis.get('presentations'):
            story.append(Paragraph("Clinical Presentations", self.styles['SectionHeader']))
            for pres in diagnosis['presentations']:
                story.append(Paragraph(f"• {pres}", self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Clinical Pearls
        if diagnosis.get('clinical_pearls'):
            story.append(Paragraph("Clinical Pearls", self.styles['SectionHeader']))
            for pearl in diagnosis['clinical_pearls']:
                story.append(Paragraph(f"💡 {pearl}", self.styles['ClinicalPearl']))
            story.append(Spacer(1, 0.2*inch))
        
        # Management
        if diagnosis.get('management'):
            story.append(Paragraph("Management", self.styles['SectionHeader']))
            for mgmt in diagnosis['management']:
                story.append(Paragraph(f"• {mgmt}", self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Tests
        if diagnosis.get('tests'):
            story.append(Paragraph("Recommended Tests", self.styles['SectionHeader']))
            for test in diagnosis['tests']:
                story.append(Paragraph(f"• {test}", self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Referrals
        if diagnosis.get('referrals'):
            story.append(Paragraph("Specialist Referrals", self.styles['SectionHeader']))
            for ref in diagnosis['referrals']:
                story.append(Paragraph(f"• {ref}", self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Footer
        story.append(Spacer(1, 0.3*inch))
        disclaimer = (
            "<i>Disclaimer: This report is generated by RealDiag Clinical Decision Support System "
            "for informational purposes only. It does not replace clinical judgment and should be "
            "used in conjunction with thorough patient evaluation and professional medical expertise. "
            "Always verify diagnoses with appropriate clinical examination and testing.</i>"
        )
        story.append(Paragraph(disclaimer, self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_multi_diagnosis_report(
        self,
        diagnoses: List[Dict[str, Any]],
        patient_info: Optional[Dict[str, Any]] = None,
        search_criteria: Optional[str] = None
    ) -> BytesIO:
        """
        Generate PDF report for multiple differential diagnoses.
        
        Args:
            diagnoses: List of diagnosis data
            patient_info: Optional patient demographics
            search_criteria: Original search symptoms/criteria
            
        Returns:
            BytesIO buffer containing PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        story = []
        
        # Header
        story.append(Paragraph("RealDiag Differential Diagnosis Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Report metadata
        report_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        story.append(Paragraph(f"<b>Report Generated:</b> {report_date}", self.styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        
        # Patient information
        if patient_info:
            story.append(Paragraph("Patient Information", self.styles['SectionHeader']))
            patient_table = Table([
                ['Patient ID:', patient_info.get('id', 'N/A')],
                ['Name:', patient_info.get('name', 'N/A')],
                ['DOB:', patient_info.get('dob', 'N/A')],
            ], colWidths=[2*inch, 4*inch])
            patient_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(patient_table)
            story.append(Spacer(1, 0.2*inch))
        
        # Search criteria
        if search_criteria:
            story.append(Paragraph("Search Criteria", self.styles['SectionHeader']))
            story.append(Paragraph(search_criteria, self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Summary table
        story.append(Paragraph(f"Differential Diagnoses ({len(diagnoses)} results)", self.styles['SectionHeader']))
        
        # Create summary table
        table_data = [['Rank', 'Diagnosis', 'Family', 'Match Score', 'ICD-10']]
        for idx, dx in enumerate(diagnoses[:10], 1):  # Top 10
            icd10 = ', '.join(dx.get('icd10', [])[:2])  # First 2 codes
            if len(dx.get('icd10', [])) > 2:
                icd10 += '...'
            table_data.append([
                str(idx),
                dx.get('label', 'Unknown')[:40],
                dx.get('family', 'N/A')[:15],
                f"{dx.get('match_score', 0):.1f}",
                icd10
            ])
        
        summary_table = Table(table_data, colWidths=[0.5*inch, 2.5*inch, 1.2*inch, 0.8*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#00796b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#f9f9f9'), HexColor('#ffffff')]),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Detailed diagnoses (top 3)
        story.append(Paragraph("Top Differential Diagnoses - Detailed", self.styles['SectionHeader']))
        
        for idx, dx in enumerate(diagnoses[:3], 1):
            story.append(Paragraph(f"{idx}. {dx.get('label', 'Unknown')}", self.styles['Heading3']))
            story.append(Paragraph(f"Match Score: {dx.get('match_score', 0):.1f}/10", self.styles['Normal']))
            
            # Clinical pearls
            if dx.get('clinical_pearls'):
                story.append(Paragraph("<b>Key Points:</b>", self.styles['Normal']))
                for pearl in dx['clinical_pearls'][:3]:  # Top 3 pearls
                    story.append(Paragraph(f"• {pearl}", self.styles['Normal']))
            
            # Management highlights
            if dx.get('management'):
                story.append(Paragraph("<b>Management:</b>", self.styles['Normal']))
                for mgmt in dx['management'][:3]:  # Top 3 management points
                    story.append(Paragraph(f"• {mgmt}", self.styles['Normal']))
            
            if idx < 3:
                story.append(Spacer(1, 0.2*inch))
        
        # Footer
        story.append(Spacer(1, 0.3*inch))
        disclaimer = (
            "<i>Disclaimer: This differential diagnosis report is generated by RealDiag for clinical decision support. "
            "Rankings are based on symptom matching algorithms and should be interpreted in the full clinical context. "
            "This tool does not replace comprehensive medical evaluation and clinical judgment.</i>"
        )
        story.append(Paragraph(disclaimer, self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
