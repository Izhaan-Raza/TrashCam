from flask import Flask, render_template, request, jsonify
import os
import requests
import base64

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set your Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyB87_Q9Trctn9TTVkkyKGy-ImYzZx7R7pU")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"

# Function to send image to Gemini API
def classify_waste(image_path):
    with open(image_path, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

    prompt_text = "Analyze the image as an waste and suggest if it should be disposed in the trash can if yes which colour trash can, dry, wet and all according to the quality of the waste; secondally if it is a home recylable waste suggest a DIY project. So your must be having be having 1st line: What type of waste is this, 2nd line: Homerecylable or not if yes suggest how and if not which tash can it is suitable for.. DO NOT ADD ANY OTHER LINES THAN THIS. WORK AS A WASTE SEGREGATION CHATBOT.. Answer in bullet points."

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt_text},
                {"inlineData": {"mimeType": "image/jpeg", "data": image_base64}}
            ]
        }]
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": "Failed to get response from Gemini API",
            "status_code": response.status_code,
            "response": response.text
        }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded"})

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"})

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    result = classify_waste(file_path)

    # Extract the message from the Gemini response
    if "candidates" in result and result["candidates"]:
        message = result["candidates"][0]["content"]["parts"][0]["text"]
    else:
        message = "Could not generate a response."

    return jsonify({"message": message})

if __name__ == '__main__':
    app.run(debug=True)
