"""Outline Generator Agent."""

import ast
import urllib.request
from datetime import datetime
from typing import Literal

from langchain_core.documents import Document
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import Field, create_model

from blog_writer.utils import State


def create_outline_generator(state: State) -> dict:
    """Generate an outline for a blog post based on the reference contents.

    Args:
        state (State): The state of the agent.

    Returns:
        dict: The generated outline and reference contents.
    """
    # If custom sections are provided, return state as is
    if state.get("custom_sections", False) and state["outline"]:
        return {
            "outline": state["outline"],
            "reference_contents": state.get("reference_contents", []),
        }

    def create_outline_model(section_count: int):
        fields = {
            f"section{i}": (str, Field(description=f"Title for section {i}"))
            for i in range(1, section_count + 1)
        }
        return create_model("DynamicOutline", **fields)

    # Generate outline using LLM
    llm = ChatOpenAI(model="gpt-4o-mini")
    dynamic_outline = create_outline_model(state["total_sections"])
    outline_parser = JsonOutputParser(pydantic_object=dynamic_outline)

    outline_prompt = PromptTemplate(
        template="""
        You are a professional blog writer and your role is to generate an outline for a blog post.
        You should always answer in same language as user's ask.
        Based on the following reference contents and topic, generate an outline for a blog post:

        Topic: {topic}

        Reference Contents:
        {reference_contents}

        {format_instructions}

        Please create a concise and structured outline that captures the key points and
        ideas from the reference contents.
        Do not include indirectly related information about the topic ({topic}).
        Today is {date}
        """,
        input_variables=["reference_contents", "topic", "date"],
        partial_variables={"format_instructions": outline_parser.get_format_instructions()},
    )

    if state["platform"] == "naver":
        secret_key = {
            "client_id": state["naver_client_id"],
            "client_secret": state["naver_client_secret"],
        }
    reference_contents = scrape_reference_contents(state["topic"], state["platform"], secret_key)

    chain = outline_prompt | llm | outline_parser
    outline = chain.invoke(
        {
            "topic": state["topic"],
            "reference_contents": reference_contents,
            "date": datetime.now().strftime("%Y-%m-%d"),
        }
    )
    return {"outline": outline, "reference_contents": reference_contents}


def scrape_reference_contents(
    topic: str,
    platform: Literal["naver"] = "naver",
    secret_key: dict = {},
) -> list[Document]:
    """Scrape reference contents from the web.

    Args:
        topic (str): The topic to search for.
        platform (Literal["naver"]): The platform to search for.
        secret_key (dict): The secret key for the platform.
    Returns:
        list[Document]: The contents of the blog posts.
            If no blog posts are found, returns an empty list.
    """
    formatted_results: list[Document] = []
    if platform == "naver":
        results = search_naver_blog_posts(
            topic,
            secret_key["client_id"],
            secret_key["client_secret"],
        )
        for result in results["items"]:
            formatted_results.append(
                Document(
                    page_content=result["description"],
                    metadata={
                        "source": result["link"],
                        "date": result["postdate"],
                        "title": result["title"],
                        "author": result["bloggername"],
                    },
                )
            )

    if formatted_results:
        return formatted_results
    return []


def search_naver_blog_posts(
    topic: str,
    client_id: str,
    client_secret: str,
) -> dict:
    """Use Naver Blog API to search for blog posts.

    Args:
        topic (str): The topic to search for.
        client_id (str): The client ID for the Naver API.
        client_secret (str): The client secret for the Naver API.

    Returns:
        dict: The contents of the blog posts with below keys:
            - lastBuildDate: The date of the last blog post.
            - total: The total number of blog posts.
            - start: The start index of the blog posts.
            - display: The number of blog posts to display.
            - items: The list of blog posts.
                - each item has below keys:
                    - title: The title of the blog post.
                    - link: The link to the blog post.
                    - description: The description of the blog post.
                    - bloggername: The name of the blog author.
                    - bloggerlink: The link to the blog author's profile.
                    - postdate: The date the blog post was published.
    """
    encText = urllib.parse.quote(topic)
    url = "https://openapi.naver.com/v1/search/blog?query=" + encText
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if rescode == 200:
        response_body = response.read()
        return ast.literal_eval(response_body.decode("utf-8"))
    else:
        return {"items": []}
