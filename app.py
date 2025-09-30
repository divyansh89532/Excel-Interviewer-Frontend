import streamlit as st
import requests
import uuid
import base64

API_BASE = "http://localhost:8000"  # adjust if your FastAPI runs elsewhere

st.set_page_config(page_title="Excel Mock Interview", layout="centered")

def start_interview():
    """Initialize a new interview session."""
    sid = str(uuid.uuid4())
    st.session_state.session_id = sid
    try:
        res = requests.post(
            f"{API_BASE}/start_interview",
            params={"session_id": sid},
            timeout=10
        ).json()
        st.session_state.current_q = res.get("first_question")
        st.session_state.chat = []
        st.session_state.feedback = None
    except Exception as e:
        st.error(f"Failed to start interview: {e}")
        st.session_state.current_q = None

def create_download_link(pdf_bytes, filename):
    """Create a download link for PDF file"""
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">Download Detailed PDF Report</a>'
    return href

# Initialize session only once
if "session_id" not in st.session_state:
    start_interview()

st.title("AI-Powered Excel Mock Interviewer")

if st.session_state.current_q:
    st.subheader("Interview in Progress")

    # Dynamic widget key ensures input resets every new question
    widget_key = f"answer_input_{len(st.session_state.chat)}"

    with st.form(key="answer_form"):
        st.markdown(f"**Question:** {st.session_state.current_q}")
        answer = st.text_input(
            "Your Answer",
            key=widget_key,
            placeholder="Type your answer here..."
        )
        submitted = st.form_submit_button("Submit")

    if submitted:
        if not answer.strip():
            st.warning("Please type an answer before submitting.")
        else:
            with st.spinner("Evaluating your answer..."):
                try:
                    payload = {
                        "session_id": st.session_state.session_id,
                        "answer": answer
                    }
                    res = requests.post(
                        f"{API_BASE}/next_question",
                        json=payload,
                        timeout=20
                    ).json()
                except Exception as e:
                    st.error(f"Error submitting answer: {e}")
                    res = {}

            # Store answer with the correct question
            st.session_state.chat.append({
                "q": st.session_state.current_q,
                "a": answer
            })

            # Move to next question or finish
            if "next_question" in res:
                st.session_state.current_q = res["next_question"]
            else:
                with st.spinner("Generating final feedback..."):
                    try:
                        st.session_state.feedback = requests.get(
                            f"{API_BASE}/feedback",
                            params={"session_id": st.session_state.session_id},
                            timeout=20
                        ).json()
                    except Exception as e:
                        st.error(f"Error fetching feedback: {e}")
                st.session_state.current_q = None

            # 🔄 Force rerun so new widget key takes effect (resets text input)
            st.rerun()

else:
    st.info("Interview complete. See feedback below or restart a new interview.")
    if st.button("Start New Interview"):
        start_interview()
        st.rerun()

# Show chat history
if st.session_state.get("chat"):
    st.write("### Your Answers")
    for item in st.session_state.chat:
        st.markdown(f"**Q:** {item['q']}")
        st.markdown(f"**A:** {item['a']}")
        st.markdown("---")

# Show final feedback when available
if st.session_state.get("feedback"):
    feedback_data = st.session_state.feedback
    
    st.write("## 📊 Feedback Report")
    
    # Performance summary in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Score", f"{feedback_data['score']}/{feedback_data['total_possible']}")
    
    with col2:
        st.metric("Percentage", f"{feedback_data['percentage']}%")
    
    with col3:
        # Color code performance level
        performance = feedback_data['performance']
        if performance == "Excellent":
            color = "green"
        elif performance == "Good":
            color = "blue"
        elif performance == "Average":
            color = "orange"
        else:
            color = "red"
        st.markdown(f"**Performance Level:** <span style='color:{color}'>{performance}</span>", 
                   unsafe_allow_html=True)
    
    with col4:
        st.metric("Questions", feedback_data['questions_answered'])
    
    # Strengths and weaknesses in columns
    st.subheader("Performance Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("**Strengths**")
        st.write(feedback_data['strengths'])
    
    with col2:
        st.error("**Areas for Improvement**")
        st.write(feedback_data['weaknesses'])
    
    # Recommendations
    st.subheader("Recommendations")
    st.info(feedback_data['recommendation'])
    
    # Download PDF Report
    st.subheader("Detailed Report")
    st.write("Download a comprehensive PDF report with detailed analysis of each question:")
    
    if st.button("📥 Generate Detailed PDF Report"):
        with st.spinner("Generating PDF report..."):
            try:
                response = requests.get(
                    f"{API_BASE}/download_report",
                    params={"session_id": st.session_state.session_id},
                    timeout=30
                )
                
                if response.status_code == 200:
                    # Save PDF temporarily and provide download
                    pdf_bytes = response.content
                    
                    # Create download link
                    st.markdown(
                        create_download_link(
                            pdf_bytes, 
                            f"Excel_Assessment_Report_{st.session_state.session_id[:8]}.pdf"
                        ), 
                        unsafe_allow_html=True
                    )
                    
                    st.success("PDF report generated successfully! Click the link above to download.")
                else:
                    st.error("Failed to generate PDF report")
                    
            except Exception as e:
                st.error(f"Error generating report: {e}")
    
    # Restart interview option
    st.markdown("---")
    if st.button("🔄 Start Another Interview"):
        start_interview()
        st.rerun()