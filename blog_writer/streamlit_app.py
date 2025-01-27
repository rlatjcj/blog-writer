"""Streamlit app for blog writer."""

import os

import streamlit as st
from dotenv import load_dotenv
from streamlit.runtime.uploaded_file_manager import UploadedFile

from blog_writer.graph import create_graph
from blog_writer.utils import State


def display_images(section_images: list[UploadedFile]) -> None:
    """Display images in a grid.

    Args:
        section_images: List of images to display.
    """
    if not section_images:
        return

    # Display images divided into columns based on the number of cols
    columns = st.columns(len(section_images))

    for idx, section_image in enumerate(section_images):
        with columns[idx % len(section_images)]:
            st.image(section_image)


if __name__ == "__main__":
    st.set_page_config(page_title="Blog Post Generator", layout="wide")

    st.title("✍️ Auto Blog Post Generator")

    # Initialize session state
    if "contents" not in st.session_state:
        st.session_state.contents = None
    if "custom_sections" not in st.session_state:
        st.session_state.custom_sections = False
    if "section_titles" not in st.session_state:
        st.session_state.section_titles = {}

    # Create form for input
    topic = st.text_input("주제", placeholder="예: 제주도 카멜리아힐")
    title = st.text_input("제목", placeholder="예: 제주도 카멜리아힐 방문후기")
    total_sections = st.number_input("소제목 수", min_value=1, max_value=10, value=5, step=1)

    # Add checkbox for custom section titles outside the form
    custom_sections = st.checkbox("소제목을 직접 입력하시겠습니까?", key="custom_sections_checkbox")

    # Create input fields for section titles if checkbox is checked
    if custom_sections:
        section_titles = {}
        section_images = {}
        with st.expander("소제목을 입력해주세요:", expanded=True):
            for i in range(1, total_sections + 1):
                section_key = f"section{i}"

                section_titles[section_key] = st.text_input(
                    f"소제목 {i}",
                    key=section_key,
                    placeholder="예: 방문 정보, 추천 코스 등",
                    help="이 필드는 필수입니다.",
                )

                if not section_titles[section_key].strip():
                    st.warning(f"소제목 {i}를 입력해주세요.")

                section_images[section_key] = st.file_uploader(
                    "사진 업로드",
                    accept_multiple_files=True,
                    type=["png", "jpg", "jpeg"],
                    key=f"image_{section_key}",
                    label_visibility="collapsed",
                )

        st.session_state.section_titles = section_titles
        st.session_state.section_images = section_images

    # else:
    #     uploaded_images = st.file_uploader(
    #         "블로그 작성에 참고할 사진, 그림을 추가해주세요.",
    #         accept_multiple_files=True,
    #         type=["png", "jpg", "jpeg"],
    #     )

    platform = st.selectbox("플랫폼", ["naver"])
    language = st.selectbox("언어", ["ko", "en"])
    submit_button = st.button("블로그 글 생성")

    if submit_button:
        load_dotenv()

        # Create graph
        graph = create_graph()

        # Prepare initial state
        initial_state = State(
            topic=topic,
            platform=platform,
            total_sections=total_sections,
            reference_contents=[],
            reference_style="friendly and natural tone",  # TODO (sungchul): input reference style
            language=language,
            naver_client_id=os.getenv("NAVER_CLIENT_ID"),
            naver_client_secret=os.getenv("NAVER_CLIENT_SECRET"),
            outline=(
                st.session_state.section_titles
                if custom_sections and all(st.session_state.section_titles.values())
                else {}
            ),
            section_images=st.session_state.get("section_images", {}),
            custom_sections=custom_sections and all(st.session_state.section_titles.values()),
        )

        with st.spinner("블로그 글을 생성하고 있습니다..."):
            final_state = graph.invoke(initial_state)
            st.session_state.contents = final_state["contents"]

    # Display generated blog post
    if st.session_state.contents:
        contents = st.session_state.contents

        st.header(initial_state["topic"])
        st.write("---")
        for idx, content in enumerate(contents):
            st.write(content)
            if 1 <= idx < len(contents) - 1:
                if section_images := st.session_state.section_images.get(f"section{idx}", None):
                    display_images(section_images)

            st.write("---")
