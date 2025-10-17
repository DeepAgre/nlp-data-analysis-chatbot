# chatbot_core.py
from textblob import TextBlob
from transformers import pipeline
import requests
import warnings
warnings.filterwarnings('ignore')

class NLPProcessor:
    def __init__(self):
        # Use a smaller and faster model for summarization
        print("Loading lightweight summarization model...")
        self.summarizer = pipeline("summarization", 
                                 model="sshleifer/distilbart-cnn-12-6", 
                                 truncation=True)
        print("Model loaded successfully!")
    
    def get_supported_languages(self):
        """Return supported language codes and examples"""
        return {
            "popular_languages": {
                "es": "Spanish",
                "fr": "French", 
                "de": "German",
                "it": "Italian",
                "pt": "Portuguese",
                "ru": "Russian",
                "zh": "Chinese",
                "ja": "Japanese",
                "ko": "Korean",
                "ar": "Arabic",
                "hi": "Hindi",
                "ur": "Urdu",
                "bn": "Bengali",
                "ta": "Tamil",
                "te": "Telugu",
                "nl": "Dutch",
                "el": "Greek",
                "he": "Hebrew",
                "sv": "Swedish",
                "pl": "Polish",
                "tr": "Turkish"
            },
            "example_usage": "translate to es: Hello world",
            "full_list_link": "https://www.science.co.il/language/Codes.php"
        }
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of the text"""
        try:
            analysis = TextBlob(text)
            polarity = analysis.sentiment.polarity
            
            if polarity > 0.1:
                return {"sentiment": "Positive 😊", "score": float(polarity)}
            elif polarity < -0.1:
                return {"sentiment": "Negative 😞", "score": float(polarity)}
            else:
                return {"sentiment": "Neutral 😐", "score": float(polarity)}
        except Exception as e:
            return {"error": f"Sentiment analysis failed: {str(e)}"}
    
    def translate_text(self, text, to_lang='en'):
        """Translate text to specified language using a simple API fallback"""
        try:
            # Simple translation using a free API (MyMemory API)
            if to_lang == 'en':
                return {"translated_text": text, "language": to_lang}  # No translation needed
                
            api_url = f"https://api.mymemory.translated.net/get?q={text}&langpair=en|{to_lang}"
            response = requests.get(api_url)
            
            if response.status_code == 200:
                data = response.json()
                if data['responseStatus'] == 200:
                    translated_text = data['responseData']['translatedText']
                    return {"translated_text": translated_text, "language": to_lang}
                else:
                    # Fallback to TextBlob if API fails
                    blob = TextBlob(text)
                    translated = blob.translate(to=to_lang)
                    return {"translated_text": str(translated), "language": to_lang}
            else:
                return {"error": "Translation service unavailable. Please try again later."}
                
        except Exception as e:
            supported_langs = self.get_supported_languages()['popular_languages']
            lang_examples = ", ".join([f"{code} ({name})" for code, name in list(supported_langs.items())[:5]])
            return {"error": f"Translation failed. Supported examples: {lang_examples}. Type 'languages' for full list."}
    
    def summarize_text(self, text, max_length=150, min_length=50):
        """Summarize the given text"""
        try:
            # Handle long texts by truncating (for demo purposes)
            if len(text) > 1024:
                text = text[:1000] + "... [text truncated for demo]"
            
            summary = self.summarizer(text, 
                                    max_length=max_length, 
                                    min_length=min_length, 
                                    do_sample=False)
            return {"summary": summary[0]['summary_text']}
        except Exception as e:
            return {"error": f"Summarization failed: {str(e)}"}
    
    def process_command(self, user_input):
        """Main method to process user input and determine action"""
        user_input = user_input.strip()
        
        # Language support command
        if user_input.lower() in ['languages', 'lang', 'language codes', 'supported languages']:
            return {
                "languages": True,
                "supported_languages": self.get_supported_languages()['popular_languages'],
                "example": self.get_supported_languages()['example_usage'],
                "reference": self.get_supported_languages()['full_list_link']
            }
        
        # Translation command: translate to fr: Hello world
        if user_input.lower().startswith('translate to '):
            parts = user_input.split(':', 1)
            if len(parts) == 2:
                lang_part = parts[0].replace('translate to ', '').replace('Translate to ', '').strip()
                text_to_translate = parts[1].strip()
                
                # Validate language code format
                if len(lang_part) != 2:
                    return {"error": "Please use 2-letter language codes (e.g., 'es', 'fr', 'hi'). Type 'languages' for supported codes."}
                    
                return self.translate_text(text_to_translate, lang_part)
            
            return {"error": "Please use format: 'translate to fr: Your text here'. Type 'languages' for supported codes."}
        
        # Sentiment analysis command
        elif user_input.lower().startswith('analyze sentiment:'):
            text = user_input.replace('analyze sentiment:', '').replace('Analyze sentiment:', '').strip()
            if text:
                return self.analyze_sentiment(text)
            return {"error": "Please provide text to analyze. Example: 'analyze sentiment: I love this!'"}
        
        # Summarization command
        elif user_input.lower().startswith('summarize:'):
            text = user_input.replace('summarize:', '').replace('Summarize:', '').strip()
            if text:
                return self.summarize_text(text)
            return {"error": "Please provide text to summarize. Example: 'summarize: Your long text here'"}
        
        # Help command
        elif user_input.lower() in ['help', '?', 'commands']:
            return {
                "help": True,
                "commands": {
                    "Translation": "translate to fr: Your text here",
                    "Sentiment Analysis": "analyze sentiment: Your text here",
                    "Summarization": "summarize: Your long text here",
                    "Language Codes": "languages (shows supported languages)"
                }
            }
        
        # Default response
        else:
            return {
                "response": "I can help with translation, sentiment analysis, and summarization!",
                "suggestion": "Type 'help' to see available commands or 'languages' for translation codes."
            }

# Create a global instance
nlp_processor = NLPProcessor()