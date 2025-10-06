import streamlit as st
import os
from agent import ResearchAgent
from config import setup_environment

def main():
    """Main entry point for the credibility research agent with Streamlit UI"""
    st.title("Credibility-Aware Research Agent")
    st.markdown("Enter a research topic to analyze claims and generate a credibility report. Optionally, upload a .txt or .md file to update research.")

    # Initialize agent in session state to persist across reruns
    if 'agent' not in st.session_state:
        setup_environment()  # Load API keys and config
        st.session_state.agent = ResearchAgent()
    agent = st.session_state.agent

    # Input topic
    topic = st.text_input("Enter research topic:", placeholder="e.g., What is the meaning of life")

    if st.button("Research"):
        if not topic:
            st.error("Please provide a topic.")
            return

        with st.spinner("🔍 Researching..."):
            try:
                result = agent.research(topic)
                st.success("✅ Research complete!")

                # Display report
                st.subheader("📊 Research Report")
                st.markdown(result['report'])
                st.write(f"**⭐ Overall Credibility:** {result['overall_credibility']:.2f}/10")
                st.write(f"**📈 Sources Analyzed:** {result['sources_count']}")

                # Display claims
                st.subheader("📝 Claims Analyzed")
                for claim in result['claims']:
                    st.write(f"- {claim['text']} (Score: {claim['credibility_score']}/10, Action: {claim['action']})")
            except Exception as e:
                st.error(f"Error during research: {e}")

    # Update with file
    st.subheader("📂 Update Research with File")
    uploaded_file = st.file_uploader("Upload a file to update research", type=["txt", "md"])
    if uploaded_file and st.button("Update Research"):
        with st.spinner("🔄 Updating research..."):
            try:
                # Save uploaded file with original extension
                file_extension = uploaded_file.name.split('.')[-1]
                temp_path = f"temp_file.{file_extension}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.read())

                # Check if prior research exists
                if not agent.research_cache:
                    st.warning("No prior research found. This upload will start new research on the file content.")

                result = agent.update_research(temp_path)
                if result is None:
                    st.error("Update failed: No prior research or invalid file. Run initial research first.")
                    return

                # Clean up
                os.remove(temp_path)

                st.success("✅ Update complete!")

                # Display updated report
                st.subheader("📊 Updated Research Report")
                st.markdown(result['report'])
                st.write(f"**⭐ Overall Credibility:** {result['overall_credibility']:.2f}/10")
                st.write("**📝 Updated Claims:**")
                for claim in result['claims']:
                    st.write(f"- {claim['text']} (Score: {claim['credibility_score']}/10, Action: {claim['action']})")
            except IndexError as e:
                st.error(f"Cache error (likely no prior research): {e}. Run a topic search first!")
            except Exception as e:
                st.error(f"Error during update: {e}")

if __name__ == "__main__":
    main()