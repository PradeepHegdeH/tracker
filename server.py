from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def extract_text_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:10000]  # Limit text length to avoid token limits
    except Exception as e:
        return str(e)

@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        data = request.json
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Extract text from webpage
        text = extract_text_from_url(url)
        
        # Generate prompt for summarization
        prompt = f"""Please provide a concise summary of the following webpage content. 
        Focus on the main points and key takeaways:

        {text}

        Please format the summary in the following structure:
        1. Main Topic
        2. Key Points (3-5 bullet points)
        3. Brief Summary (2-3 sentences)
        """
        
        # Generate summary using Gemini
        response = model.generate_content(prompt)
        summary = response.text
        
        return jsonify({'summary': summary})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000) 