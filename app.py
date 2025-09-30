import streamlit as st
import requests
import uuid
import base64
from dotenv import load_dotenv 

load_dotenv()

API_BASE = os.getenv('BACKEND_URI')  # adjust if your FastAPI runs elsewhere

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
        st.session_state.interview_started = True
    except Exception as e:
        st.error(f"Failed to start interview: {e}")
        st.session_state.current_q = None

def create_download_link(pdf_bytes, filename):
    """Create a download link for PDF file"""
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">Download Detailed PDF Report</a>'
    return href

# Initialize session state with default values
if "current_step" not in st.session_state:
    st.session_state.current_step = "welcome"
if "user_details" not in st.session_state:
    st.session_state.user_details = {}
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "current_q" not in st.session_state:
    st.session_state.current_q = None
if "chat" not in st.session_state:
    st.session_state.chat = []
if "feedback" not in st.session_state:
    st.session_state.feedback = None

# # Debug: Show current state (you can remove this later)
# st.sidebar.write("Debug - Current Step:", st.session_state.current_step)

# Step 1: Welcome Message
if st.session_state.current_step == "welcome":
    st.title("🎯 Excel Skills Assessment Platform")
    
    # Platform Introduction
    st.markdown("""
    ## Welcome to AI-Powered Excel Mock Interviewer
    
    **Transform your Excel skills with our intelligent assessment platform!**
    
    This platform is designed to evaluate and enhance your Microsoft Excel proficiency through 
    AI-powered interviews. Our system assesses your knowledge across various Excel concepts 
    and provides detailed feedback to help you improve.
    
    ### What to Expect:
    - 📝 **5 carefully selected Excel questions** across different difficulty levels
    - 🤖 **AI-powered evaluation** with detailed scoring
    - 📊 **Comprehensive feedback report** with strengths and areas for improvement
    - 📄 **Professional PDF report** for your records
    - 🎯 **Personalized recommendations** for skill development
    """)
    
    if st.button("🚀 Continue to Assessment", type="primary", key="continue_btn"):
        st.session_state.current_step = "details"
        st.rerun()

# Step 2: User Details Form
elif st.session_state.current_step == "details":
    st.title("📋 Candidate Details")
    
    st.markdown("Please provide your details to begin the assessment:")
    
    with st.form("user_details_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name*", placeholder="Enter your full name", key="name_input")
        with col2:
            email = st.text_input("Email Address*", placeholder="Enter your email address", key="email_input")
        
        company = st.text_input("Company/Organization", placeholder="Optional", key="company_input")
        position = st.text_input("Current Position", placeholder="Optional", key="position_input")
        
        submitted = st.form_submit_button("Continue to Instructions")
        
        if submitted:
            if not name.strip() or not email.strip():
                st.error("Please fill in all required fields (Name and Email)")
            else:
                st.session_state.user_details = {
                    "name": name.strip(),
                    "email": email.strip(),
                    "company": company.strip(),
                    "position": position.strip()
                }
                st.session_state.current_step = "instructions"
                st.rerun()

# Step 3: Instructions Section
elif st.session_state.current_step == "instructions":
    st.title("📋 Interview Instructions")
    
    st.markdown(f"""
    ### Hello, {st.session_state.user_details['name']}!
    
    Before we begin the assessment, please review these important instructions:
    """)
    
    st.info("""
    **🎯 Assessment Guidelines:**
    
    1. **Question Format**: You will receive 5 Excel-related questions of varying difficulty levels
    2. **Answer Length**: Provide comprehensive but concise answers
    3. **Technical Terms**: Use appropriate Excel terminology when possible
    4. **Time Consideration**: Take your time to think before answering
    5. **No External Help**: Please complete the assessment without external assistance
    6. **Navigation**: Use the submit button to move to the next question
    
    **📝 Answering Tips:**
    - Be specific and detailed in your responses
    - Include examples where relevant
    - Mention practical applications of concepts
    - If unsure, explain your thought process
    
    **⚡ Technical Requirements:**
    - Stable internet connection
    - Modern web browser
    - No Excel installation required
    
    **⏱️ Duration**: Approximately 10-15 minutes
    """)
    
    st.warning("""
    **Important**: Once you start the interview, please complete it in one sitting. 
    Your progress cannot be saved and resumed later.
    """)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ Back to Details"):
            st.session_state.current_step = "details"
            st.rerun()
    with col2:
        if st.button("✅ I Understand & Start Interview", type="primary"):
            st.session_state.current_step = "interview"
            start_interview()
            st.rerun()

