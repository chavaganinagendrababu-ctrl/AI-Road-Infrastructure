import sqlite3


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DATABASE_NAME = "road_reports.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    return sqlite3.connect(
        DATABASE_NAME
    )


# ============================================================
# CREATE DATABASE
# ============================================================

def create_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (

            report_id TEXT PRIMARY KEY,

            issue TEXT NOT NULL,

            confidence REAL,

            severity TEXT,

            priority TEXT,

            location TEXT,

            road_area TEXT,

            description TEXT,

            reported_date TEXT,

            reported_time TEXT,

            status TEXT,

            image_path TEXT,

            pdf_path TEXT

        )
    """)

    connection.commit()

    connection.close()


# ============================================================
# SAVE REPORT
# ============================================================

def save_report(
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
    image_path,
    pdf_path
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO reports (
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
            image_path,
            pdf_path
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
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
        image_path,
        pdf_path
    ))

    connection.commit()

    connection.close()


# ============================================================
# GET ALL REPORTS
# ============================================================

def get_all_reports():

    connection = get_connection()

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
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
            image_path,
            pdf_path
        FROM reports
        ORDER BY rowid DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# GET REPORTS
# ============================================================

def get_reports():

    return get_all_reports()


# ============================================================
# UPDATE REPORT STATUS
# ============================================================

def update_report_status(
    report_id,
    status
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE reports
        SET status = ?
        WHERE report_id = ?
    """, (
        status,
        report_id
    ))

    connection.commit()

    updated_rows = cursor.rowcount

    connection.close()

    return updated_rows > 0