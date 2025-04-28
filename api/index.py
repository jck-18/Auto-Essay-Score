from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import sys
import logging
import traceback
from dotenv import load_dotenv
import json

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the scorer
from gemma_scorer import GemmaEssayScorer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Get API key from environment variable
api_key = os.environ.get("OPENROUTER_API_KEY")

# Initialize scorer
scorer = GemmaEssayScorer(api_key=api_key)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/score', methods=['POST'])
def score_essay():
    try:
        data = request.get_json()
        essay_text = data.get('essay_text', '')
        scoring_method = data.get('scoring_method', 'online')
        
        logger.info(f"Received essay with length: {len(essay_text)}")
        logger.info(f"Using scoring method: {scoring_method}")
        
        # Validate input
        if not essay_text:
            logger.warning("Missing essay text in request")
            return jsonify({
                "error": "Missing essay text. Please submit an essay to score."
            }), 400
            
        if len(essay_text.split()) < 5:
            logger.warning(f"Essay too short: {len(essay_text.split())} words")
            return jsonify({
                "error": "Essay is too short for evaluation. Please submit a longer essay."
            }), 400
        
        # Score the essay
        if scoring_method == 'online':
            try:
                result = scorer.score_essay_online(essay_text)
                return jsonify(result)
            except Exception as e:
                logger.error(f"Error in online scoring: {str(e)}")
                logger.error(traceback.format_exc())
                # Fallback to offline scoring
                logger.info("Falling back to offline scoring")
                result = scorer.score_essay_offline(essay_text)
                result["note"] = "Scored using our local model due to API limitations."
                return jsonify(result)
        else:
            result = scorer.score_essay_offline(essay_text)
            return jsonify(result)
            
    except Exception as e:
        logger.error(f"Error in score_essay: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "An error occurred while scoring your essay. Please try again later."
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "api_key_configured": bool(api_key)}), 200

# Configuration for Flask app
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Set the path to serve static files
app.static_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')

# For local development
if __name__ == '__main__':
    app.run(debug=True) 