import ast
import os
import urllib.request
from typing import Literal

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


class ReferenceEmbedder:
    """This class finds reference descriptions from blog posts using user query.

    When given query, it searches for relevant blog posts and embeds them to vector database.
    These embeddings will be used as a reference for PostWriter when writing blog posts.
    """

    def __init__(self):
        self.retriever = None

    def set_reference_into_db(
        self, query: str, platform: Literal["naver"] = "naver"
    ) -> None:
        """Set reference blog posts into vector database for RAG.

        Args:
            query (str): The query to search for.
            platform (Literal["naver"]): The platform to search for.
        """
        blog_posts = self.search_blog_posts(query, platform)
        self.embed_blog_posts(blog_posts)

    def search_blog_posts(
        self,
        query: str,
        platform: Literal["naver"] = "naver",
    ) -> list[Document]:
        """Search for blog posts.

        Args:
            query (str): The query to search for.
            platform (Literal["naver"]): The platform to search for.

        Returns:
            list[Document]: The contents of the blog posts. If no blog posts are found, returns an empty list.
        """
        formatted_results: list[Document] = []
        if platform == "naver":
            results = search_naver_blog_posts(query)
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
        else:
            raise ValueError(f"Unsupported platform: {platform}")

        if formatted_results:
            return formatted_results
        return []

    def embed_blog_posts(self, formatted_blog_posts: list[Document]) -> None:
        """Embed blog posts to vector database.

        TODO (sungchul): make text_splitter, embeddings, and db more flexible as using arguments.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", ".", ",", " ", ""],
            chunk_size=1000,
            chunk_overlap=0,
        )

        texts = text_splitter.split_documents(formatted_blog_posts)
        embeddings = OpenAIEmbeddings()
        db = Chroma.from_documents(texts, embeddings)
        self.retriever = db.as_retriever()


def search_naver_blog_posts(
    query: str,
    client_id: str = os.getenv("NAVER_CLIENT_ID"),
    client_secret: str = os.getenv("NAVER_CLIENT_SECRET"),
) -> dict | str:
    """Use Naver Blog API to search for blog posts.

    Args:
        query (str): The query to search for.
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
        str: The error message if the request fails.
    """
    encText = urllib.parse.quote(query)
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


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    contents = search_naver_blog_posts("카멜리아힐")
    print(contents)
