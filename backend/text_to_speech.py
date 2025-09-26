from gtts import gTTS


def text_to_audio(text, language, output_file):

        audio = gTTS(text=text, lang=language, slow=False)
        audio.save(output_file)
        print(f"✅ Audio file saved as {output_file}")
        

if __name__ == "__main__":

    text = """
    CHAPTER I: JONATHAN HARKER'S JOURNAL

    3 May. Bistritz.
    I left Munich at 8:35 PM on May 1st and arrived in Vienna early the next morning, but the train was an hour late. 
    I had a glimpse of Budapest from the train and the streets I walked through. It seemed like we were moving from 
    the West to the East, with the Danube River wide and deep, reminding me of the old Turkish rule.
    """
    language = "en"  # Change to 'fr' for French, 'it' for Italian, etc.
    output_file = "audiobook_chapter1.mp3"
    
    text_to_audio(text, language, output_file)