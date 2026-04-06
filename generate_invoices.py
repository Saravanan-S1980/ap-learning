import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

OUTPUT_DIR = "sample_invoices"
os.makedirs(OUTPUT_DIR, exist_ok=True)

BUYER = {
    "name": "Genpact India Pvt Ltd",
    "address": "Plot No. 119, Sector 44\nGurugram, Haryana - 122003",
    "gstin": "29AABCG1234A1Z5",
    "email": "ap@genpact.com",
}

INVOICES = [
    {
        "inv_num": "INV-5001",
        "vendor": {
            "name": "Wipro Limited",
            "address": "Doddakannelli, Sarjapur Road\nBengaluru, Karnataka - 560035",
            "gstin": "29AAACW0X41F1ZA",
            "email": "invoices@wipro.com",
            "bank_account": "000405009876543",
            "ifsc": "HDFC0000040",
            "state": "Karnataka",
        },
        "date": "15-Mar-2026",
        "due_date": "14-Apr-2026",
        "payment_terms": "Net 30",
        "po_ref": "PO-001",
        "description": "IT infrastructure maintenance",
        "gst_rate": 18,
        "gst_type": "intra",  # CGST + SGST
        "hsn_sac": "SAC 998314",
        "line_items": [
            ("Server maintenance & monitoring (monthly)", 1, 50000),
            ("Network infrastructure support", 1, 28000),
            ("Hardware AMC charges", 1, 17000),
        ],
        "shipping": 1200,
    },
    {
        "inv_num": "INV-5002",
        "vendor": {
            "name": "Mahindra Logistics Ltd",
            "address": "Mahindra Towers, 5th Floor\nWorli, Mumbai, Maharashtra - 400018",
            "gstin": "27AABCM2921B1ZE",
            "email": "billing@mahindralogistics.com",
            "bank_account": "00720350012345",
            "ifsc": "YESB0000072",
            "state": "Maharashtra",
        },
        "date": "18-Mar-2026",
        "due_date": "17-Apr-2026",
        "payment_terms": "Net 30",
        "po_ref": "PO-002",
        "description": "Freight and warehousing Q1",
        "gst_rate": 12,
        "gst_type": "inter",  # IGST
        "hsn_sac": "SAC 996791",
        "line_items": [
            ("Freight charges – Q1 2026", 1, 95000),
            ("Warehousing & storage fees (3 months)", 3, 16000),
            ("Last-mile delivery – Gurugram hub", 1, 18000),
        ],
        "shipping": 2500,
    },
    {
        "inv_num": "INV-5003",
        "vendor": {
            "name": "Tata Consultancy Services Ltd",
            "address": "TCS House, Raveline Street\nFort, Mumbai, Maharashtra - 400001",
            "gstin": "27AAACT2727Q1ZL",
            "email": "invoicing@tcs.com",
            "bank_account": "1234500078901",
            "ifsc": "ICIC0000124",
            "state": "Maharashtra",
        },
        "date": "20-Mar-2026",
        "due_date": "19-Apr-2026",
        "payment_terms": "Net 30",
        "po_ref": "PO-003",
        "description": "Software development services",
        "gst_rate": 18,
        "gst_type": "intra",  # CGST + SGST (buyer also in different state but using intra for demo)
        "hsn_sac": "SAC 998313",
        "line_items": [
            ("Custom ERP module development – Phase 2", 1, 200000),
            ("UAT support & bug fixes", 80, 1000),
            ("Technical documentation & handover", 1, 40000),
        ],
        "shipping": 3500,
    },
    {
        "inv_num": "INV-5004",
        "vendor": {
            "name": "Reliance Industries Ltd – Utilities Division",
            "address": "Maker Chambers IV, 3rd Floor\nNariman Point, Mumbai, Maharashtra - 400021",
            "gstin": "27AAACR4849R1ZP",
            "email": "utilities.billing@ril.com",
            "bank_account": "9087654321001",
            "ifsc": "SBIN0001234",
            "state": "Maharashtra",
        },
        "date": "22-Mar-2026",
        "due_date": "06-Apr-2026",
        "payment_terms": "Net 15",
        "po_ref": "PO-004",
        "description": "Electricity and water charges",
        "gst_rate": 5,
        "gst_type": "inter",  # IGST
        "hsn_sac": "HSN 2716",
        "line_items": [
            ("Electricity charges – Feb 2026 (42,500 units)", 42500, 0.55),
            ("Water supply charges – Feb 2026", 1, 5175),
        ],
        "shipping": 500,
    },
    {
        "inv_num": "INV-5005",
        "vendor": {
            "name": "Infosys BPO Limited",
            "address": "Electronics City, Hosur Road\nBengaluru, Karnataka - 560100",
            "gstin": "29AABCI1234M1ZX",
            "email": "accounts@infosysbpo.com",
            "bank_account": "5050101234567",
            "ifsc": "AXIS0000505",
            "state": "Karnataka",
        },
        "date": "25-Mar-2026",
        "due_date": "24-Apr-2026",
        "payment_terms": "Net 30",
        "po_ref": "PO-005",
        "description": "Finance process outsourcing",
        "gst_rate": 18,
        "gst_type": "intra",  # CGST + SGST
        "hsn_sac": "SAC 998211",
        "line_items": [
            ("Accounts payable processing – Mar 2026", 1, 120000),
            ("General ledger & reconciliation services", 1, 55000),
            ("MIS reporting & analytics", 1, 35000),
        ],
        "shipping": 800,
    },
]


