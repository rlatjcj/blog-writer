import os

import streamlit as st

from blog_writer.graph import create_graph
from blog_writer.utils import State

st.set_page_config(page_title="Blog Post Generator", layout="wide")

st.title("✍️ Auto Blog Post Generator")

# Initialize session state
if "contents" not in st.session_state:
    st.session_state.contents = None

# Create form for input
with st.form("blog_input_form"):
    topic = st.text_input("주제", placeholder="예: 제주도 카멜리아힐")
    title = st.text_input("제목", placeholder="예: 제주도 카멜리아힐 방문후기")
    platform = st.selectbox("플랫폼", ["naver"])
    language = st.selectbox("언어", ["ko", "en"])

    submit_button = st.form_submit_button("블로그 글 생성")

if submit_button:
    # Create graph
    graph = create_graph()

    # Prepare initial state
    initial_state = State(
        topic=topic,
        platform=platform,
        total_sections=5,
        reference_contents=[],
        reference_style="friendly and natural tone",  # TODO (sungchul): enable to input reference style
        language=language,
    )

    with st.spinner("블로그 글을 생성하고 있습니다..."):
        # Run graph
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
else:
    st.write("블로그 글이 생성되지 않았습니다.")
