import os
import psycopg2
from psycopg2.extras import RealDictCursor


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DATABASE_URL = os.getenv("DATABASE_URL")


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    if not DATABASE_URL:

        raise RuntimeError(
            "DATABASE_URL environment variable is not configured."
        )

    return psycopg2.connect(
        DATABASE_URL
    )


# ============================================================
# CREATE DATABASE TABLE
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

    cursor.close()

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

        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
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

    cursor.close()

    connection.close()


# ============================================================
# GET ALL REPORTS
# ============================================================

def get_all_reports():

    connection = get_connection()

    cursor = connection.cursor(
        cursor_factory=RealDictCursor
    )

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
        ORDER BY reported_date DESC, reported_time DESC
    """)

    rows = cursor.fetchall()

    cursor.close()

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
        SET status = %s
        WHERE report_id = %s
    """, (
        status,
        report_id
    ))

    connection.commit()

    updated_rows = cursor.rowcount

    cursor.close()

    connection.close()

    return updated_rows > 0