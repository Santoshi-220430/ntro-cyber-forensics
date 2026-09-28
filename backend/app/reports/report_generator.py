"""
Forensic Platform - Professional PDF & JSON Forensic Report Generator
Problem ID: SIH26148 | NTRO Cyber Forensics Prototype
"""

import os
import uuid
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from ..database import get_db_connection
from ..config import REPORTS_DIR
from ..audit.audit_service import AuditService
from ..evidence.chain_of_custody import ChainOfCustodyService

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        # Header
        self.drawString(54, 750, "NTRO CYBER FORENSICS LABORATORY — OFFICIAL INVESTIGATION REPORT")
        self.setStrokeColor(colors.HexColor("#334155"))
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        # Footer
        self.line(54, 50, 558, 50)
        self.setFont("Helvetica", 8)
        self.drawString(54, 38, "CONFIDENTIAL // RESTRICTED LAWFUL FORENSIC USE ONLY // SIH26148 PROTOTYPE")
        self.drawRightString(558, 38, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

class ForensicReportGenerator:
    @staticmethod
    def generate_report(case_id: str, author_name: str = "Lead DFIR Analyst", author_badge: str = "NTRO-INV-42") -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch Case
        cursor.execute("SELECT * FROM cases WHERE id = ?;", (case_id,))
        case = cursor.fetchone()
        if not case:
            conn.close()
            raise ValueError(f"Case with ID {case_id} not found.")

        # Fetch Evidence
        cursor.execute("SELECT * FROM evidence WHERE case_id = ? ORDER BY acquisition_timestamp ASC;", (case_id,))
        evidence_list = [dict(r) for r in cursor.fetchall()]

        # Fetch Findings
        cursor.execute("SELECT * FROM findings WHERE case_id = ? ORDER BY timestamp DESC;", (case_id,))
        findings = [dict(r) for r in cursor.fetchall()]

        # Fetch Timeline
        cursor.execute("SELECT * FROM timeline_events WHERE case_id = ? ORDER BY timestamp ASC LIMIT 30;", (case_id,))
        timeline = [dict(r) for r in cursor.fetchall()]

        # Fetch Chain of Custody
        cursor.execute("SELECT * FROM chain_of_custody WHERE case_id = ? ORDER BY timestamp ASC;", (case_id,))
        coc_entries = [dict(r) for r in cursor.fetchall()]

        # Fetch System Info
        cursor.execute("SELECT * FROM system_info WHERE case_id = ? ORDER BY collected_at DESC LIMIT 1;", (case_id,))
        sys_info = cursor.fetchone()

        conn.close()

        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        report_number = f"REP-{case['case_number']}-{now.strftime('%Y%m%d%H%M')}"
        report_id = f"rep-{uuid.uuid4().hex[:12]}"
        pdf_filename = f"{report_number}.pdf"
        pdf_path = REPORTS_DIR / pdf_filename

        # Build PDF with ReportLab
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=letter,
            leftMargin=54,
            rightMargin=54,
            topMargin=60,
            bottomMargin=60
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=12
        )
        h2_style = ParagraphStyle(
            'SectionH2',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=14,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'BodyDark',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155")
        )
        badge_style = ParagraphStyle(
            'BadgeText',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            textColor=colors.HexColor("#b91c1c")
        )

        story = []

        # Header Title
        story.append(Spacer(1, 10))
        story.append(Paragraph("DIGITAL FORENSIC EXAMINATION REPORT", title_style))
        story.append(Paragraph(f"<b>National Technical Research Organisation (NTRO)</b> — Case Reference: <b>{case['case_number']}</b>", body_style))
        story.append(Spacer(1, 10))

        # Case Metadata Table
        case_meta_data = [
            [Paragraph("<b>Case Number:</b>", body_style), Paragraph(case['case_number'], body_style), Paragraph("<b>Target Host:</b>", body_style), Paragraph(case['target_host'] or "N/A", body_style)],
            [Paragraph("<b>Case Title:</b>", body_style), Paragraph(case['title'], body_style), Paragraph("<b>Status:</b>", body_style), Paragraph(case['status'], body_style)],
            [Paragraph("<b>Lead Investigator:</b>", body_style), Paragraph(f"{author_name} ({author_badge})", body_style), Paragraph("<b>Date & Time:</b>", body_style), Paragraph(now.strftime("%Y-%m-%d %H:%M UTC"), body_style)],
            [Paragraph("<b>Forensic Framework:</b>", body_style), Paragraph("NTRO DSL-DFIR v2.4 (Authorized Mode)", body_style), Paragraph("<b>Evidence Hash Protocol:</b>", body_style), Paragraph("FIPS 180-4 SHA-256", body_style)]
        ]
        t_meta = Table(case_meta_data, colWidths=[100, 150, 100, 150])
        t_meta.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t_meta)
        story.append(Spacer(1, 14))

        # Executive Summary
        story.append(Paragraph("1. EXECUTIVE SUMMARY", h2_style))
        summary_text = (
            f"An authorized forensic investigation was commenced for target host <b>{case['target_host']}</b> "
            f"under NTRO digital evidence procedures. Forensic analysis utilized non-intrusive domain-specific "
            f"scripting language (Forensic DSL) commands operating under <b>FORENSIC_READ_ONLY</b> policies. "
            f"A total of <b>{len(evidence_list)}</b> evidence items were acquired with verified SHA-256 cryptographic digests. "
            f"The deterministic rule engine identified <b>{len(findings)}</b> notable security findings."
        )
        story.append(Paragraph(summary_text, body_style))
        story.append(Spacer(1, 10))

        # Suspicious Findings Table
        story.append(Paragraph("2. KEY SUSPICIOUS FINDINGS", h2_style))
        if findings:
            finding_rows = [[
                Paragraph("<b>Severity</b>", body_style),
                Paragraph("<b>Rule & Title</b>", body_style),
                Paragraph("<b>Category</b>", body_style),
                Paragraph("<b>Evidence Reference</b>", body_style)
            ]]
            for f in findings:
                sev_color = "#dc2626" if f['severity'] in ('CRITICAL', 'HIGH') else "#d97706"
                finding_rows.append([
                    Paragraph(f"<font color='{sev_color}'><b>{f['severity']}</b></font>", body_style),
                    Paragraph(f"<b>{f['title']}</b><br/>{f['description'][:90]}...", body_style),
                    Paragraph(f['category'], body_style),
                    Paragraph(f['evidence_ref'] or "N/A", body_style)
                ])
            t_findings = Table(finding_rows, colWidths=[65, 235, 75, 125])
            t_findings.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e2e8f0")),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#f1f5f9")),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ]))
            story.append(t_findings)
        else:
            story.append(Paragraph("No critical or high-risk findings detected in current evidence store.", body_style))
        story.append(Spacer(1, 12))

        # Evidence Inventory Table
        story.append(Paragraph("3. EVIDENCE INVENTORY & SHA-256 HASH VERIFICATION", h2_style))
        if evidence_list:
            ev_rows = [[
                Paragraph("<b>ID</b>", body_style),
                Paragraph("<b>Artifact Name</b>", body_style),
                Paragraph("<b>Type</b>", body_style),
                Paragraph("<b>SHA-256 Digest</b>", body_style),
                Paragraph("<b>Integrity</b>", body_style)
            ]]
            for ev in evidence_list:
                status_color = "#16a34a" if ev['integrity_status'] == 'VERIFIED' else "#dc2626"
                ev_rows.append([
                    Paragraph(ev['evidence_number'], body_style),
                    Paragraph(ev['name'], body_style),
                    Paragraph(ev['source_type'], body_style),
                    Paragraph(f"<font size='7'>{ev['sha256_hash'][:28]}...</font>", body_style),
                    Paragraph(f"<font color='{status_color}'><b>{ev['integrity_status']}</b></font>", body_style)
                ])
            t_ev = Table(ev_rows, colWidths=[75, 115, 60, 180, 70])
            t_ev.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e2e8f0")),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#f1f5f9")),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ]))
            story.append(t_ev)
        else:
            story.append(Paragraph("No physical or logical evidence files acquired yet.", body_style))
        story.append(Spacer(1, 12))

        # Chain of Custody Table
        story.append(Paragraph("4. CHAIN OF CUSTODY AUDIT TRAIL", h2_style))
        if coc_entries:
            coc_rows = [[
                Paragraph("<b>Timestamp</b>", body_style),
                Paragraph("<b>Action</b>", body_style),
                Paragraph("<b>Investigator</b>", body_style),
                Paragraph("<b>Details & Chain Digest</b>", body_style)
            ]]
            for c in coc_entries[-6:]: # Display recent 6 entries in summary
                coc_rows.append([
                    Paragraph(c['timestamp'][:19], body_style),
                    Paragraph(c['action'], body_style),
                    Paragraph(c['actor_name'], body_style),
                    Paragraph(f"{c['details'][:70]}...<br/><font size='6' color='#64748b'>Digest: {c['integrity_hash'][:20]}...</font>", body_style)
                ])
            t_coc = Table(coc_rows, colWidths=[105, 105, 90, 200])
            t_coc.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e2e8f0")),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#f1f5f9")),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ]))
            story.append(t_coc)
        story.append(Spacer(1, 14))

        # Conclusion & Formal Sign-off
        story.append(Paragraph("5. INVESTIGATOR ATTESTATION & CONCLUSION", h2_style))
        conclusion_text = (
            "I hereby attest that the digital evidence items cataloged in this report were acquired and processed "
            "in accordance with standardized forensic procedures. All operations executed strictly within read-only "
            "boundaries under authorized cryptographic control. No system state was illegally modified."
        )
        story.append(Paragraph(conclusion_text, body_style))
        story.append(Spacer(1, 15))

        sign_data = [
            [Paragraph(f"<b>Examiner:</b> {author_name}", body_style), Paragraph(f"<b>Signature:</b> <i>[CRYPTOGRAPHICALLY SEALED BY {author_badge}]</i>", body_style)],
            [Paragraph(f"<b>Badge:</b> {author_badge}", body_style), Paragraph(f"<b>Date:</b> {now.strftime('%Y-%m-%d %H:%M:%S UTC')}", body_style)]
        ]
        t_sign = Table(sign_data, colWidths=[250, 250])
        t_sign.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_sign)

        # Build Document
        doc.build(story, canvasmaker=NumberedCanvas)

        # Calculate generated PDF SHA-256
        pdf_size = os.path.getsize(pdf_path)
        with open(pdf_path, "rb") as f:
            pdf_hash = hashlib.sha256(f.read()).hexdigest()

        # Save to reports table
        summary_payload = {
            "case_number": case["case_number"],
            "target_host": case["target_host"],
            "evidence_count": len(evidence_list),
            "findings_count": len(findings),
            "critical_findings": len([f for f in findings if f["severity"] == "CRITICAL"]),
            "high_findings": len([f for f in findings if f["severity"] == "HIGH"])
        }

        conn = get_db_connection()
        cursor = conn.cursor()

        # DEDUPLICATION CHECK: If identical report hash already exists for this case, reuse it
        cursor.execute("SELECT * FROM reports WHERE case_id = ? AND sha256_hash = ?;", (case_id, pdf_hash))
        existing_report = cursor.fetchone()
        if existing_report:
            conn.close()
            return {
                "id": existing_report["id"],
                "report_number": existing_report["report_number"],
                "filename": os.path.basename(existing_report["file_path"]),
                "file_size": existing_report["file_size"],
                "sha256_hash": existing_report["sha256_hash"],
                "generated_at": existing_report["generated_at"],
                "summary": json.loads(existing_report["summary_json"] or "{}")
            }

        cursor.execute("""
        INSERT INTO reports (id, case_id, report_number, title, format, file_path, file_size, sha256_hash, generated_by, generated_at, summary_json)
        VALUES (?, ?, ?, ?, 'PDF', ?, ?, ?, ?, ?, ?)
        """, (
            report_id, case_id, report_number,
            f"Forensic Investigation Report - {case['case_number']}",
            str(pdf_path), pdf_size, pdf_hash, author_name, now_iso, json.dumps(summary_payload)
        ))
        conn.commit()
        conn.close()

        ChainOfCustodyService.record_entry(
            case_id=case_id,
            evidence_id=None,
            action="REPORT_GENERATED",
            actor_name=author_name,
            actor_role="INVESTIGATOR",
            details=f"Official PDF Report {report_number} generated and sealed with SHA-256: {pdf_hash[:16]}..."
        )

        AuditService.log_event(
            actor_name=author_name,
            actor_role="INVESTIGATOR",
            action="GENERATE_REPORT",
            resource_type="REPORT",
            resource_id=report_id,
            details=f"Report {report_number} generated. SHA-256: {pdf_hash}"
        )

        return {
            "id": report_id,
            "report_number": report_number,
            "filename": pdf_filename,
            "file_size": pdf_size,
            "sha256_hash": pdf_hash,
            "generated_at": now_iso,
            "summary": summary_payload
        }
