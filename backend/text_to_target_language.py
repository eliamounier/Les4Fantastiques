import os
import openai

def translate_text(text, target_language):
    """
    Translate the given text into the target language using the LLM.

    Args:
        text (str): The text to translate.
        target_language (str): The target language for translation.

    Returns:
        None
    """
    system_prompt = """
    You are a translator that translates faithfully with no creation, hallucination, or new content in the response text.
    """
    user_prompt = f"""
    TRANSLATE THIS: {text} in {target_language}
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
    NEW_LANGUAGE = "French"

    translate_text(TEXT, NEW_LANGUAGE)

if __name__ == "__main__":
    main()