# Step 4: Main Interview Section
elif st.session_state.current_step == "interview" and st.session_state.current_q:
    st.title("💼 Excel Skills Assessment - In Progress")
    
    # Progress bar
    total_questions = 5
    current_progress = len(st.session_state.chat) / total_questions
    st.progress(current_progress)
    st.caption(f"Progress: {len(st.session_state.chat)}/{total_questions} questions completed")
    
    st.subheader("Current Question")

    # Dynamic widget key ensures input resets every new question
    widget_key = f"answer_input_{len(st.session_state.chat)}"

    with st.form(key="answer_form"):
        st.markdown(f"**Question {len(st.session_state.chat) + 1}:** {st.session_state.current_q}")
        answer = st.text_area(
            "Your Answer",
            key=widget_key,
            placeholder="Type your detailed answer here...",
            height=120
        )
        submitted = st.form_submit_button("📤 Submit Answer")

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
                st.session_state.current_step = "results"
                st.session_state.current_q = None

            st.rerun()

# Step 5: Results Section
elif st.session_state.current_step == "results":
    st.info("🎉 Interview complete! See your detailed feedback below.")
    
    # Show chat history
    if st.session_state.chat:
        st.write("### 📝 Your Answers")
        for i, item in enumerate(st.session_state.chat, 1):
            st.markdown(f"**Q{i}:** {item['q']}")
            st.markdown(f"**Your Answer:** {item['a']}")
            st.markdown("---")

    # Show final feedback when available
    if st.session_state.feedback:
        feedback_data = st.session_state.feedback
        user_details = st.session_state.user_details
        
        st.write("## 📊 Assessment Report")
        
        # Candidate Information
        st.subheader("👤 Candidate Information")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Name:** {user_details.get('name', 'N/A')}")
            st.write(f"**Email:** {user_details.get('email', 'N/A')}")
        with col2:
            st.write(f"**Company:** {user_details.get('company', 'N/A')}")
            st.write(f"**Position:** {user_details.get('position', 'N/A')}")
        
        st.markdown("---")
        
        # Performance summary in columns
        st.subheader("📈 Performance Summary")
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
        st.subheader("🔍 Performance Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("**✅ Strengths**")
            st.write(feedback_data['strengths'])
        
        with col2:
            st.error("**📝 Areas for Improvement**")
            st.write(feedback_data['weaknesses'])
        
        # Recommendations
        st.subheader("🎯 Recommendations")
        st.info(feedback_data['recommendation'])
        
        # Download PDF Report
        st.markdown("---")
        st.subheader("📄 Detailed Report")
        st.write("Download a comprehensive PDF report with detailed analysis of each question and your performance:")
        
        if st.button("📥 Generate Detailed PDF Report", type="primary"):
            with st.spinner("Generating professional PDF report..."):
                try:
                    # Include user details in the request
                    response = requests.get(
                        f"{API_BASE}/download_report",
                        params={
                            "session_id": st.session_state.session_id,
                            "user_name": user_details.get('name', ''),
                            "user_email": user_details.get('email', ''),
                            "user_company": user_details.get('company', ''),
                            "user_position": user_details.get('position', '')
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        # Save PDF temporarily and provide download
                        pdf_bytes = response.content
                        
                        # Create download link
                        filename = f"Excel_Assessment_Report_{user_details.get('name', 'Candidate').replace(' ', '_')}_{st.session_state.session_id[:8]}.pdf"
                        
                        st.markdown(
                            create_download_link(pdf_bytes, filename), 
                            unsafe_allow_html=True
                        )
                        
                        st.success("✅ PDF report generated successfully! Click the link above to download.")
                    else:
                        st.error("❌ Failed to generate PDF report. Please try again.")
                        
                except Exception as e:
                    st.error(f"❌ Error generating report: {e}")
    
    # Navigation options
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔄 Start New Interview"):
            # Reset to welcome but keep user details
            user_details_backup = st.session_state.user_details.copy()
            for key in list(st.session_state.keys()):
                if key not in ['current_step', 'user_details']:
                    del st.session_state[key]
            st.session_state.current_step = "welcome"
            st.session_state.user_details = user_details_backup
            st.rerun()
    with col2:
        if st.button("🏠 Return to Home"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# Handle edge case - if somehow we're in interview state but no current question
elif st.session_state.current_step == "interview" and not st.session_state.current_q:
    st.session_state.current_step = "results"
    st.rerun()
