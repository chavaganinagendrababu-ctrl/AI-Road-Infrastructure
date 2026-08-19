import requests
import streamlit as st
from PIL import Image


# ============================================================
# FASTAPI BACKEND
# ============================================================

API_BASE_URL = "https://ai-road-infrastructure.onrender.com"

REPORT_API_URL = f"{API_BASE_URL}/reports"

HEALTH_API_URL = f"{API_BASE_URL}/health"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Road Infrastructure",
    page_icon="🛣️",
    layout="centered"
)


# ============================================================
# SESSION STATE
# ============================================================

if "clear_upload" not in st.session_state:
    st.session_state.clear_upload = 0


# ============================================================
# HEADER
# ============================================================

st.title(
    "AI Road Infrastructure"
)

st.subheader(
    "Road Damage Detection & Reporting"
)

st.write(
    "Upload a road image to detect road damage "
    "and create a road issue report."
)


# ============================================================
# BACKEND STATUS
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


if backend_online:

    st.success(
        "Backend: Online"
    )

else:

    st.error(
        "Backend: Offline"
    )

    st.info(
        "Start FastAPI using:"
    )

    st.code(
        "uvicorn backend.main:app --reload"
    )


# ============================================================
# ROAD DETAILS
# ============================================================

st.subheader(
    "Road Details"
)


location = st.text_input(
    "Location",
    placeholder="Example: Hyderabad, Telangana"
)


road_area = st.text_input(
    "Road / Area",
    placeholder="Example: KPHB Main Road"
)


description = st.text_area(
    "Issue Description",
    placeholder="Describe the road condition..."
)


# ============================================================
# IMAGE UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "Upload a road image",

    type=[
        "jpg",
        "jpeg",
        "png"
    ],

    key=f"uploader_{st.session_state.clear_upload}"
)


# ============================================================
# IMAGE DISPLAY
# ============================================================

if uploaded_file is not None:

    image = Image.open(
        uploaded_file
    ).convert("RGB")


    st.image(
        image,
        caption="Uploaded Road Image",
        width=500
    )


    st.divider()


    # ========================================================
    # BUTTONS
    # ========================================================

    col1, col2 = st.columns(2)


    with col1:

        analyze = st.button(
            "Analyze Road",
            use_container_width=True
        )


    with col2:

        clear = st.button(
            "Clear",
            use_container_width=True
        )


    # ========================================================
    # CLEAR BUTTON
    # ========================================================

    if clear:

        st.session_state.clear_upload += 1

        st.rerun()


    # ========================================================
    # ANALYZE BUTTON
    # ========================================================

    if analyze:


        # ----------------------------------------------------
        # BACKEND CHECK
        # ----------------------------------------------------

        if not backend_online:

            st.error(
                "FastAPI backend is offline."
            )

            st.stop()


        # ----------------------------------------------------
        # VALIDATE LOCATION
        # ----------------------------------------------------

        if not location:

            st.warning(
                "Please enter the location."
            )

            st.stop()


        # ----------------------------------------------------
        # VALIDATE ROAD AREA
        # ----------------------------------------------------

        if not road_area:

            st.warning(
                "Please enter the road / area."
            )

            st.stop()


        # ----------------------------------------------------
        # SEND REQUEST TO FASTAPI
        # ----------------------------------------------------

        with st.spinner(
            "Analyzing road image..."
        ):

            try:

                response = requests.post(

                    REPORT_API_URL,

                    files={
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type
                        )
                    },

                    data={
                        "location": location,
                        "road_area": road_area,
                        "description": description
                    },

                    timeout=120
                )


            except requests.exceptions.ConnectionError:

                st.error(
                    "Could not connect to FastAPI."
                )

                st.code(
                    "uvicorn backend.main:app --reload"
                )

                st.stop()


            except requests.exceptions.Timeout:

                st.error(
                    "FastAPI took too long to respond."
                )

                st.stop()


            except requests.exceptions.RequestException as error:

                st.error(
                    f"Backend request failed: {error}"
                )

                st.stop()


        # ----------------------------------------------------
        # CHECK HTTP STATUS
        # ----------------------------------------------------

        if response.status_code != 200:

            st.error(
                "FastAPI failed to create the report."
            )

            st.code(
                response.text
            )

            st.stop()


        # ----------------------------------------------------
        # READ JSON RESPONSE
        # ----------------------------------------------------

        try:

            result = response.json()

        except ValueError:

            st.error(
                "FastAPI returned an invalid response."
            )

            st.stop()


        # ----------------------------------------------------
        # EXTRACT RESULT
        # ----------------------------------------------------

        try:

            report_id = result[
                "report_id"
            ]

            predicted_class = result[
                "prediction"
            ]

            confidence = float(
                result["confidence"]
            )

            severity = result[
                "severity"
            ]

            priority = result[
                "priority"
            ]

            reported_date = result[
                "reported_date"
            ]

            reported_time = result[
                "reported_time"
            ]

            status = result[
                "status"
            ]

        except KeyError as error:

            st.error(
                f"Missing field from FastAPI response: {error}"
            )

            st.json(result)

            st.stop()


        # ====================================================
        # AI DETECTION RESULT
        # ====================================================

        st.subheader(
            "AI Detection Result"
        )


        st.success(
            f"Prediction: {predicted_class}"
        )


        st.metric(
            "Confidence",
            f"{confidence:.2f}%"
        )


        st.info(
            f"Severity: {severity}"
        )


        # ====================================================
        # PRIORITY
        # ====================================================

        if priority == "High":

            st.error(
                f"Priority: {priority}"
            )

        elif priority == "Medium":

            st.warning(
                f"Priority: {priority}"
            )

        else:

            st.success(
                f"Priority: {priority}"
            )


        # ====================================================
        # ROAD ISSUE REPORT
        # ====================================================

        st.subheader(
            "Road Issue Report"
        )


        st.write(
            f"Report ID: {report_id}"
        )


        st.write(
            f"Location: {location}"
        )


        st.write(
            f"Road / Area: {road_area}"
        )


        st.write(
            f"Issue: {predicted_class}"
        )


        st.write(
            f"Severity: {severity}"
        )


        st.write(
            f"Priority: {priority}"
        )


        st.write(
            f"AI Confidence: {confidence:.2f}%"
        )


        st.write(
            f"Description: "
            f"{description if description else 'Not provided'}"
        )


        st.write(
            f"Reported: "
            f"{reported_date} {reported_time}"
        )


        st.info(
            f"Status: {status}"
        )


        # ====================================================
        # SUCCESS MESSAGE
        # ====================================================

        st.success(
            "Road issue reported successfully."
        )


        # ====================================================
        # DOWNLOAD PDF REPORT
        # ====================================================

        st.subheader(
            "Road Damage Report"
        )


        pdf_url = (
            f"{REPORT_API_URL}/"
            f"{report_id}/pdf"
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
                        f"{report_id}_road_report.pdf"
                    ),

                    mime="application/pdf",

                    use_container_width=True
                )


            else:

                st.warning(
                    "PDF report is not available."
                )


        except requests.exceptions.RequestException:

            st.warning(
                "Could not connect to the PDF service."
            )