import yt_dlp
import webbrowser
import re
import urllib.parse
import threading

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
             webbrowser.open(query)
             return f"Opening Spotify Link..."
        if "youtube.com" in query or "youtu.be" in query:
             webbrowser.open(query)
             return f"Opening YouTube Link..."

        if self.mode == "Spotify":
            clean = self._clean_spotify_query(query)
            encoded = urllib.parse.quote(clean)
            uri = f"spotify:search:{encoded}"
            webbrowser.open(uri)
            return f"Searching '{clean}' on Spotify..."
            
        elif self.mode == "YouTube":
            vid_id, title = self._get_video_info(query)
            if vid_id:
                url = f"https://www.youtube.com/watch?v={vid_id}"
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

    def clear_queue(self):
        count = len(self.queue)
        self.queue = []
        return f"Queue cleared ({count} items removed)."
