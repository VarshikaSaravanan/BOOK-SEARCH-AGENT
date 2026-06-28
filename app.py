import streamlit as st
import os
import json
import requests
from dotenv import load_dotenv

from tools import search_books
from prompts import SYSTEM_PROMPT

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "openrouter/free"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

st.set_page_config(page_title="Book Search Agent", page_icon="📚", layout="centered")

# Custom CSS for beautiful UI
st.markdown("""
<style>
    /* Gradient Background for the main title */
    .main-title {
        background: -webkit-linear-gradient(45deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3em;
        margin-bottom: 0px;
    }
    
    /* Style for the book cards */
    .book-card {
        background-color: #2b2b2b;
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s ease-in-out;
        text-align: center;
        height: 100%;
    }
    
    .book-card:hover {
        transform: translateY(-5px);
    }
    
    .book-img-container {
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    
    .book-title {
        font-size: 16px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 4px;
        line-height: 1.2;
    }
    
    .book-author {
        font-size: 14px;
        font-style: italic;
        color: #a0a0a0;
        margin-bottom: 8px;
    }
    
    .book-tag {
        display: inline-block;
        background: #4ECDC4;
        color: #000;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_books",
            "description": "Search for books by title, author, or keyword.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query (e.g. title or author)"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

TOOL_FUNCTIONS = {
    "search_books": search_books
}

def call_llm(messages):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": TOOLS
    }
    response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def run_tool(tool_call):
    tool_name = tool_call["function"]["name"]
    arguments = json.loads(tool_call["function"]["arguments"])
    if tool_name in TOOL_FUNCTIONS:
        return TOOL_FUNCTIONS[tool_name](**arguments)
    return json.dumps({"error": "Tool not found"})

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# Header
st.markdown('<h1 class="main-title">📚 Book Explorer AI</h1>', unsafe_allow_html=True)
st.markdown("*Your intelligent assistant for finding your next great read.*")
st.divider()

def render_book_gallery(tool_data):
    """Helper function to render the book gallery beautifully"""
    if "books" in tool_data and len(tool_data["books"]) > 0:
        books = tool_data["books"]
        
        # Display 3 books per row
        for i in range(0, len(books), 3):
            cols = st.columns(3)
            row_books = books[i:i+3]
            
            for idx, book in enumerate(row_books):
                with cols[idx]:
                    genre_tag = f'<span class="book-tag">{book["genres"][0]}</span>' if book.get("genres") else ""
                    
                    st.markdown(f"""
                    <div class="book-card">
                        <div class="book-img-container">
                            <img src="{book.get('cover_url', '')}" style="width: 100%; object-fit: cover;" alt="Cover Art">
                        </div>
                        <div class="book-title">{book.get('title', 'Unknown Title')}</div>
                        <div class="book-author">by {book.get('author', 'Unknown Author')}</div>
                        {genre_tag}
                    </div>
                    """, unsafe_allow_html=True)
    elif "error" in tool_data:
        st.error(tool_data["error"])

# Display existing chat messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
            
    elif msg["role"] == "assistant":
        if msg.get("content"):
            with st.chat_message("assistant"):
                st.write(msg["content"])
                
    elif msg["role"] == "tool":
        try:
            tool_data = json.loads(msg["content"])
            render_book_gallery(tool_data)
        except Exception:
            pass

# Chat Input
if prompt := st.chat_input("E.g., What are some popular books by Andy Weir?"):
    
    # 1. Add and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # 2. Get Agent response
    with st.spinner("Thinking..."):
        while True:
            response_data = call_llm(st.session_state.messages)
            assistant_message = response_data["choices"][0]["message"]
            
            # If the agent wants to use a tool
            if "tool_calls" in assistant_message and assistant_message["tool_calls"]:
                st.session_state.messages.append(assistant_message)
                
                for tool_call in assistant_message["tool_calls"]:
                    query = json.loads(tool_call['function']['arguments']).get('query', '')
                    
                    with st.status(f"Searching library for: '{query}'..."):
                        result_str = run_tool(tool_call)
                        
                        tool_msg = {
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "name": tool_call["function"]["name"],
                            "content": result_str
                        }
                        st.session_state.messages.append(tool_msg)
                        
                        # Render the book gallery instantly!
                        try:
                            tool_data = json.loads(result_str)
                            render_book_gallery(tool_data)
                        except Exception as e:
                            st.error(f"Failed to render books: {e}")
                            
            # If the agent is replying with text
            else:
                answer = assistant_message.get("content", "Unable to answer.")
                st.session_state.messages.append(assistant_message)
                
                with st.chat_message("assistant"):
                    st.write(answer)
                break
