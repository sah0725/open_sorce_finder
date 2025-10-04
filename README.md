# GSoC Contributor Compass

An AI-powered web app to help new open-source contributors find and analyze beginner-friendly GitHub issues, built for the FutureStack'25 hackathon.

## Features
- Search for "good first issues" and "help wanted" issues across multiple programming languages
- AI-powered analysis and summary for each issue (Meta Llama 3 via OpenRouter)
- Modern, responsive UI inspired by goodfirstissue.dev
- Secure API key management with `.env`

## How It Works
1. Select your preferred programming language(s)
2. Click "Find Issues"
3. Browse a curated, AI-analyzed list of open issues from GitHub

## Tech Stack
- **Backend:** Python, Flask, OpenAI (OpenRouter), Requests
- **Frontend:** HTML, CSS, JavaScript
- **APIs:** GitHub REST API, OpenRouter (Meta Llama 3)

## Setup Instructions
1. Clone this repo
2. Create a `.env` file with your `OPENROUTER_API_KEY` and `GITHUB_TOKEN`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the app: `python app.py`
5. Open your browser to `http://localhost:5001`

## Environment Variables
```
OPENROUTER_API_KEY=your_openrouter_key
GITHUB_TOKEN=your_github_pat
```


