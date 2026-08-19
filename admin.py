import os

import pandas as pd
import requests
import streamlit as st


# ============================================================
# FASTAPI BACKEND
# ============================================================

API_BASE_URL = "https://ai-road-infrastructure.onrender.com"

REPORTS_API_URL = f"{API_BASE_URL}/reports"

HEALTH_API_URL = f"{API_BASE_URL}/health"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Road Infrastructure Admin",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title(
    "Road Infrastructure Admin Dashboard"
)

st.write(
    "Monitor and manage reported road damage."
)


# ============================================================
# BACKEND HEALTH CHECK
# ============================================================

try:

    health_response = requests.get(
        HEALTH_API_URL,
        timeout=5
    )

    backend_online = (
        health_response.status_code == 200
    )

except requests.exceptions.RequestException:

    backend_online = False


if not backend_online:

    st.error(
        "FastAPI backend is offline."
    )

    st.code(
        "uvicorn backend.main:app --reload"
    )

    st.stop()


st.success(
    "Backend: Online"
)


# ============================================================
# LOAD REPORTS FROM FASTAPI
# ============================================================

try:

    response = requests.get(
        REPORTS_API_URL,
        timeout=10
    )

except requests.exceptions.ConnectionError:

    st.error(
        "Could not connect to FastAPI."
    )

    st.stop()


except requests.exceptions.Timeout:

    st.error(
        "FastAPI request timed out."
    )

    st.stop()


except requests.exceptions.RequestException as error:

    st.error(
        f"Backend request failed: {error}"
    )

    st.stop()


# ============================================================
# CHECK RESPONSE
# ============================================================

if response.status_code != 200:

    st.error(
        "FastAPI failed to load reports."
    )

    st.code(
        response.text
    )

    st.stop()


# ============================================================
# READ RESPONSE
# ============================================================

try:

    response_data = response.json()

except ValueError:

    st.error(
        "FastAPI returned an invalid response."
    )

    st.stop()


reports = response_data.get(
    "reports",
    []
)


# ============================================================
# NO REPORTS
# ============================================================

if not reports:

    st.info(
        "No road reports available yet."
    )

    st.stop()


# ============================================================
# DATAFRAME
# ============================================================

df = pd.DataFrame(
    reports
)


# ============================================================
# RENAME DATABASE COLUMNS
# ============================================================

df = df.rename(
    columns={
        "report_id": "Report ID",
        "issue": "Issue",
        "confidence": "Confidence",
        "severity": "Severity",
        "priority": "Priority",
        "location": "Location",
        "road_area": "Road Area",
        "description": "Description",
        "reported_date": "Date",
        "reported_time": "Time",
        "status": "Status",
        "image_path": "Image Path",
        "pdf_path": "PDF Path"
    }
)


# ============================================================
# METRICS
# ============================================================

total_reports = len(df)


high_priority = len(
    df[
        df["Priority"] == "High"
    ]
)


medium_priority = len(
    df[
        df["Priority"] == "Medium"
    ]
)


resolved = len(
    df[
        df["Status"] == "Resolved"
    ]
)


col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "Total Reports",
    total_reports
)


col2.metric(
    "High Priority",
    high_priority
)


col3.metric(
    "Medium Priority",
    medium_priority
)


col4.metric(
    "Resolved",
    resolved
)


st.divider()


# ============================================================
# FILTERS
# ============================================================

st.subheader(
    "Filter Reports"
)


col1, col2, col3 = st.columns(3)


with col1:

    priority_filter = st.selectbox(
        "Priority",
        [
            "All",
            "High",
            "Medium",
            "None"
        ]
    )


with col2:

    issue_filter = st.selectbox(
        "Issue",
        [
            "All",
            "Large pothole",
            "Small pothole",
            "Normal"
        ]
    )


with col3:

    status_filter = st.selectbox(
        "Status",
        [
            "All",
            "Reported",
            "In Progress",
            "Resolved"
        ]
    )


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df.copy()


if priority_filter != "All":

    filtered_df = filtered_df[
        filtered_df["Priority"]
        == priority_filter
    ]


if issue_filter != "All":

    filtered_df = filtered_df[
        filtered_df["Issue"]
        == issue_filter
    ]


