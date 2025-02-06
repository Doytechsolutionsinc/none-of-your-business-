from flask import Flask, render_template, request, jsonify, redirect
import openai
import requests
from io import BytesIO
from PIL import Image
import base64
import os
import pyttsx3
import speech_recognition as sr

app = Flask(__name__)

# Set your OpenAI API key
openai.api_key = "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"

# Initialize TTS engine
engine = pyttsx3.init()

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Custom response for "Who made you?"
CUSTOM_RESPONSE = "I was created by Doy Tech Solutions Inc, a Ghanaian company that specializes in software and bot development."

@app.route("/")
def home():
    return redirect("/loading")

@app.route("/loading")
def loading():
    return render_template("loading.html")

@app.route("/main")
def main():
    return render_template("index.html")

@app.route("/send_message", methods=["POST"])
def send_message():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    # Custom response for "Who made you?"
    if "who made you" in user_input.lower():
        return jsonify({"response": CUSTOM_RESPONSE})

    # Check for TTS commands
    tts_commands = ["sing a song", "tell a rhyme", "tell a story"]
    if any(cmd in user_input.lower() for cmd in tts_commands):
        return handle_tts(user_input)

    # Get MetroTex AI response
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are MetroTex AI, a helpful assistant."},
                {"role": "user", "content": user_input}
            ]
        )
        chatbot_response = response['choices'][0]['message']['content']
        return jsonify({"response": chatbot_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/create_image", methods=["POST"])
def create_image():
    prompt = request.json.get("prompt")
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    try:
        # Generate image using DALL·E
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"
        )
        image_url = response['data'][0]['url']

        # Download and display the image
        image_data = requests.get(image_url).content
        image = Image.open(BytesIO(image_data))
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return jsonify({"image": img_str})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def handle_tts(user_input):
    try:
        # Generate a response using GPT
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are MetroTex AI, a helpful assistant."},
                {"role": "user", "content": user_input}
            ]
        )
        chatbot_response = response['choices'][0]['message']['content']

        # Convert response to speech
        engine.say(chatbot_response)
        engine.runAndWait()

        return jsonify({"response": chatbot_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)