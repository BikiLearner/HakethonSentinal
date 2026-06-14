import streamlit as st
import os

def planner_widget(view_model):
    st.title("💻 Planner AI Mode")
    st.markdown("Upgrade your analysis with Gemini AI. Upload a file to get a detailed breakdown.")

    st.markdown("---")

    # File Upload
    uploaded_file = st.file_uploader(
        "Upload a .py, .txt, .md, or .docx file",
        type=["txt", "py", "md", "doc", "docx"],
        on_change=view_model.clear_all  # Clear state on new file selection
    )

    if uploaded_file is not None:
        # Trigger analysis on first upload
        if not view_model.input_content and not view_model.is_loading:
            view_model.on_file_uploaded(uploaded_file)

    st.markdown("---")
    
    # --- UI Rendering Logic ---

    # 1. Loading State
    if view_model.is_loading:
        with st.spinner("🤖 Gemini is analyzing your file... Please wait."):
            # The view_model is processing in the background
            pass

    # 2. Error State
    elif view_model.error_message:
        st.error(f"**Analysis Failed:** {view_model.error_message}")
        st.warning("Please check your API key, file content, or try again later.")

    # 3. Success State (Output Display)
    elif view_model.output_content:
        st.success("🎉 Analysis Complete!")
        
        output = view_model.output_content
        
        # Display Sections
        st.markdown("### 📌 Summary")
        st.write(output.get('summary', 'Not available.'))

        st.markdown("### ⚡ Complexity")
        st.code(output.get('complexity', 'Not available.'), language='text')

        st.markdown("### 🚀 Improvements")
        improvements = output.get('improvements', [])
        if improvements:
            for item in improvements:
                st.markdown(f"- {item}")
        else:
            st.info("No specific improvements suggested.")

        st.markdown("### 🌍 Use Case")
        st.info(output.get('use_case', 'Not available.'))

        st.markdown("### 🧭 Step-by-step Plan")
        steps = output.get('step_by_step', [])
        if steps:
            for i, step in enumerate(steps, 1):
                st.markdown(f"{i}. {step}")
        else:
            st.info("No step-by-step plan provided.")
            
        st.markdown("---")
        
        # Expander for original content
        with st.expander("📄 View Original Uploaded Content"):
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            lang = 'python' if file_extension == '.py' else 'text'
            st.code(view_model.input_content, language=lang)

    # 4. Initial State
    else:
        st.info("👋 Welcome! Upload a file to begin the AI analysis.")

