import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)


def generate_report_pdf(
    report_id,
    issue,
    confidence,
    severity,
    priority,
    location,
    road_area,
    description,
    reported_date,
    reported_time,
    status,
    image_path
):

    # ========================================================
    # PDF DIRECTORY
    # ========================================================

    report_directory = os.path.dirname(
        image_path
    )

    pdf_path = os.path.join(
        report_directory,
        "road_damage_report.pdf"
    )


    # ========================================================
    # PDF DOCUMENT
    # ========================================================

    document = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )


    # ========================================================
    # STYLES
    # ========================================================

    styles = getSampleStyleSheet()


    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        spaceAfter=10
    )


    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=11,
        spaceAfter=20
    )


    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=10,
        spaceAfter=8
    )


    normal_style = ParagraphStyle(
        "NormalStyle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14
    )


    # ========================================================
    # CONTENT
    # ========================================================

    story = []


    # ========================================================
    # TITLE
    # ========================================================

    story.append(
        Paragraph(
            "AI ROAD INFRASTRUCTURE",
            title_style
        )
    )


    story.append(
        Paragraph(
            "Road Damage Detection Report",
            subtitle_style
        )
    )


    # ========================================================
    # REPORT INFORMATION
    # ========================================================

    story.append(
        Paragraph(
            "Report Information",
            heading_style
        )
    )


    report_data = [

        ["Report ID", report_id],

        ["Reported Date", reported_date],

        ["Reported Time", reported_time],

        ["Status", status],

    ]


    report_table = Table(
        report_data,
        colWidths=[
            1.6 * inch,
            4.8 * inch
        ]
    )


    report_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.lightgrey
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),

            (
                "FONTNAME",
                (1, 0),
                (1, -1),
                "Helvetica"
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                10
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                8
            )

        ])
    )


    story.append(
        report_table
    )


    story.append(
        Spacer(
            1,
            15
        )
    )


    # ========================================================
    # ROAD IMAGE
    # ========================================================

    story.append(
        Paragraph(
            "Road Image",
            heading_style
        )
    )


    if (
        image_path
        and os.path.exists(image_path)
    ):

        road_image = Image(
            image_path
        )

        road_image._restrictSize(
            5.8 * inch,
            4.2 * inch
        )

        story.append(
            road_image
        )

    else:

        story.append(
            Paragraph(
                "Road image not available.",
                normal_style
            )
        )


    story.append(
        Spacer(
            1,
            15
        )
    )


    # ========================================================
    # AI DETECTION
    # ========================================================

    story.append(
        Paragraph(
            "AI Detection Result",
            heading_style
        )
    )


    detection_data = [

        ["Detected Issue", issue],

        [
            "AI Confidence",
            f"{float(confidence):.2f}%"
        ],

        ["Severity", severity],

        ["Priority", priority],

    ]


    detection_table = Table(
        detection_data,
        colWidths=[
            1.8 * inch,
            4.6 * inch
        ]
    )


    detection_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.lightgrey
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                10
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            )

        ])
    )


    story.append(
        detection_table
    )


    story.append(
        Spacer(
            1,
            15
        )
    )


    # ========================================================
    # LOCATION
    # ========================================================

    story.append(
        Paragraph(
            "Road Details",
            heading_style
        )
    )


    location_data = [

        ["Location", location],

        ["Road / Area", road_area],

    ]


    location_table = Table(
        location_data,
        colWidths=[
            1.8 * inch,
            4.6 * inch
        ]
    )


    location_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.lightgrey
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                10
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            )

        ])
    )


    story.append(
        location_table
    )


    story.append(
        Spacer(
            1,
            15
        )
    )


    # ========================================================
    # DESCRIPTION
    # ========================================================

    story.append(
        Paragraph(
            "Issue Description",
            heading_style
        )
    )


    description_text = (
        description
        if description
        else "Not provided"
    )


    story.append(
        Paragraph(
            description_text,
            normal_style
        )
    )


    story.append(
        Spacer(
            1,
            20
        )
    )


    # ========================================================
    # FOOTER NOTE
    # ========================================================

    story.append(
        Paragraph(
            "This report was generated by the "
            "AI Road Infrastructure system.",
            normal_style
        )
    )


    # ========================================================
    # GENERATE PDF
    # ========================================================

    document.build(
        story
    )


    return pdf_path