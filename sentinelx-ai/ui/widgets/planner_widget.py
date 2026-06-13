import streamlit as st

def planner_widget(view_model):
    st.title("💻 Planner AI Mode")

    st.markdown("### 📂 Upload Algorithm / Config")

    # File Upload
    uploaded_file = st.file_uploader(
        "Upload Algorithm or Config File",
        type=["txt", "py", "md", "doc"]
    )

    if uploaded_file is not None:
        content = uploaded_file.read().decode("utf-8")

        # Send to ViewModel
        view_model.on_file_uploaded(content)

    st.divider()

    # 🔹 Input Preview
    st.markdown("### 📄 Input Content")

    if view_model.input_content:
        st.code(view_model.input_content, language="python")
    else:
        st.info("No input uploaded yet.")

    st.divider()

    # 🔹 Output Section
    st.markdown("### 🤖 AI Explanation")

    if view_model.output_content:
        st.success("Generated Output:")
        st.write(view_model.output_content)
    else:
        st.warning("No output generated yet.")

    st.divider()

    # 🔹 Config Display (BOTTOM - IMPORTANT)
    st.markdown("### ⚙️ Active Configuration")

    if view_model.current_config:
        st.json(view_model.current_config)
    else:
        st.info("No configuration loaded.")