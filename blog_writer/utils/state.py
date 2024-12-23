from typing import Literal, TypedDict
from langchain_core.documents import Document


class State(TypedDict):
    topic: str
    platform: Literal["naver"]
    reference_contents: list[Document] = []
    total_sections: int = 5
    outline: str = ""
