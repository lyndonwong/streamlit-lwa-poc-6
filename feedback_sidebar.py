import streamlit as st
import requests
import datetime


def feedback_sidebar(city_name: str):
    """Reusable sidebar for collecting feedback from different city apps."""

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### 💬 Feedback")
    st.sidebar.write(
        f"Help improve this {city_name.title()} recap! Report bugs, "
        "suggest improvements, or sign up for future updates."
    )

    feedback_type = st.sidebar.selectbox(
        "Type of feedback:",
        ["Bug or data issue", "Feature suggestion", "Other comment"],
    )

    feedback_text = st.sidebar.text_area(
        "Describe your feedback:",
        placeholder="Example: The project map didn’t load correctly...",
    )

    rating = st.sidebar.radio(
        "How useful is this app so far?",
        ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"],
        horizontal=True,
    )

    contact_email = st.sidebar.text_input(
        "Your email (optional)",
        placeholder="you@example.com",
    )
# CTA to join mailing list
    st.sidebar.markdown(
        f"📬 Want updates? Include your email above."
    )

    # Load secrets securely
    try:
        gas_url = st.secrets["feedback"]["gas_url"]
        secret_token = st.secrets["feedback"]["token"]
    except Exception:
        st.sidebar.error("⚠️ Missing Google Apps Script credentials. Check secrets.toml or Streamlit Cloud settings.")
        return

    if st.sidebar.button("📨 Submit Feedback"):
        if not feedback_text.strip():
            st.sidebar.warning("Please enter some feedback before submitting.")
        else:
            payload = {
                "city_name": city_name,      # 👈 added city name field
                "feedback_type": feedback_type,
                "feedback_text": feedback_text,
                "rating": rating,
                "contact_email": contact_email,
                "token": secret_token,
            }

            try:
                response = requests.post(gas_url, json=payload, timeout=5)
                if response.status_code == 200 and "success" in response.text:
                    st.sidebar.success("✅ Feedback sent successfully! Thank you.")
                else:
                    st.sidebar.error("⚠️ Could not send feedback. Try again later.")
                    st.sidebar.caption(f"Response: {response.text}")
            except Exception as e:
                st.sidebar.error(f"Network error: {e}")

    # Optional footer
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "Prefer a form? [Submit feedback via Google Form](https://link.lyndonwong.com/mp-council-dashboard-feedback)"
    )



