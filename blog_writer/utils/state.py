from typing import Literal, TypedDict
from langchain_core.documents import Document


class State(TypedDict):
    topic: str
    platform: Literal["naver"]
    reference_contents: list[Document] = []
    reference_style: str = "friendly and natural tone"
    total_sections: int = 5
    outline: dict
    contents: dict
    language: Literal["ko", "en"] = "ko"
