import requests
import json

def search_books(query):
    print("Searching:", query)

    url = "https://itunes.apple.com/search"

    params = {
        "term": query,
        "entity": "ebook",
        "limit": 6  # Get 6 books to fit nicely in 3 columns
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )
        
        data = response.json()
        
        if data.get("resultCount", 0) == 0:
            return json.dumps({"error": f"No books found for '{query}'."})
            
        books = []
        for item in data.get("results", []):
            book = {
                "title": item.get('trackName', 'Unknown'),
                "author": item.get('artistName', 'Unknown'),
                "genres": item.get('genres', ['Unknown']),
                "published": str(item.get('releaseDate', 'Unknown'))[:10],
                # Request a larger cover image (300x300 instead of 100x100)
                "cover_url": item.get('artworkUrl100', '').replace('100x100bb', '300x300bb')
            }
            books.append(book)
            
        return json.dumps({"books": books})
    except Exception as e:
        return json.dumps({"error": f"Error occurred during search: {str(e)}"})