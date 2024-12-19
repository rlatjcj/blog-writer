import ast
import os
import urllib.request


def search_naver_blog(
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
        return "Error Code:" + rescode


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    contents = search_naver_blog("카멜리아힐")
    print(contents)