if status_filter != "All":

    filtered_df = filtered_df[
        filtered_df["Status"]
        == status_filter
    ]


# ============================================================
# REPORT TABLE
# ============================================================

st.subheader(
    "Road Issue Reports"
)


display_columns = [
    "Report ID",
    "Issue",
    "Confidence",
    "Severity",
    "Priority",
    "Location",
    "Road Area",
    "Date",
    "Time",
    "Status"
]


st.dataframe(
    filtered_df[display_columns],
    use_container_width=True,
    hide_index=True
)


# ============================================================
# REPORT DETAILS
# ============================================================

st.divider()

st.subheader(
    "Report Details"
)


selected_report = st.selectbox(
    "Select Report",
    df["Report ID"].tolist()
)


selected_row = df[
    df["Report ID"] == selected_report
].iloc[0]


col1, col2 = st.columns(2)


with col1:

    st.write(
        f"**Issue:** {selected_row['Issue']}"
    )

    st.write(
        f"**Confidence:** "
        f"{float(selected_row['Confidence']):.2f}%"
    )

    st.write(
        f"**Severity:** "
        f"{selected_row['Severity']}"
    )

    st.write(
        f"**Priority:** "
        f"{selected_row['Priority']}"
    )

    st.write(
        f"**Status:** "
        f"{selected_row['Status']}"
    )


with col2:

    st.write(
        f"**Location:** "
        f"{selected_row['Location']}"
    )

    st.write(
        f"**Road:** "
        f"{selected_row['Road Area']}"
    )

    st.write(
        f"**Date:** "
        f"{selected_row['Date']}"
    )

    st.write(
        f"**Time:** "
        f"{selected_row['Time']}"
    )

    st.write(
        f"**Description:** "
        f"{selected_row['Description']}"
    )


# ============================================================
# ROAD IMAGE
# ============================================================

st.subheader(
    "Road Image"
)

image_url = (
    f"{API_BASE_URL}/reports/"
    f"{selected_report}/image"
)

try:

    image_response = requests.get(
        image_url,
        timeout=30
    )

    if image_response.status_code == 200:

        st.image(
            image_response.content,
            caption="Reported Road Image",
            width=600
        )

    else:

        st.warning(
            "Road image not found on the backend."
        )

except requests.exceptions.RequestException as error:

    st.error(
        f"Could not load road image: {error}"
    )


# ============================================================
# DOWNLOAD PDF REPORT
# ============================================================

st.subheader(
    "Road Damage Report"
)


pdf_url = (
    f"{REPORTS_API_URL}/"
    f"{selected_report}/pdf"
)


try:

    pdf_response = requests.get(
        pdf_url,
        timeout=30
    )


    if pdf_response.status_code == 200:

        st.download_button(

            label="Download PDF Report",

            data=pdf_response.content,

            file_name=(
                f"{selected_report}_road_report.pdf"
            ),

            mime="application/pdf",

            use_container_width=True
        )


    elif pdf_response.status_code == 404:

        st.warning(
            "PDF report is not available for this report."
        )


    else:

        st.warning(
            "Unable to retrieve the PDF report."
        )


except requests.exceptions.RequestException as error:

    st.warning(
        f"Could not connect to PDF service: {error}"
    )


# ============================================================
# UPDATE STATUS
# ============================================================

st.divider()

st.subheader(
    "Update Report Status"
)


new_status = st.selectbox(
    "New Status",
    [
        "Reported",
        "In Progress",
        "Resolved"
    ],
    key="status_selector"
)


if st.button(
    "Update Status",
    use_container_width=True
):

    try:

        status_response = requests.put(

            f"{REPORTS_API_URL}/"
            f"{selected_report}/status",

            params={
                "status": new_status
            },

            timeout=10
        )


    except requests.exceptions.RequestException as error:

        st.error(
            f"Could not update status: {error}"
        )

        st.stop()


    if status_response.status_code == 200:

        st.success(
            f"{selected_report} updated to "
            f"{new_status}"
        )

        st.rerun()


    else:

        st.error(
            "FastAPI failed to update the report."
        )

        st.code(
            status_response.text
        )