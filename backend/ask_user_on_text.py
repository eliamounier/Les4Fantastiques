import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def generate_question(text, language):
    """
    Generate a question to test the user's understanding of the given text.

    Args:
        text (str): The text to generate a question from.
        language (str): The language in which the question should be asked.

    Returns:
        None
    """
    system_prompt = f"""
    You are a teaching assistant specialized in language comprehension. You need to test the user on their understanding of the following text. 
    Do not provide any response to the question. Only ask the question.
    """

    user_prompt = f"""
    Test me on this text with a single question.

    Here is the TEXT:
    {text}

    Please talk to me in {language}.
    """

    client = openai.OpenAI(
        api_key=os.getenv("SWISS_AI_PLATFORM_API_KEY"),
        base_url="https://api.swisscom.com/layer/swiss-ai-weeks/apertus-70b/v1"
    )

    stream = client.chat.completions.create(
        model="swiss-ai/Apertus-70B",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        stream=True
    )

    for chunk in stream:
        print(chunk.choices[0].delta.content or "", end="", flush=True)


def provide_feedback(text, question, user_response, language):
    """
    Provide feedback on the user's response to the question.

    Args:
        text (str): The original text.
        question (str): The question asked.
        user_response (str): The user's response to the question.
        language (str): The language in which the feedback should be provided.

    Returns:
        None
    """
    system_prompt = f"""
    You are a teaching assistant specialized in language comprehension. Your job is to evaluate the my response to a question based on the given text. 
    Provide constructive feedback in {language}. Be polite and helpful.
    """

    user_prompt = f"""
    Here is the TEXT:
    {text}

    Here is the QUESTION:
    {question}

    Here is the USER'S RESPONSE:
    {user_response}

    Please provide feedback on my response. Do not repeat the question. Do not over-explain.
    """

    client = openai.OpenAI(
        api_key=os.getenv("SWISS_AI_PLATFORM_API_KEY"),
        base_url="https://api.swisscom.com/layer/swiss-ai-weeks/apertus-70b/v1"
    )

    stream = client.chat.completions.create(
        model="swiss-ai/Apertus-70B",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        stream=True
    )

    feedback = ""
    for chunk in stream:
        feedback += chunk.choices[0].delta.content or ""
        print(chunk.choices[0].delta.content or "", end="", flush=True)

def main():
    TEXT = '''CHAPTER I: JONATHAN HARKER'S JOURNAL

    3 May. Bistritz.
    I left Munich at 8:35 PM on May 1st and arrived in Vienna early the next morning, but the train was an hour late. 
    I had a glimpse of Budapest from the train and the streets I walked through. It seemed like we were moving from 
    the West to the East, with the Danube River wide and deep, reminding me of the old Turkish rule.

    I stopped at the Hotel Royale in Klausenburgh for the night. I had dinner, which was a chicken dish called "paprika hendl," 
    spicy but very good. The waiter said it's a national dish and I could find it in the Carpathian region. My basic German 
    helped me a lot here.

    Before my trip, I visited the British Museum in London to learn about Transylvania. I found that the area Count Dracula 
    mentioned is in the eastern part of the country, near the borders of Transylvania, Moldavia, and Bukovina, in the Carpathian 
    mountains. It's a wild and little-known part of Europe. I couldn't find a map of the exact location of Dracula's castle, 
    but I know Bistritz, the town he mentioned, is well-known.

    I didn't sleep well, maybe because of the spicy food or the dog howling outside. In the morning, I had more paprika and a 
    maize flour porridge called "mamaliga" and eggplant stuffed with meat ("impletata"). I had to rush to catch the train to 
    Bukovina, which was supposed to leave at 8 AM but didn't start until 9:30.

    The train ride was slow and the further east we went, the less punctual the trains seemed. We passed through beautiful 
    countryside with hills, rivers, and villages. I saw different types of people, including Slovaks with big hats and wide 
    leather belts, who looked like bandits but were said to be harmless.

    At Bistritz, I stayed at the Golden Krone Hotel. The landlord seemed nervous when I asked about Count Dracula and his castle. 
    He wouldn't talk much, but gave me a letter from the Count.
    '''

    LANGUAGE_FOR_USER = "English"

    print("\nGenerating a question based on the text...\n")
    question = generate_question(TEXT, LANGUAGE_FOR_USER)

    # Simulate a user's response
    user_response = input("\nEnter your response to the question: ")

    print("\nProviding feedback on the user's response...\n")
    provide_feedback(TEXT, question, user_response, LANGUAGE_FOR_USER)

if __name__ == "__main__":
    main()