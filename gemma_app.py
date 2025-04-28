from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import json
import sys

# We need to handle the import error for gemma_scorer if the dependencies are not installed
try:
    from gemma_scorer import GemmaEssayScorer
    have_gemma_scorer = True
except ImportError:
    print("Could not import GemmaEssayScorer - will use simplified scoring")
    have_gemma_scorer = False

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Define a simple scorer function to use if gemma_scorer is not available
def simple_score_essay(essay_text):
    word_count = len(essay_text.split())
    sentences = [s.strip() for s in essay_text.split('.') if s.strip()]
    sentence_count = len(sentences)
    
    # Simple scoring logic
    coherence_score = min(10, max(1, 5 + (1 if word_count > 200 else 0)))
    grammar_score = min(10, max(1, 5 + (1 if sentence_count > 10 else 0)))
    content_score = min(10, max(1, word_count // 50))
    evidence_score = min(10, max(1, word_count // 75))
    
    overall_score = round((coherence_score + grammar_score + content_score + evidence_score) / 4)
    
    return {
        "coherence_score": coherence_score,
        "grammar_score": grammar_score,
        "content_score": content_score,
        "evidence_score": evidence_score,
        "overall_score": overall_score,
        "scoring_method": "basic",
        "feedback": {
            "coherence": f"Your essay has approximately {sentence_count} sentences. Consider focusing on logical structure and flow.",
            "grammar": "The essay might benefit from a review for grammar and punctuation.",
            "content": f"Your essay contains {word_count} words. Consider adding more detailed arguments for a higher score.",
            "evidence": "Try to include specific examples and references to support your points."
        },
        "summary": f"This {word_count}-word essay demonstrates basic writing skills. Focus on improving organization and evidence for a better score."
    }

# Get API key from environment variable first, fallback to hardcoded key for local testing
api_key = os.environ.get("OPENROUTER_API_KEY")
if not api_key:
    # Fallback for local development only
    api_key = "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"
    print("Warning: Using hardcoded API key. Set OPENROUTER_API_KEY environment variable for production.")

# Initialize the scorer if available
if have_gemma_scorer:
    scorer = GemmaEssayScorer(api_key)
else:
    scorer = None

@app.route('/')
def home():
    """Serve the home page with the essay submission form."""
    return render_template('index.html')

@app.route('/api/score', methods=['POST'])
def score_essay():
    """API endpoint to score an essay."""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'error': 'Missing essay text',
                'message': 'Please provide an essay in the "text" field.'
            }), 400
            
        essay_text = data['text']
        
        if len(essay_text) < 50:
            return jsonify({
                'error': 'Essay too short',
                'message': 'Please provide an essay with at least 50 characters.'
            }), 400
            
        # If we don't have the required dependencies, use simple scoring
        if not have_gemma_scorer:
            print("Using simplified scoring due to missing dependencies")
            result = simple_score_essay(essay_text)
            return jsonify(result), 200
        
        # Otherwise try online scoring with API    
        try:
            print(f"Processing essay with {len(essay_text)} characters")
            if api_key:
                print(f"Using API key: {api_key[:8]}...{api_key[-4:]}")
                result = scorer.score_essay(essay_text)
                # Check if there was an API error
                if "error" in result:
                    print(f"API returned error: {result['error']}")
                    print("Falling back to offline scoring")
                    result = scorer.score_essay_offline(essay_text)
                    # For UI, we'll call this "basic model" instead of "offline"
                    result['scoring_method'] = 'basic'
                    # Store but don't expose the API error
                    result['_api_error'] = result.get('error', 'Unknown API error')
                    # Remove the 'error' key so it doesn't show in the UI
                    if 'error' in result:
                        del result['error']
                else:
                    print("Successful API scoring")
                    # Rename to hide the actual model
                    result['scoring_method'] = 'advanced'
            else:
                print("No API key available - using offline scoring")
                # No API key, use offline scoring
                result = scorer.score_essay_offline(essay_text)
                result['scoring_method'] = 'basic'
                
            # Clean up any raw responses that might reveal the model
            if 'raw_response' in result:
                del result['raw_response']
                
            return jsonify(result), 200
            
        except Exception as e:
            # If online scoring fails, fall back to offline
            print(f"Exception in scoring: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # If offline scoring is available, use it
            if hasattr(scorer, 'score_essay_offline'):
                result = scorer.score_essay_offline(essay_text)
            else:
                # Otherwise use our simple scorer
                result = simple_score_essay(essay_text)
                
            result['scoring_method'] = 'basic'
            # Store but don't expose the API error
            result['_api_error'] = str(e)
            return jsonify(result), 200
            
    except Exception as e:
        print(f"Server error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Server error',
            'message': f'An unexpected error occurred: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'api_connected': api_key is not None,
        'advanced_scoring': have_gemma_scorer,
        'version': '1.0.0'
    })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Check if we're missing the API key
    if not api_key:
        print("\n" + "="*80)
        print("Warning: No OpenRouter API key found. The application will use offline scoring only.")
        print("To use Gemma 3 for more accurate scoring, please:")
        print("1. Get a free API key from https://openrouter.ai/keys")
        print("2. Set it as an environment variable: export OPENROUTER_API_KEY=your_key_here")
        print("="*80 + "\n")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port) 