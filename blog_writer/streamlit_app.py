import streamlit as st
from blog_writer.workflow import create_blog_workflow, BlogState
import os

st.set_page_config(page_title="Blog Post Generator", layout="wide")

st.title("✍️ Auto Blog Post Generator")

# Initialize session state
if "blog_content" not in st.session_state:
    st.session_state.blog_content = None

# Create form for input
with st.form("blog_input_form"):
    title = st.text_input("장소 이름", placeholder="예: 제주도 카멜리아힐")

    information = st.text_area(
        "포스팅 정보",
        placeholder="주소, 운영시간, 입장료 등 기본 정보 또는 포스팅 작성에 참고할 내용을 입력해주세요.",
    )

    reference = st.text_area(
        "참고할 글 스타일 (선택사항)",
        placeholder="참고하고 싶은 블로그 글이나 말투를 입력해주세요.",
    )

    uploaded_files = st.file_uploader(
        "사진 업로드", accept_multiple_files=True, type=["png", "jpg", "jpeg"]
    )

    submit_button = st.form_submit_button("블로그 글 생성")

if submit_button and uploaded_files:
    # Save uploaded images
    image_paths = []
    for uploaded_file in uploaded_files:
        with open(f"temp_{uploaded_file.name}", "wb") as f:
            f.write(uploaded_file.getbuffer())
            image_paths.append(f"temp_{uploaded_file.name}")

    # Create workflow
    workflow = create_blog_workflow()

    # Prepare initial state
    initial_state = BlogState(
        title=title,
        information=information,
        images=image_paths,
        reference=reference,
        retrieved_contents=[],
        blog_content={},
    )

    with st.spinner("블로그 글을 생성하고 있습니다..."):
        # Run workflow
        final_state = workflow.invoke(initial_state)
        st.session_state.blog_content = final_state["blog_content"]
        st.session_state.image_paths = image_paths  # 이미지 경로 저장

# Display generated blog post
if st.session_state.blog_content:
    content = st.session_state.blog_content

    st.header(title)
    st.write("---")

    # Display greeting
    st.write(content["greeting"])
    st.write("---")

    # Display place information
    st.subheader("📍 장소 정보")
    st.write(content["place_info"])
    st.write("---")

    # Display images and descriptions
    st.subheader("📸 방문 후기")
    for item in content["image_descriptions"]:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(item["image"])
        with col2:
            st.write(item["description"])
        st.write("---")

    # Display conclusion
    st.write(content["conclusion"])

    # Clean up temporary files after displaying
    if "image_paths" in st.session_state:
        for path in st.session_state.image_paths:
            try:
                os.remove(path)
            except FileNotFoundError:
                pass
        del st.session_state.image_paths
