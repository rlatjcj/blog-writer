from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from typing import Optional, List
from pydantic import BaseModel


class BlogPostInput(BaseModel):
    title: str
    information: str
    images: List[str]
    reference: Optional[str] = None
    retrieved_contents: Optional[List[str]] = None


class PostWriter:
    """This agent writes blog posts based on given title, information, images, and reference.

    To write blog posts, following steps:
    1. Set reference blog posts into vector database.
    2. Get title, information, and images from user.
    3. Set outline based on the title and information.
    4. Analyze the images based on the reference blog posts.
    5. Write a blog post based on the title, information, images, and reference.
    """

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    def write_blog_post(self, args: BlogPostInput) -> dict:
        """Write a blog post based on given title, information, images, and reference."""
        # 1. Write greeting and introduction
        greeting_prompt = PromptTemplate.from_template(
            """
            {title}에 대한 블로그 포스트를 시작하는 친근하고 반가운 인사말을 작성해주세요. 
            편안하고 자연스러운 말투로 작성하지만, 반말은 사용하지 말아주세요.
            참고할 글 스타일: {reference}
            """
        )
        greeting = self.llm.invoke(
            greeting_prompt.format(
                title=args.title, reference=args.reference or "친근하고 자연스러운 말투"
            )
        ).content
        previous_sections = f"{greeting}"

        # 2. Write place information
        info_prompt = PromptTemplate.from_template(
            """
            다음 장소에 대한 상세한 정보를 작성해주세요: {information}
            이전 섹션 ({previous_sections})에서 작성한 내용을 참고해주세요.
            인사말을 작성하지 않고 바로 본론으로 들어가세요.
            실용적인 정보와 흥미로운 사실들을 포함해주세요.
            편안하고 자연스러운 말투로 작성하지만, 반말은 사용하지 말아주세요.
            앞서 작성한 인사말의 톤과 일관성 있게 작성해주세요.
            참고할 글 스타일: {reference}
            참고할 만한 내용: {references}
            """
        )
        place_info = self.llm.invoke(
            info_prompt.format(
                information=args.information,
                reference=args.reference or "친근하고 자연스러운 말투",
                references=(
                    "\n".join(args.retrieved_contents)
                    if args.retrieved_contents
                    else "없음"
                ),
                previous_sections=previous_sections,
            )
        ).content
        previous_sections += f"\n\n{place_info}"

        # 3. Write image descriptions
        image_descriptions = []
        for image in args.images:
            img_prompt = PromptTemplate.from_template(
                """
                {location}을(를) 둘러보다가 마주친 풍경을 생생하게 설명해주세요.
                이전 섹션 ({previous_sections})에서 작성한 내용을 참고해주세요.
                인사말을 작성하지 않고 바로 본론으로 들어가세요.
                마치 직접 방문해서 보고 느낀 것처럼 감정과 분위기를 담아주세요.
                편안하고 자연스러운 말투로 작성하지만, 반말은 사용하지 말아주세요.
                3~5줄 이내로 간단명료하게 작성해주세요.
                앞서 작성한 내용의 톤과 일관성 있게 작성해주세요.
                '이 사진', '여기서는' 등의 사진 지칭 표현은 사용하지 말고,
                실제로 그 곳에 서있는 것처럼 현장감 있게 설명해주세요.
                참고할 글 스타일: {reference}
                참고할 만한 내용: {references}
                """
            )
            desc = self.llm.invoke(
                img_prompt.format(
                    location=args.title,
                    reference=args.reference or "친근하고 자연스러운 말투",
                    references=(
                        "\n".join(args.retrieved_contents)
                        if args.retrieved_contents
                        else "없음"
                    ),
                    previous_sections=previous_sections,
                )
            ).content
            image_descriptions.append({"image": image, "description": desc})
            previous_sections += f"\n\n{desc}"
        # 4. Write conclusion
        conclusion_prompt = PromptTemplate.from_template(
            """
            {title} 방문에 대한 전반적인 인상과 따뜻한 작별 인사를 포함해주세요.
            이전 섹션 ({previous_sections})에서 작성한 내용을 참고해주세요.
            인사말을 작성하지 않고 바로 본론으로 들어가세요.
            '~해주셔서 감사합니다' 같은 업장 인사는 포함하지 않아주세요.
            편안하고 자연스러운 말투로 작성하지만, 반말은 사용하지 말아주세요.
            앞서 작성한 내용들의 톤과 일관성 있게 작성해주세요.
            참고할 글 스타일: {reference}
            """
        )
        conclusion = self.llm.invoke(
            conclusion_prompt.format(
                title=args.title,
                reference=args.reference or "친근하고 자연스러운 말투",
                previous_sections=previous_sections,
            )
        ).content

        return {
            "greeting": greeting,
            "place_info": place_info,
            "image_descriptions": image_descriptions,
            "conclusion": conclusion,
        }
