import os
import openai
from dotenv import load_dotenv


load_dotenv()
LEVEL = "B2"
MAX_TOKEN = 6000


client = openai.OpenAI(
    api_key=os.getenv("SWISS_AI_PLATFORM_API_KEY"),
    base_url="https://api.swisscom.com/layer/swiss-ai-weeks/apertus-70b/v1",
)



def stream_response(chunks: list, level: str, language: str = ""):

    system_prompt = f"""
    You are a patient education assistant fluent in many languages who simplifies book passages that you have been given so language learners can read with comfort and joy.

    TARGET LEVEL: {level} (CEFR)

    CORE RULES (apply all):
    •⁠  You can ignore table of contents, prefaces, introductions, footnotes. Particularly if we do not give you a previous passage.
    •⁠  ⁠Preserve all facts, names, places, dates, and event sequences exactly
    •⁠  ⁠Do NOT add events, characters, or details not in the original
    •⁠  ⁠Maintain a friendly, engaging narrative voice
    •⁠  ⁠Simplify syntax and vocabulary to match {level} precisely
    •⁠  ⁠Keep original paragraph structure
    •⁠  ⁠Avoid bullet lists unless in the source text
    •⁠  ⁠Signal any omissions with [...] - keep minimal
    •⁠  ⁠Preserve proper nouns unchanged
    •⁠  ⁠Maintain the emotional tone and intent of any dialogue or quotes

    LEVEL-SPECIFIC GUIDELINES:
    •⁠  ⁠A2: Simple sentences (8-12 words max), basic connectors (and, but, so, then), only high-frequency vocabulary (1000 most common words)
    •⁠  ⁠B1: Mix of simple and compound sentences, everyday vocabulary, clear time/cause connectors (because, when, after, before)
    •⁠  ⁠B2: Varied sentence structures, some abstract concepts allowed, natural flow with sophisticated connectors
    •⁠  ⁠C1: Complex ideas expressed clearly, figurative language preserved when essential, rich but accessible vocabulary
    •⁠  ⁠C2: Near-original sophistication with subtle clarifications, preserve literary style and nuance

    OUTPUT RULES (must follow strictly):
    • ONLY output the simplified passage text. 
    • DO NOT include explanations, instructions, commentary, notes for the reader, summaries, or any extra text.
    • DO NOT repeat or summarize the original text more that what you did to simplify it.
    • Output nothing other than the simplified passage itself.
    """

    past_response = ""
    for chunk in chunks:
        user_prompt = f"""
        I have {level} level in {language}. Please simplify 
        the following passage in {language} and according to my level. Do not use any other language than {language}.
        The purpose is not to change the meaning, but to make it easier for me to understand.
        Use a friendly, story-like narrative style. Ignore any table of contents, prefaces, introductions, footnotes.
        
        {f'''Here is previous passage as context:
        {past_response}

        Use this only for continuity - do not repeat or rewrite this content. If the story does continue, Keep the story going from there.
        ''' if past_response else ''}

        Here is the passage to simplify:
        {chunk['Content']}
        ONLY RETURN THE TRANSFORMED TEXT REPRESENTING THE ORIGINAL TEXT — Do not include explanations, notes, or comments.

        """

        print(user_prompt)
        print("************")

        stream = client.chat.completions.create(
            model="swiss-ai/Apertus-70B",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=True,
            temperature=0,
            max_tokens=MAX_TOKEN,
        )
        full_answer = ""
        for token in stream:
            content = token.choices[0].delta.content or ""
            full_answer += content
            yield content

        past_response = full_answer
