
from src.engine import AIEngine
from src.simple_nlp import SimpleIntentClassifier

def test_nlp_integration():
    classifier = SimpleIntentClassifier()
    
    test_phrases = [
        "turn off my computer", # Traditionally failed
        "can you make it louder", # Traditionally failed
        "shutdown",
        "too loud in here",
        "weather in Tokyo" # Mixed bag
    ]
    
    print(f"{'Input':<30} | {'Predicted Intent':<20} | {'Score'}")
    print("-" * 65)
    
    for phrase in test_phrases:
        intent, score = classifier.predict(phrase)
        print(f"{phrase:<30} | {str(intent):<20} | {score:.2f}")

if __name__ == "__main__":
    test_nlp_integration()
