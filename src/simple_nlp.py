import re
import math
from collections import Counter

class SimpleIntentClassifier:
    def __init__(self):
        # Define intents and their training phrases
        self.intents = {
            "system.shutdown": [
                "shutdown", "turn off computer", "power off", "kill system", "shut down pc", "turn off pc"
            ],
            "system.restart": [
                "restart", "reboot", "restart computer", "restart pc"
            ],
            "system.lock": [
                "lock screen", "lock pc", "lock computer", "secure output"
            ],
            "volume.set": [ # For specific directed commands, regex is still good, but this helps catch generic ones
                "change volume", "set volume", "adjust sound", "audio level"
            ],
            "volume.up": [
                "volume up", "louder", "boost sound", "increase volume", "turn up", "can't hear"
            ],
            "volume.down": [
                "volume down", "quieter", "lower sound", "decrease volume", "turn down", "too loud"
            ],
            "app.open": [
                "open app", "launch", "start program", "run application"
            ],
            "weather.check": [
                "check weather", "how is the weather", "weather report", "is it raining"
            ]
        }
        self.vocabulary = set()
        self._build_vocabulary()

    def _build_vocabulary(self):
        for phrases in self.intents.values():
            for phrase in phrases:
                words = self._tokenize(phrase)
                self.vocabulary.update(words)

    def _tokenize(self, text):
        # Simple regex tokenizer
        text = text.lower()
        return re.findall(r'\b\w+\b', text)

    def _get_vector(self, text):
        words = self._tokenize(text)
        word_counts = Counter(words)
        vector = {word: word_counts[word] for word in words if word in self.vocabulary}
        return vector

    def _cosine_similarity(self, vec1, vec2):
        if not vec1 or not vec2:
            return 0.0
        
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum(vec1[x] * vec2[x] for x in intersection)
        
        sum1 = sum(vec1[x]**2 for x in vec1)
        sum2 = sum(vec2[x]**2 for x in vec2)
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        
        if not denominator:
            return 0.0
        return numerator / denominator

    def predict(self, text):
        input_vec = self._get_vector(text)
        best_intent = None
        max_score = 0.0
        
        # Compare against all training phrases (Nearest Neighbor)
        for intent, phrases in self.intents.items():
            for phrase in phrases:
                phrase_vec = self._get_vector(phrase)
                score = self._cosine_similarity(input_vec, phrase_vec)
                if score > max_score:
                    max_score = score
                    best_intent = intent
        
        # Threshold to avoid random matches
        if max_score < 0.3:
            return None, 0.0
            
        return best_intent, max_score
