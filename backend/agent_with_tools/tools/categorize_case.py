"""Case categorization tool."""

from backend.agent_with_tools.schemas import CategoryResult
from classifier.classifier_chain import get_classifier_chain


def categorize_case(text: str) -> CategoryResult:
    """
    Categorize a legal case into one of three categories.
    
    Args:
        text: Case description text to categorize
        
    Returns:
        CategoryResult with category and confidence score
        
    Note:
        Uses the actual classifier chain that returns traffic_law and employment_law booleans.
        Maps to: Arbeitsrecht (employment_law=True), Strafverkehrsrecht (traffic_law=True), 
        Andere (both False or ambiguous cases).
    """
    try:
        # Set the API key in the environment for the classifier
        import os
        if "APERTUS_API_KEY" in os.environ and "API_KEY" not in os.environ:
            os.environ["API_KEY"] = os.environ["APERTUS_API_KEY"]
        
        # Get the classifier chain
        classifier = get_classifier_chain()
        
        # Run classification with empty chat history
        result = classifier.invoke({"user_input": text, "chat_history": []})
        
        # Map classifier output to our schema
        traffic_law = result.get("traffic_law", False)
        employment_law = result.get("employment_law", False)
        
        # Determine category based on the boolean flags
        if employment_law and not traffic_law:
            category = "Arbeitsrecht"
            confidence = 0.85  # High confidence for single match
        elif traffic_law and not employment_law:
            category = "Strafverkehrsrecht" 
            confidence = 0.85  # High confidence for single match
        elif employment_law and traffic_law:
            # Both categories match - choose the more likely one or default to Andere
            # For now, we'll default to Andere for ambiguous cases
            category = "Andere"
            confidence = 0.60  # Lower confidence for ambiguous cases
        else:
            # Neither category matches
            category = "Andere"
            confidence = 0.70  # Medium confidence for clear non-match
            
        return CategoryResult(category=category, confidence=confidence)
        
    except Exception as e:
        # Fallback in case of classifier failure
        print(f"Classifier failed: {e}, falling back to 'Andere'")
        return CategoryResult(category="Andere", confidence=0.50)