def rupee(amount):
    return f"\u20b9{amount:,.2f}"


def build_invoice(inv):
    filename = os.path.join(OUTPUT_DIR, f"invoice_{inv['inv_num']}.pdf")
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    normal.fontSize = 9
    normal.leading = 13

    title_style = ParagraphStyle("title", fontSize=20, fontName="Helvetica-Bold",
                                  textColor=colors.HexColor("#1a3c6e"), spaceAfter=2)
    subtitle_style = ParagraphStyle("subtitle", fontSize=9, fontName="Helvetica",
                                     textColor=colors.grey)
    bold9 = ParagraphStyle("bold9", fontSize=9, fontName="Helvetica-Bold")
    right9 = ParagraphStyle("right9", fontSize=9, alignment=TA_RIGHT)
    rightbold = ParagraphStyle("rightbold", fontSize=10, fontName="Helvetica-Bold",
                                alignment=TA_RIGHT)
    center_gray = ParagraphStyle("cg", fontSize=8, alignment=TA_CENTER,
                                  textColor=colors.grey)
    small_gray = ParagraphStyle("sg", fontSize=7, textColor=colors.grey)

    vendor = inv["vendor"]
    story = []

    # ── HEADER ──────────────────────────────────────────────────────────────
    header_data = [
        [
            Paragraph(vendor["name"], title_style),
            Paragraph("TAX INVOICE", ParagraphStyle("ti", fontSize=22,
                      fontName="Helvetica-Bold", alignment=TA_RIGHT,
                      textColor=colors.HexColor("#1a3c6e"))),
        ],
        [
            Paragraph(vendor["address"].replace("\n", "<br/>") +
                      f"<br/>GSTIN: {vendor['gstin']}<br/>Email: {vendor['email']}",
                      subtitle_style),
            Paragraph(
                f"<b>Invoice No:</b> {inv['inv_num']}<br/>"
                f"<b>Invoice Date:</b> {inv['date']}<br/>"
                f"<b>Due Date:</b> {inv['due_date']}<br/>"
                f"<b>Payment Terms:</b> {inv['payment_terms']}",
                ParagraphStyle("invmeta", fontSize=9, alignment=TA_RIGHT, leading=14),
            ),
        ],
    ]
    header_table = Table(header_data, colWidths=[95 * mm, 85 * mm])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a3c6e"),
                             spaceAfter=8))

    # ── BILL TO ──────────────────────────────────────────────────────────────
    bill_data = [
        [
            Paragraph("<b>Bill To:</b>", bold9),
        ],
        [
            Paragraph(
                f"<b>{BUYER['name']}</b><br/>"
                f"{BUYER['address'].replace(chr(10), '<br/>')}<br/>"
                f"GSTIN: {BUYER['gstin']}<br/>"
                f"Email: {BUYER['email']}",
                ParagraphStyle("buyer", fontSize=9, leading=14),
            ),
        ],
    ]
    bill_table = Table(bill_data, colWidths=[180 * mm])
    bill_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2f8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1a3c6e")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#1a3c6e")),
    ]))
    story.append(bill_table)
    story.append(Spacer(1, 10))

    # ── LINE ITEMS TABLE ─────────────────────────────────────────────────────
    item_header = ["#", "Description", "Qty", "Unit Price (₹)", "Total (₹)"]
    item_rows = [item_header]
    subtotal = 0
    for i, (desc, qty, unit) in enumerate(inv["line_items"], 1):
        total = qty * unit
        subtotal += total
        item_rows.append([
            str(i),
            desc,
            str(qty),
            rupee(unit),
            rupee(total),
        ])

    items_table = Table(
        item_rows,
        colWidths=[8 * mm, 100 * mm, 15 * mm, 28 * mm, 29 * mm],
    )
    items_table.setStyle(TableStyle([
        # Header row
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3c6e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        # Data rows
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f7fb")]),
        ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 1), (0, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cccccc")),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 8))

    # ── SUMMARY TABLE ────────────────────────────────────────────────────────
    shipping = inv["shipping"]
    gst_rate = inv["gst_rate"]
    gst_base = subtotal + shipping
    gst_amount = round(gst_base * gst_rate / 100, 2)
    grand_total = subtotal + shipping + gst_amount

    summary_rows = [
        ["Subtotal", rupee(subtotal)],
        ["Shipping & Handling", rupee(shipping)],
    ]

    if inv["gst_type"] == "intra":
        half = round(gst_amount / 2, 2)
        summary_rows.append([f"CGST @ {gst_rate // 2}%", rupee(half)])
        summary_rows.append([f"SGST @ {gst_rate // 2}%", rupee(half)])
    else:
        summary_rows.append([f"IGST @ {gst_rate}%", rupee(gst_amount)])

    summary_rows.append(["Grand Total", rupee(grand_total)])

    summary_table = Table(
        summary_rows,
        colWidths=[130 * mm, 50 * mm],
    )
    summary_style = TableStyle([
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("LINEABOVE", (0, -1), (-1, -1), 1.5, colors.HexColor("#1a3c6e")),
        ("LINEBELOW", (0, -1), (-1, -1), 1.5, colors.HexColor("#1a3c6e")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, -1), (-1, -1), 10),
        ("TEXTCOLOR", (0, -1), (-1, -1), colors.HexColor("#1a3c6e")),
    ])
    summary_table.setStyle(summary_style)
    story.append(summary_table)
    story.append(Spacer(1, 12))

    # ── PO REFERENCE + BANK DETAILS ─────────────────────────────────────────
    details_data = [
        [
            Paragraph(
                f"<b>PO Reference:</b> {inv['po_ref']}<br/><br/>"
                f"<b>Bank Details:</b><br/>"
                f"Account No: {vendor['bank_account']}<br/>"
                f"IFSC Code: {vendor['ifsc']}<br/>"
                f"Bank: As per vendor master",
                ParagraphStyle("bank", fontSize=9, leading=14),
            ),
            Paragraph(
                f"<b>HSN / SAC Code:</b> {inv['hsn_sac']}<br/>"
                f"<b>Place of Supply:</b> {vendor['state']}<br/>"
                f"<b>GST Type:</b> {'Intra-state (CGST + SGST)' if inv['gst_type'] == 'intra' else 'Inter-state (IGST)'}",
                ParagraphStyle("tax_info", fontSize=9, leading=14),
            ),
        ]
    ]
    details_table = Table(details_data, colWidths=[95 * mm, 85 * mm])
    details_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOX", (0, 0), (0, 0), 0.5, colors.HexColor("#cccccc")),
        ("BOX", (1, 0), (1, 0), 0.5, colors.HexColor("#cccccc")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f5f7fb")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 20))

    # ── FOOTER ───────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey, spaceAfter=6))
    story.append(Paragraph("This is a computer generated invoice.", center_gray))
    story.append(Paragraph(
        f"Subject to {vendor['state']} jurisdiction. E. &amp; O.E.",
        center_gray,
    ))

    doc.build(story)
    return grand_total, filename


if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"  Generating Indian AP Invoices -> {OUTPUT_DIR}/")
    print(f"{'='*60}")
    for inv in INVOICES:
        grand_total, filepath = build_invoice(inv)
        print(f"  [{inv['inv_num']}]  {inv['vendor']['name'][:35]:<35}  Grand Total: INR {grand_total:,.2f}")
        print(f"           Saved: {filepath}")
    print(f"{'='*60}")
    print(f"  Done. {len(INVOICES)} invoices generated.\n")
