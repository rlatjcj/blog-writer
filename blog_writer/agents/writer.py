from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from typing import Optional, List
from pydantic import BaseModel

from blog_writer.utils import State


def create_writer(state: State):
    """Write blog posts based on given outline.

    This agent writes blog posts based on given outline.
    This agent can use reference contents to write blog posts as a tool.

    Args:
        state (State): The state of the blog post.
    """
    reference_contents = "\n\n".join(
        [ref_content.page_content for ref_content in state["reference_contents"]]
    )
    llm = ChatOpenAI(model="gpt-4o-mini")

    # Write greeting and introduction
    greeting_prompt = PromptTemplate.from_template(
        """
        Please write a friendly and welcoming greeting to start a blog post about {topic}.
        Write like a friend who is visiting {topic} recently.
        Write in a comfortable and natural tone, but maintain a professional style.
        Writing style reference: {reference_style}
        Language: {language}
        """
    )
    greeting = llm.invoke(
        greeting_prompt.format(
            topic=state["topic"],
            reference_style=state["reference_style"],
            language=state["language"],
        )
    ).content
    previous_contents = [greeting]

    # Write sections
    section_prompt = PromptTemplate(
        template="""
        Write a detailed section ({section}) of the main topic ({topic}).
        
        Use the following search results to get appropriate information: {reference_contents}
        
        Refer to the previous sections and try not to repeat the same information: {previous_contents}
        
        Write the content with the following style:
        ## {section}
        content
        
        Writing style reference: {reference_style}
        Language: {language}
        
        Write only the content for this section ({section}), do not include any image prompts or suggestions.
        Detailed statistics or information is needed, so you should include collected information from search result.
        Do not include indirectly related information about the topic ({topic}).
        Write the content concisely in 5~10 lines.
        """,
        input_variables=["topic", "section", "reference_contents", "previous_contents"],
    )
    for section in state["outline"].values():
        section_content = llm.invoke(
            section_prompt.format(
                topic=state["topic"],
                section=section,
                reference_contents=reference_contents,
                previous_contents=previous_contents,
                reference_style=state["reference_style"],
                language=state["language"],
            )
        ).content
        previous_contents.append(section_content)

    # Write conclusion
    conclusion_prompt = PromptTemplate.from_template(
        """
        Please include your overall impressions of visiting {topic} and a warm farewell by summarizing the content from previous sections ({previous_contents}).
        Skip the greeting and go straight to the main content.
        Avoid formal business-like closings such as 'thank you for visiting'.
        Write in a comfortable and natural tone while maintaining professionalism.
        Maintain consistency with the tone used in the previous content.
        Write the content concisely in 3~5 lines.
        Writing style reference: {reference_style}
        Language: {language}
        Write the content with the following style:
        ## 총평
        content
        """
    )
    conclusion = llm.invoke(
        conclusion_prompt.format(
            topic=state["topic"],
            reference_style=state["reference_style"],
            previous_contents=previous_contents,
            language=state["language"],
        )
    ).content
    previous_contents.append(conclusion)

    return {"contents": previous_contents}
