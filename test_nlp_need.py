
from src.engine import AIEngine

def test_engine():
    engine = AIEngine()
    
    test_phrases = [
        "shutdown", # Should work
        "turn off my computer", # Might fail if strictly looking for 'shutdown'
        "boost the sound", # Might fail if looking for 'volume'
        "open calculator", # Should work
        "start calc", # Might fail if app launcher is strict
        "weather in Tokyo", # Should work
        "what's the weather like in Paris" # Should work
    ]
    
    print(f"{'Input':<30} | {'Response'}")
    print("-" * 60)
    for phrase in test_phrases:
        response = engine.process_input(phrase)
        # Truncate response
        resp_str = str(response)[:40] + "..." if len(str(response)) > 40 else str(response)
        print(f"{phrase:<30} | {resp_str}")

if __name__ == "__main__":
    test_engine()
