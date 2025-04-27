import os
import requests
import json
from typing import Dict, Any, List, Optional

class GemmaEssayScorer:
    """Essay scoring system using Gemma 3's natural language understanding capabilities.
    
    This implementation uses the free OpenRouter API to access Google's Gemma 3 model.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the GemmaEssayScorer.
        
        Args:
            api_key: OpenRouter API key (optional, will use environment variable if not provided)
        """
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            print("Warning: No API key provided. Please set OPENROUTER_API_KEY environment variable or provide a key.")
        else:
            print(f"API key configured: {self.api_key[:8]}...{self.api_key[-4:]}")
            
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "google/gemma-3-27b-it"  # Using Gemma 3 model (fixed format)
        
    def _create_scoring_prompt(self, essay_text: str) -> List[Dict[str, Any]]:
        """Create a well-structured prompt for essay scoring.
        
        Args:
            essay_text: The essay text to be scored
            
        Returns:
            List of message dictionaries for the API
        """
        system_prompt = """You are an expert essay grader with years of experience in evaluating student essays. 
Your task is to grade the provided essay on a scale of 1-10 based on these criteria:

1. Coherence and Organization (structure, flow, logical progression)
2. Grammar and Language (spelling, sentence structure, word choice)
3. Content Quality (depth of analysis, relevance, originality)
4. Evidence and Support (use of examples, reasoning)

You MUST provide your response in valid JSON format with the EXACT following structure. Do not include any explanations outside the JSON:

{
  "coherence_score": <number between 1 and 10>,
  "grammar_score": <number between 1 and 10>,
  "content_score": <number between 1 and 10>,
  "evidence_score": <number between 1 and 10>,
  "overall_score": <number between 1 and 10>,
  "feedback": {
    "coherence": "<specific feedback on coherence>",
    "grammar": "<specific feedback on grammar>",
    "content": "<specific feedback on content>",
    "evidence": "<specific feedback on evidence>"
  },
  "summary": "<brief overall assessment, 1-2 sentences>"
}
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Please evaluate this essay according to the criteria and format specified in the system message:\n\n{essay_text}"}
        ]
        
        return messages
    
    def score_essay(self, essay_text: str) -> Dict[str, Any]:
        """Score an essay using the Gemma 3 model.
        
        Args:
            essay_text: The essay text to be scored
            
        Returns:
            Dictionary containing scores and feedback
        """
        if not self.api_key:
            print("Error: Missing API key")
            return {
                "error": "No API key provided",
                "overall_score": 5,  # Default fallback score
                "summary": "Unable to score essay: No API key provided"
            }
            
        messages = self._create_scoring_prompt(essay_text)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "automatic-essay-scoring.example.com",  # Simplified domain
            "X-Title": "Automatic Essay Scoring"  # Your app's name
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,  # Low temperature for more consistent scoring
            "max_tokens": 1000,
            "response_format": {"type": "json_object"}  # Request JSON formatted response
        }
        
        try:
            print(f"Sending request to {self.api_url} with model {self.model}")
            response = requests.post(self.api_url, headers=headers, data=json.dumps(data))
            
            print(f"Response status code: {response.status_code}")
            if response.status_code != 200:
                print(f"Error response: {response.text}")
                
            response.raise_for_status()
            
            response_data = response.json()
            print(f"Response data keys: {response_data.keys()}")
            
            model_response = response_data["choices"][0]["message"]["content"]
            print(f"Response content preview: {model_response[:100]}...")
            
            # Extract JSON from the response
            try:
                score_data = json.loads(model_response)
                print("Successfully parsed JSON response")
                return score_data
            except json.JSONDecodeError as e:
                # If the model doesn't return valid JSON, try to extract the scores manually
                print(f"JSON decode error: {str(e)}")
                print(f"Raw response: {model_response}")
                return {
                    "error": "Invalid JSON response from model",
                    "raw_response": model_response,
                    "overall_score": 5  # Default fallback score
                }
                
        except requests.exceptions.RequestException as e:
            print(f"Request exception: {str(e)}")
            return {
                "error": f"API request error: {str(e)}",
                "overall_score": 5  # Default fallback score
            }
    
    def score_essay_offline(self, essay_text: str) -> Dict[str, Any]:
        """Score an essay using simple heuristics when API is unavailable.
        
        Args:
            essay_text: The essay text to be scored
            
        Returns:
            Dictionary containing scores and feedback
        """
        # Simple heuristic-based scoring as a fallback
        word_count = len(essay_text.split())
        sentence_count = len([s for s in essay_text.split('.') if s.strip()])
        avg_words_per_sentence = word_count / max(sentence_count, 1)
        
        # Check for basic grammar markers
        grammar_issues = 0
        for marker in [". ,", "  ", " .", " ,", ",,", "!!"]:
            if marker in essay_text:
                grammar_issues += 1
        
        # Count paragraphs as a measure of structure
        paragraphs = len([p for p in essay_text.split('\n\n') if p.strip()])
        paragraphs = max(1, paragraphs)
        
        # Very basic scoring heuristics
        coherence_score = min(10, max(1, int((avg_words_per_sentence / 5) + (paragraphs / 2))))
        grammar_score = min(10, max(1, 7 - grammar_issues + (1 if word_count > 300 else 0)))
        content_score = min(10, max(1, word_count // 75))
        evidence_score = min(10, max(1, word_count // 100))
        
        overall_score = round((coherence_score + grammar_score + content_score + evidence_score) / 4)
        
        return {
            "coherence_score": coherence_score,
            "grammar_score": grammar_score,
            "content_score": content_score,
            "evidence_score": evidence_score,
            "overall_score": overall_score,
            "feedback": {
                "coherence": f"Your essay has {paragraphs} paragraphs and an average of {round(avg_words_per_sentence, 1)} words per sentence. Consider organizing your ideas into clearly defined paragraphs with topic sentences for better structure.",
                "grammar": f"The essay contains some grammatical elements that could be improved. Pay attention to punctuation and sentence structure to enhance readability.",
                "content": f"Your essay contains {word_count} words. To improve content depth, consider adding more specific examples and developing your arguments with greater detail.",
                "evidence": "Consider incorporating more specific evidence to support your main points. Strong essays use concrete examples and references to strengthen arguments."
            },
            "summary": f"This {word_count}-word essay demonstrates {['limited', 'basic', 'good', 'strong'][min(3, overall_score//3)]} writing skills. Focus on improving organization, grammar, and supporting evidence for a better score."
        }


# Example usage
if __name__ == "__main__":
    scorer = GemmaEssayScorer()
    
    sample_essay = """
    The impact of artificial intelligence on society is profound and multifaceted. 
    AI technologies are transforming industries, from healthcare to transportation, 
    and changing how we work and live. While these advancements offer tremendous 
    benefits, including increased efficiency and new capabilities, they also present 
    significant challenges related to privacy, employment, and ethics.
    
    In healthcare, AI systems can analyze medical images and patient data to identify 
    patterns that humans might miss, potentially leading to earlier diagnosis and more 
    effective treatments. Similarly, in transportation, autonomous vehicles promise to 
    reduce accidents and improve mobility for those unable to drive.
    
    However, concerns about job displacement are valid as automation continues to advance. 
    Additionally, the collection of vast amounts of data raises serious privacy concerns, 
    and the potential for algorithmic bias could perpetuate or even amplify social inequities.
    
    Society must navigate these complex issues through thoughtful policy, education, and 
    a commitment to ethical development of AI technologies. By proactively addressing 
    challenges while embracing the benefits, we can shape an AI-enabled future that 
    enhances human welfare and upholds our core values.
    """
    
    # Try to use the API first, fall back to offline scoring if unavailable
    try:
        result = scorer.score_essay(sample_essay)
        if "error" in result:
            print("Falling back to offline scoring...")
            result = scorer.score_essay_offline(sample_essay)
    except Exception as e:
        print(f"Error using API: {e}")
        print("Falling back to offline scoring...")
        result = scorer.score_essay_offline(sample_essay)
    
    print(json.dumps(result, indent=2)) 