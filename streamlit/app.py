"""
CV-RAG Streamlit App
====================
Interactive chat interface for Mike Murphy's AI-powered resume.

Author: Mike Murphy
Project: CV-RAG
"""

import os
import streamlit as st
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Mike Murphy - AI Resume Chat",
    page_icon=">",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
    }
    .sample-question {
        margin: 0.5rem 0;
    }
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: #666;
    }
    </style>
""", unsafe_allow_html=True)


def query_resume(question: str, webhook_url: str) -> dict:
    """
    Send query to n8n webhook and get AI-generated response.

    Args:
        question: User's question
        webhook_url: n8n webhook endpoint

    Returns:
        Response dictionary with 'answer' and optional 'sources'
    """
    try:
        response = requests.post(
            webhook_url,
            json={'chatInput': question},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {
                'answer': f"Error: Received status code {response.status_code}",
                'error': True
            }
    except requests.exceptions.Timeout:
        return {
            'answer': "Request timed out. Please try again.",
            'error': True
        }
    except Exception as e:
        return {
            'answer': f"Error: {str(e)}",
            'error': True
        }


def main():
    """
    Main Streamlit app function.
    """
    # Header
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("> Ask My AI Resume Anything")
    st.markdown("**Chat with Mike Murphy's Experience Using RAG + LLM**")
    st.markdown('</div>', unsafe_allow_html=True)

    # Get webhook URL from environment
    webhook_url = os.getenv("N8N_WEBHOOK_URL")

    if not webhook_url:
        st.error("� Configuration Error: N8N_WEBHOOK_URL not set in .env file")
        st.info("Please set up your n8n workflow and add the webhook URL to .env")
        return

    # Sidebar with info and sample questions
    with st.sidebar:
        st.header("📊 About This Project")
        st.markdown("""
        This is an AI-powered resume built using:
        - **RAG** (Retrieval-Augmented Generation)
        - **n8n AI/LangChain nodes** for the entire pipeline
        - **PostgreSQL + pgvector** for vector search
        - **Ollama** (nomic-embed-text + llama3.2) on VPS
        - **Streamlit** for this interface

        Built by Mike Murphy to demonstrate AI engineering skills.
        """)

        st.divider()

        st.header("💡 Sample Questions")
        st.markdown("Click a question below to try it:")

        sample_questions = [
            "What AI tutorials has Mike created?",
            "What makes Mike great for tech support roles?",
            "Tell me about Mike's RAG system experience",
            "What's Mike's experience with n8n?",
            "What courses has Mike published?",
            "Why should I hire Mike as an AI educator?"
        ]

        selected_question = None
        for i, question in enumerate(sample_questions):
            if st.button(f"💬 {question}", key=f"sample_{i}", use_container_width=True):
                selected_question = question

    # Main chat interface
    st.divider()

    # Use a form to enable Enter key submission
    with st.form(key="question_form", clear_on_submit=False):
        user_question = st.text_input(
            "Ask a question about Mike's experience:",
            value=selected_question if selected_question else "",
            placeholder="e.g., What's Mike's experience with AI?",
            key="user_input"
        )

        # Search button
        submit_button = st.form_submit_button("🔍 Ask", type="primary", use_container_width=True)

    if submit_button:
        if user_question:
            with st.spinner("🤔 AI is searching through Mike's resume and generating an answer... This may take 20-30 seconds."):
                result = query_resume(user_question, webhook_url)

                if result.get('error'):
                    st.error(result['answer'])
                else:
                    st.success(" Here's what I found:")
                    st.markdown(f"**Answer:**\n\n{result.get('answer', 'No answer generated')}")

                    # Show sources if available
                    if 'sources' in result:
                        with st.expander("📚 View Sources"):
                            st.write(result['sources'])
        else:
            st.warning("Please enter a question or click a sample question.")

    # Download section
    st.divider()
    st.subheader("📥 Download Resume Materials")

    col1, col2 = st.columns(2)

    with col1:
        # Check if PDF exists
        resume_pdf_path = Path(__file__).parent.parent / "docs" / "Mike_Murphy_Resume.pdf"
        if resume_pdf_path.exists():
            with open(resume_pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="📄 Download Resume (PDF)",
                    data=pdf_file,
                    file_name="Mike_Murphy_Resume.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        else:
            st.info("📄 PDF resume coming soon")

    with col2:
        cover_letter_path = Path(__file__).parent.parent / "docs" / "cover-letter_template.md"
        if cover_letter_path.exists():
            with open(cover_letter_path, "r") as cover_file:
                st.download_button(
                    label="📝 Download Cover Letter",
                    data=cover_file.read(),
                    file_name="Mike_Murphy_Cover_Letter.md",
                    mime="text/markdown",
                    use_container_width=True
                )

    # Footer
    st.divider()
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
        **Mike Murphy** | AI Educator & Technical Content Creator

        🌐 [mikemurphy.co](https://mikemurphy.co) |
        💼 [LinkedIn](https://linkedin.com/in/mikemurphyco) |
        📺 [YouTube](https://youtube.com/@mikemurphyco) |
        💻 [GitHub](https://github.com/mikemurphyco)

        *Built with Claude Code, n8n, PostgreSQL, Ollama, and Streamlit*
    """)
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
