import warnings

# Suppress the "package renamed" warning aggressively
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*renamed to.*ddgs.*")

try:
    from duckduckgo_search import DDGS
except ImportError:
    try:
        from ddgs import DDGS
    except ImportError:
         DDGS = None

def search_web(query):
    if not DDGS:
        return "Search library (ddgs) not installed correctly."

    try:
        # Suppress warning locally as well just in case
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*renamed to.*ddgs.*")
            results = DDGS().text(query, max_results=3)
            
        if not results:
            return "I couldn't find anything on the web for that."
        
        summary = "Here is what I found:\n"
        for r in results:
            summary += f"- {r['title']}: {r['body']}\n({r['href']})\n\n"
        return summary
    except Exception as e:
        return f"Error searching web: {e}"

def search_news(query):
    if not DDGS:
        return "Search library (ddgs) not installed correctly."
        
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*renamed to.*ddgs.*")
            results = DDGS().news(query, max_results=3)
            
        if not results:
            return "No recent news found."
            
        summary = "Latest News:\n"
        for r in results:
            summary += f"- {r['title']} ({r['source']})\n  {r['url']}\n\n"
        return summary
    except Exception as e:
        return f"Error fetching news: {e}"
