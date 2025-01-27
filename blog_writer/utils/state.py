"""State for blog writer."""

from typing import Literal, TypedDict

from langchain_core.documents import Document


class State(TypedDict):
    """State for blog writer."""

    topic: str
    platform: Literal["naver"]
    reference_contents: list[Document] = []
    reference_style: str = "friendly and natural tone"
    total_sections: int = 5
    current_section: int = 0
    outline: dict = {}
    section_images: dict = {}
    contents: dict = {}
    language: Literal["ko", "en"] = "ko"
    naver_client_id: str
    naver_client_secret: str
    custom_sections: bool = False
