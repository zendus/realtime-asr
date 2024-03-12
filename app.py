import gradio as gr
import whisper
from transformers import pipeline

# Load models
model = whisper.load_model("base")
sentiment_analysis = pipeline("sentiment-analysis", framework="pt", model="SamLowe/roberta-base-go_emotions")

def analyze_sentiment(text):
    results = sentiment_analysis(text)
    sentiment_results = {result['label']: result['score'] for result in results}
    return sentiment_results

# Define sentiment emojis
def get_sentiment_emoji(sentiment):
    emoji_mapping = {
        "disappointment": "😞",
        "sadness": "😢",
        "annoyance": "😠",
        "neutral": "😐",
        "disapproval": "👎",
        "realization": "😮",
        "nervousness": "😬",
        "approval": "👍",
        "joy": "😄",
        "anger": "😡",
        "embarrassment": "😳",
        "caring": "🤗",
        "remorse": "😔",
        "disgust": "🤢",
        "grief": "😥",
        "confusion": "😕",
        "relief": "😌",
        "desire": "😍",
        "admiration": "😌",
        "optimism": "😊",
        "fear": "😨",
        "love": "❤️",
        "excitement": "🎉",
        "curiosity": "🤔",
        "amusement": "😄",
        "surprise": "😲",
        "gratitude": "🙏",
        "pride": "🦁"
    }
    return emoji_mapping.get(sentiment, "")

# Display sentiment results
def display_sentiment_results(sentiment_results, option):
    sentiment_text = ""
    for sentiment, score in sentiment_results.items():
        emoji = get_sentiment_emoji(sentiment)
        if option == "Sentiment Only":
            sentiment_text += f"{sentiment} {emoji}\n"
        elif option == "Sentiment + Score":
            sentiment_text += f"{sentiment} {emoji}: {score}\n"
    return sentiment_text

# Inference function
def inference(audio, sentiment_option):
    audio = whisper.load_audio(audio)
    audio = whisper.pad_or_trim(audio)

    mel = whisper.log_mel_spectrogram(audio).to(model.device)

    _, probs = model.detect_language(mel)
    lang = max(probs, key=probs.get)

    options = whisper.DecodingOptions(fp16=False)
    result = whisper.decode(model, mel, options)

    sentiment_results = analyze_sentiment(result.text)
    sentiment_output = display_sentiment_results(sentiment_results, sentiment_option)

    return lang.upper(), result.text, sentiment_output

# Interface settings
title = """<h1 align="center">🎤 Multilingual Automatic Speech Recognition and Sentiment Analyzer 💬</h1>"""
image_path = "thmbnail.jpg"
description = """
<br>
💻 This demo showcases a general-purpose speech recognition model called Whisper. It is trained on a large dataset of diverse audio and supports multilingual speech recognition, speech translation, and language identification tasks.<br><br>
<br>
⚙️ Components of the tool:<br>
<br>
&nbsp;&nbsp;&nbsp;&nbsp; - Real-time multilingual speech recognition<br>
&nbsp;&nbsp;&nbsp;&nbsp; - Language identification<br>
&nbsp;&nbsp;&nbsp;&nbsp; - Sentiment analysis of the transcriptions<br>
<br>
🎯 The sentiment analysis results are provided as a dictionary with different emotions and their corresponding scores.<br>
<br>
😃 The sentiment analysis results are displayed with emojis representing the corresponding sentiment.<br>
<br>
✅ The higher the score for a specific emotion, the stronger the presence of that emotion in the transcribed text.<br>
<br>
❓ Use the microphone for real-time speech recognition.<br>
<br>
⚡️ The model will transcribe the audio and perform sentiment analysis on the transcribed text.<br>
"""

custom_css = """
#banner-image {
    display: block;
    margin-left: auto;
    margin-right: auto;
}
#chat-message {
    font-size: 18px;
    min-height: 300px;
}
"""

# Define interface
iface = gr.Interface(
    inference,
    [
        gr.Audio(
            label="Input Audio",
            show_label=True,
            sources=["microphone"],
            type="filepath"
        ),
        gr.Radio(
            choices=["Sentiment Only", "Sentiment + Score"],
            label="Select an option",
            value="Sentiment Only"
        )
    ],
    [
        gr.Textbox(label="Language"),
        gr.Textbox(label="Transcription"),
        gr.Textbox(label="Sentiment Analysis Results")
    ],
    title=title,
    description=description,
    css=custom_css
)

iface.launch()
