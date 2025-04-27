# Gemma 3-Powered Automatic Essay Scoring System

This project provides an automatic essay scoring system powered by Google's Gemma 3 language model. It includes both API-based scoring using Gemma 3 via OpenRouter's free API, as well as a fallback offline scoring system.

## Features

- Score essays based on multiple criteria:
  - Coherence and Organization
  - Grammar and Language
  - Content Quality
  - Evidence and Support
- Detailed feedback for each criterion
- Summary assessment of the overall essay quality
- Attractive web interface for submitting essays and viewing results
- Fallback offline scoring when the API is unavailable

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get an API Key (Optional, but Recommended)

For more accurate scoring using Gemma 3, you'll need an API key from OpenRouter:

1. Visit [OpenRouter](https://openrouter.ai/keys) and sign up for a free account
2. Generate an API key
3. Set the API key as an environment variable:

```bash
# On Windows
set OPENROUTER_API_KEY=your_api_key_here

# On Linux/macOS
export OPENROUTER_API_KEY=your_api_key_here
```

### 3. Run the Application

```bash
python gemma_app.py
```

The application will be available at http://localhost:5000.

## Usage

1. Open your web browser and navigate to http://localhost:5000
2. Enter or paste an essay into the text area (minimum 50 characters)
3. Click "Score My Essay"
4. View the detailed assessment and feedback for your essay

## About the Scoring System

### Online Scoring with Gemma 3

When an API key is provided, the system uses Google's Gemma 3 model via OpenRouter's API to perform a sophisticated analysis of your essay, providing detailed feedback on multiple criteria.

### Offline Scoring

If no API key is provided or if the API request fails, the system falls back to a simple heuristic-based scoring method that evaluates basic aspects like word count and sentence length.

## Technical Details

- **Frontend**: HTML, CSS, JavaScript with Bootstrap 5
- **Backend**: Flask (Python)
- **AI Model**: Gemma 3 (27B parameters) via OpenRouter API
- **Fallback**: Rule-based scoring algorithm

## File Structure

- `gemma_scorer.py`: Core scoring functionality
- `gemma_app.py`: Flask application
- `templates/index.html`: Frontend user interface
- `requirements.txt`: Required Python packages

## Limitations

- The offline scoring is significantly less accurate than the Gemma 3-based scoring
- API requests may take several seconds to complete, especially for longer essays
- The system may not work perfectly for all types of essays or writing styles

## How to Get Help

If you encounter any issues or have questions, please:

1. Check that you've properly set up the API key (if using online scoring)
2. Verify that all dependencies are correctly installed
3. Check the console for any error messages

## License

This project is open source and available for educational and non-commercial use.

## Acknowledgments

- Google for developing the Gemma 3 model
- OpenRouter for providing free API access to Gemma 3 