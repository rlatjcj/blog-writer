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


def get_ui_text(language: str) -> dict:
    """Get UI text based on selected language.

    Args:
        language (str): Selected language code ('ko' or 'en')

    Returns:
        dict: UI text dictionary
    """
    if language == "en":
        return {
            "title": "✍️ Auto Blog Post Generator",
            "topic": "Topic",
            "topic_placeholder": "e.g., Camellia Hill in Jeju",
            "title_input": "Title",
            "title_placeholder": "e.g., My Visit to Camellia Hill in Jeju",
            "sections_count": "Number of Sections",
            "custom_sections_check": "Would you like to enter section titles manually?",
            "sections_expander": "Please enter section titles:",
            "section_placeholder": "e.g., Visitor Information, Recommended Course",
            "section_help": "This field is required.",
            "section_warning": "Please enter section title {}.",
            "photo_upload": "Photo Upload",
            "platform": "Platform",
            "language": "Language",
            "generate_button": "Generate Blog Post",
            "generating_spinner": "Generating blog post...",
        }
    return {
        "title": "✍️ 자동 블로그 글 생성기",
        "topic": "주제",
        "topic_placeholder": "예: 제주도 카멜리아힐",
        "title_input": "제목",
        "title_placeholder": "예: 제주도 카멜리아힐 방문후기",
        "sections_count": "소제목 수",
        "custom_sections_check": "소제목을 직접 입력하시겠습니까?",
        "sections_expander": "소제목을 입력해주세요:",
        "section_placeholder": "예: 방문 정보, 추천 코스 등",
        "section_help": "이 필드는 필수입니다.",
        "section_warning": "소제목 {}를 입력해주세요.",
        "photo_upload": "사진 업로드",
        "platform": "플랫폼",
        "language": "언어",
        "generate_button": "블로그 글 생성",
        "generating_spinner": "블로그 글을 생성하고 있습니다...",
    }


if __name__ == "__main__":
    st.set_page_config(page_title="Blog Post Generator", layout="wide")

    # Language selector at the top
    language = st.selectbox("Language / 언어", ["ko", "en"], index=0)
    ui_text = get_ui_text(language)

    st.title(ui_text["title"])

    # Initialize session state
    if "contents" not in st.session_state:
        st.session_state.contents = None
    if "custom_sections" not in st.session_state:
        st.session_state.custom_sections = False
    if "section_titles" not in st.session_state:
        st.session_state.section_titles = {}

    # Create form for input
    topic = st.text_input(ui_text["topic"], placeholder=ui_text["topic_placeholder"])
    title = st.text_input(ui_text["title_input"], placeholder=ui_text["title_placeholder"])
    total_sections = st.number_input(
        ui_text["sections_count"], min_value=1, max_value=10, value=5, step=1
    )

    # Add checkbox for custom section titles
    custom_sections = st.checkbox(ui_text["custom_sections_check"], key="custom_sections_checkbox")

    # Create input fields for section titles if checkbox is checked
    if custom_sections:
        section_titles = {}
        section_images = {}
        with st.expander(ui_text["sections_expander"], expanded=True):
            for i in range(1, total_sections + 1):
                section_key = f"section{i}"

                section_titles[section_key] = st.text_input(
                    f"{ui_text['sections_count']} {i}",
                    key=section_key,
                    placeholder=ui_text["section_placeholder"],
                    help=ui_text["section_help"],
                )

                if not section_titles[section_key].strip():
                    st.warning(ui_text["section_warning"].format(i))

                section_images[section_key] = st.file_uploader(
                    ui_text["photo_upload"],
                    accept_multiple_files=True,
                    type=["png", "jpg", "jpeg"],
                    key=f"image_{section_key}",
                    label_visibility="collapsed",
                )

        st.session_state.section_titles = section_titles
        st.session_state.section_images = section_images

    platform = st.selectbox(ui_text["platform"], ["naver"])
    submit_button = st.button(ui_text["generate_button"])

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
            reference_style="friendly and natural tone",
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

        with st.spinner(ui_text["generating_spinner"]):
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
