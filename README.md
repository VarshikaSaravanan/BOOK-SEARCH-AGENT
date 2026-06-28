# Book Search Agent 

An intelligent, AI-powered conversational agent built with Streamlit and OpenRouter. This agent helps you discover your next great read by answering book-related questions and using an integrated search tool to find books, authors, and cover art.
<img width="508" height="657" alt="image" src="https://github.com/user-attachments/assets/c665dd0a-5bc3-4804-9d01-f58c18fc27da" />
<img width="510" height="268" alt="image" src="https://github.com/user-attachments/assets/675129be-a7ae-4e85-a939-8f99bfe917b8" />
## Features

- **Conversational Interface**: Chat naturally with the AI to get book recommendations.
- **Tool Integration**: The AI has access to a search tool that queries the Apple Books API for real-time book metadata and cover images.
- **Beautiful UI**: Enjoy a modern, responsive gallery view of the book results right in your chat window.

## Prerequisites

- Python 3.8+
- An API key from [OpenRouter](https://openrouter.ai/)

## Installation

1. **Clone or Download the Repository**
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Set Up Environment Variables**:
   Create a `.env` file in the root of the project and add your OpenRouter API key:
   ```env
   OPENROUTER_API_KEY=your_api_key_here
   ```

## Usage

You can run the application in two ways:

### 1. Web Application (Streamlit)
To launch the interactive web interface with the beautiful UI:
```bash
python -m streamlit run app.py
```
*(If you encounter a port conflict, you can run it on a different port using `--server.port 8502`)*

### 2. Command Line Interface (CLI)
To run the agent directly in your terminal without a web UI:
```bash
python main.py
```

## Technologies Used

- **[Streamlit](https://streamlit.io/)**: For the frontend web application.
- **[OpenRouter API](https://openrouter.ai/)**: For access to open-source LLMs (defaulted to `openrouter/free`).
- **[Apple Books API](https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/index.html)**: Used by the agent's tools to fetch book details and cover art.
