import yt_dlp
import webbrowser
import re
import urllib.parse
import threading
import json
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup

class MusicSkill:
    def __init__(self):
        self.queue = [] # List of tuples (type, id/url, title)
        self.mode = "Spotify" # Default mode
        self.ydl_opts = {
            'quiet': True,
            'format': 'bestaudio/best',
            'noplaylist': True,
            'extract_flat': True,
        }
        # Use absolute path for history file to avoid CWD issues
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.history_file = os.path.join(base_dir, "music_history.json")
        self.history = self._load_history()

    def _load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading history: {e}")
                return []
        return []

    def _save_history(self):
        try:
            with open(self.history_file, "w") as f:
                json.dump(self.history, f, indent=4)
        except Exception as e:
            print(f"Error saving history: {e}")

    def _add_to_history(self, type, id, title):
        # Check if already at the top to avoid immediate duplicates
        if self.history and self.history[0].get('id') == id:
             return
        
        entry = {
            "type": type,
            "id": id,
            "title": title,
            "timestamp": datetime.now().isoformat()
        }
        self.history.insert(0, entry)
        self.history = self.history[:50] # Limit to 50 items
        self._save_history()

    def get_history(self):
        return self.history

    def set_mode(self, mode):
        if mode in ["Spotify", "YouTube"]:
            self.mode = mode
            return f"Music source switched to {mode}."
        return "Invalid mode."

    def _get_video_info(self, query):
        """
        Returns (id, title) for a query or link using yt-dlp.
        """
        try:
            # If it's not a link, make it a search query
            if not query.startswith("http"):
                query = f"ytsearch1:{query}"
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(query, download=False)
                
                if 'entries' in info:
                    if len(info['entries']) > 0:
                        video = info['entries'][0]
                        return video['id'], video['title']
                else:
                    return info['id'], info['title']
                    
        except Exception as e:
            print(f"Error extracting video info: {e}")
            return None, None
        return None, None

    def _clean_spotify_query(self, query):
        return re.sub(r'on spotify', '', query, flags=re.IGNORECASE).replace("spotify", "").strip()

    def play_now(self, query):
        """
        Plays immediately based on current mode.
        """
        # Always handle direct links appropriately regardless of mode
        if "open.spotify.com" in query:
             title = "Spotify Link"
             
             # Attempt to fetch metadata
             try:
                 headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                 response = requests.get(query, headers=headers, timeout=3)
                 if response.status_code == 200:
                     soup = BeautifulSoup(response.text, 'html.parser')
                     
                     # Try OpenGraph title first (usually cleanest)
                     og_title = soup.find("meta", property="og:title")
                     og_desc = soup.find("meta", property="og:description")
                     
                     if og_title:
                         content = og_title.get("content", "")
                         # Basic cleanup if needed
                         title = content
                         
                         # If it's a song, og:title is usually just the song name
                         # og:description usually contains the artist: "Artist · Song · 202X"
                         if og_desc:
                             desc = og_desc.get("content", "")
                             # simple heuristic: if description starts with something that isn't the song name
                             parts = desc.split(" · ")
                             if len(parts) > 0:
                                 artist = parts[0]
                                 title = f"{title} - {artist}"
                     else:
                         # Fallback to page title
                         web_title = soup.title.string if soup.title else ""
                         if web_title:
                             title = web_title.replace(" | Spotify", "")
             except Exception as e:
                 print(f"Error fetching Spotify metadata: {e}")
                 # Fallback to simple regex parsing if request fails
                 match = re.search(r'open\.spotify\.com/(track|album|playlist)/([a-zA-Z0-9]+)', query)
                 if match:
                     type_ = match.group(1).capitalize()
                     title = f"Spotify {type_}"
                 
             self._add_to_history("spotify", query, title)
             webbrowser.open(query)
             return f"Opening: {title}"

        if "youtube.com" in query or "youtu.be" in query:
             # Try to extract detailed info for history if possible, else just link
             vid_id, title = self._get_video_info(query)
             if vid_id:
                  self._add_to_history("youtube", vid_id, title)
             else:
                  self._add_to_history("youtube", query, "YouTube Link")
             
             webbrowser.open(query)
             return f"Opening YouTube Link..."

        if self.mode == "Spotify":
            clean = self._clean_spotify_query(query)
            encoded = urllib.parse.quote(clean)
            uri = f"spotify:search:{encoded}"
            
            # Save to history so user can re-search easily
            self._add_to_history("spotify", uri, clean.title())
            
            webbrowser.open(uri)
            return f"Searching '{clean}' on Spotify..."
            
        elif self.mode == "YouTube":
            vid_id, title = self._get_video_info(query)
            if vid_id:
                url = f"https://www.youtube.com/watch?v={vid_id}"
                self._add_to_history("youtube", vid_id, title)
                webbrowser.open(url)
                return f"Playing on YouTube: {title}"
            return f"Could not find music for: {query}"
            
        return "Unknown music mode."

    def add_to_queue(self, query):
        if self.mode == "Spotify":
             return "⚠️ Queueing (`m!add`) is not supported in Spotify mode. Switch to YouTube mode for queue features."
        
        # YouTube Mode
        vid_id, title = self._get_video_info(query)
        if vid_id:
            self.queue.append(('youtube', vid_id, title))
            return f"Added to queue: {title}"
        return f"Could not find music for: {query}"

    def start_loop(self):
        if self.mode == "Spotify":
             return "⚠️ Looping (`m!loop`) is not supported in Spotify mode."
             
        if not self.queue:
            return "The music queue is empty. Add songs with 'm!add <name>'."
        
        # Filter for YouTube items
        yt_ids = [item[1] for item in self.queue if item[0] == 'youtube']
                
        if not yt_ids:
            return "No YouTube songs in queue to loop."
            
        id_str = ",".join(yt_ids)
        url = f"https://www.youtube.com/watch_videos?video_ids={id_str}"
        
        webbrowser.open(url)
        return f"Starting loop of {len(yt_ids)} songs on YouTube."

    def format_history(self):
        if not self.history:
            return "History is empty."
        
        lines = ["**Music History:**"]
        for i, item in enumerate(self.history[:10], 1): # Top 10
            lines.append(f"{i}. {item.get('title', 'Unknown')} ({item.get('type')})")
        return "\n".join(lines)

    def play_from_history(self, index):
        if 1 <= index <= len(self.history):
            item = self.history[index - 1]
            if item['type'] == 'youtube':
                # If ID looks like a URL (legacy fallback), open it directly
                if item['id'].startswith("http"):
                    webbrowser.open(item['id'])
                else:
                    url = f"https://www.youtube.com/watch?v={item['id']}"
                    webbrowser.open(url)
                
                # Re-add to top of history (update timestamp)
                self._add_to_history(item['type'], item['id'], item['title'])
                return f"Playing from history: {item.get('title')}"
                
            elif item['type'] == 'spotify':
                 webbrowser.open(item['id']) # ID is the full URL
                 self._add_to_history(item['type'], item['id'], item['title'])
                 return f"Opening Spotify link: {item.get('title')}"
                 
        return f"Invalid history index. Use 1-{len(self.history)}."
    
    def delete_history_item(self, index):
        if 1 <= index <= len(self.history):
            removed = self.history.pop(index - 1)
            self._save_history()
            return f"Removed '{removed.get('title')}' from history."
        return "Invalid index."

    def clear_history(self):
        self.history = []
        self._save_history()
        return "Music history cleared."

    def clear_queue(self):
        count = len(self.queue)
        self.queue = []
        return f"Queue cleared ({count} items removed)."
