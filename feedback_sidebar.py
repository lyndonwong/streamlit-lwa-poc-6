import streamlit as st
import datetime

def feedback_sidebar():
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💬 We’d love your feedback!")
    st.sidebar.write(
        "Help improve the VisiGov app by reporting bugs, "
        "suggesting improvements, or signing up for future updates."
    )

    # --- Bug & Suggestion Form ---
    st.sidebar.markdown("#### 🪲 Report a Bug or Suggestion")
    feedback_type = st.sidebar.selectbox(
        "What kind of feedback would you like to share?",
        ["Bug or data issue", "Feature suggestion", "Other comment"],
    )

    feedback_text = st.sidebar.text_area(
        "Describe what you noticed or suggest:",
        placeholder="Example: The project map didn’t load correctly...",
    )

    # --- Optional Contact Info ---
    contact = st.sidebar.text_input(
        "Your email (optional)",
        placeholder="you@example.com",
    )

    # --- Submission Logic ---
    if st.sidebar.button("📨 Submit Feedback"):
        if feedback_text.strip() == "":
            st.sidebar.warning("Please add a brief description before submitting.")
        else:
            # Append feedback to a local log file or Google Sheet later
            timestamp = datetime.datetime.now().isoformat()
            with open("user_feedback_log.txt", "a") as f:
                f.write(
                    f"{timestamp}\t{feedback_type}\t{feedback_text}\t{contact}\n"
                )
            st.sidebar.success("✅ Thank you! Your feedback has been recorded.")
            st.sidebar.info(
                "We appreciate your help in improving the app."
            )

    # --- External Form (optional fallback) ---
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "Prefer a form? [Submit feedback via Google Form](https://forms.gle/your-feedback-form)"
    )

    # --- Contact and Follow-Up ---
    st.sidebar.markdown("#### 📬 Stay in Touch")
    st.sidebar.markdown(
        "Want updates about new features? "
        "[Email us](mailto:team@visigov.app) or add your email above."
    )
