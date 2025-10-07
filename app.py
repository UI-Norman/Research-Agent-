import streamlit as st
from agent import ResearchAgent
from config import setup_environment
from llm_factory import LLMFactory
import os

def display_llm_menu(config):
    models = LLMFactory.get_available_models(config)
    model_options = [f"{model['display']}" for model in models]
    return models, model_options

def main():
    st.set_page_config(page_title="Credibility-Aware Research Agent", layout="wide")
    st.title("🔬 Credibility-Aware Research Agent")
    st.markdown("Enter a research topic to analyze claims and generate a credibility report with a summary, detailed findings, and source analysis. Optionally, upload a .txt, .pdf, or .docx file to update research.")

    if 'config' not in st.session_state:
        st.session_state.config = setup_environment()
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'research_result' not in st.session_state:
        st.session_state.research_result = None
    if 'update_result' not in st.session_state:
        st.session_state.update_result = None

    st.header("🤖 Select Your LLM")
    models, model_options = display_llm_menu(st.session_state.config)
    selected_model = st.selectbox("Choose a model:", model_options, key="llm_select")
    
    selected_idx = model_options.index(selected_model)
    provider = models[selected_idx]['provider']
    model = models[selected_idx]['model']
    
    if st.button("Confirm LLM Selection"):
        st.session_state.agent = ResearchAgent(provider, model)
        st.success(f"✅ Selected: {selected_model}")

    if st.session_state.agent:
        st.header("📌 Research Topic")
        topic = st.text_input("Enter research topic:", key="topic_input", placeholder="e.g., What is the meaning of life")
        
        if st.button("🔍 Start Research") and topic:
            with st.spinner("🔎 Researching..."):
                try:
                    st.session_state.research_result = st.session_state.agent.research(topic)
                    st.success(f"✅ Research complete for: {topic}")
                except Exception as e:
                    st.error(f"❌ Research failed: {str(e)}")

        if st.session_state.research_result:
            st.header("📊 Research Report")
            st.markdown(st.session_state.research_result['report'])
            st.write("---")
            st.write(f"⭐ **Overall Credibility**: {st.session_state.research_result['overall_credibility']:.2f}/10")
            st.write(f"📚 **Sources Analyzed**: {st.session_state.research_result['sources_count']}")
            st.markdown(f"**Source Details**:\n{st.session_state.research_result['sources_analyzed']}")
            st.write(f"⏱️ **Processing Time**: {st.session_state.research_result['time_seconds']:.1f}s")
            st.write("---")

            if st.button("💾 Download Report"):
                filename = f"research_{topic.replace(' ', '_')[:30]}.md"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(st.session_state.research_result['report'] + "\n\n## Sources Analyzed\n" + st.session_state.research_result['sources_analyzed'])
                with open(filename, 'rb') as f:
                    st.download_button(
                        label="Download Report as Markdown",
                        data=f,
                        file_name=filename,
                        mime="text/markdown"
                    )

        st.header("📂 Update Research")
        uploaded_file = st.file_uploader("Upload a file to update research:", type=["txt", "pdf", "docx"])
        if uploaded_file and st.button("🔄 Process Update"):
            with st.spinner("🔄 Processing update..."):
                try:
                    file_extension = uploaded_file.name.split('.')[-1]
                    temp_path = f"temp_update.{file_extension}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.read())
                    st.session_state.update_result = st.session_state.agent.update_research(temp_path)
                    st.success("✅ Update complete!")
                except Exception as e:
                    st.error(f"❌ Update failed: {str(e)}")
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

        if st.session_state.update_result:
            st.header("📊 Updated Research Report")
            st.markdown(st.session_state.update_result['report'])
            st.write("---")
            st.write(f"⭐ **New Credibility**: {st.session_state.update_result['overall_credibility']:.2f}/10")
            st.write(f"📚 **Sources Analyzed**: {st.session_state.update_result['sources_analyzed']}")
            st.write(f"⏱️ **Update Time**: {st.session_state.update_result['update_time']:.1f}s")
            st.write(f"📉 **Overhead**: {st.session_state.update_result['overhead_ratio']*100:.1f}% of initial")
            st.write(f"🎯 **Strategy**: {st.session_state.update_result['update_strategy']['approach']}")
            st.write(f"💡 **Reasoning**: {st.session_state.update_result['update_strategy']['reasoning']}")
            st.write("---")

if __name__ == "__main__":
    main()