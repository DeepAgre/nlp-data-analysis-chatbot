# app.py
from flask import Flask, render_template, request, jsonify
from chatbot_core import nlp_processor
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    """Render the main chat interface"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages from the frontend"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message received'})
        
        # Process the user's message
        result = nlp_processor.process_command(user_message)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'})

@app.route('/health')
def health_check():
    """Health check endpoint for deployment"""
    return jsonify({'status': 'healthy', 'model': 'loaded'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)