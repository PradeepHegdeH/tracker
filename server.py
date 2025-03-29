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
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

@app.route('/models', methods=['GET'])
def list_models():
    try:
        models = genai.list_models()
        return jsonify({'models': [model.name for model in models]})
    except Exception as e:
        return jsonify({'error': f'Error listing models: {str(e)}'}), 500

def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        if not text.strip():
            raise ValueError("No text content found on the webpage")
        
        return text[:10000]  # Limit text length to avoid token limits
    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch webpage: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error processing webpage: {str(e)}")

@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
        
        url = data.get('url')
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Extract text from webpage
        try:
            text = extract_text_from_url(url)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
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
        try:
            response = model.generate_content(prompt)
            summary = response.text
            if not summary:
                raise ValueError("Failed to generate summary")
            return jsonify({'summary': summary})
        except Exception as e:
            return jsonify({'error': f'Error generating summary: {str(e)}'}), 500
    
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

if __name__ == '__main__':
    print("Starting Flask server on http://localhost:5000")
    app.run(port=5000, debug=True) 