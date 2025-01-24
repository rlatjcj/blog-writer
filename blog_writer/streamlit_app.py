"""Streamlit app for blog writer."""

import os

import streamlit as st
from dotenv import load_dotenv

from blog_writer.graph import create_graph
from blog_writer.utils import State

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
    section_titles = {}
    if custom_sections:
        with st.expander("소제목을 입력해주세요:", expanded=True):
            for i in range(1, total_sections + 1):
                section_key = f"section{i}"
                section_titles[section_key] = st.text_input(
                    f"소제목 {i}", key=section_key, placeholder="예: 방문 정보, 추천 코스 등"
                )
        st.session_state.section_titles = section_titles

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
        for content in contents:
            st.write(content)
            st.write("---")
