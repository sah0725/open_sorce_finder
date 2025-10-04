from openai import OpenAI
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

GITHUB_API_URL = "https://api.github.com/search/issues"

def search_github_issues(languages):
    """
    Searches GitHub for open issues with "good first issue" or "help wanted" labels
    for the specified languages.
    """
    all_issues = []
    print(f"Searching for issues in languages: {languages}")

    # Construct one query for all selected languages
    lang_queries = [f"language:{lang}" for lang in languages]
    language_query_part = " OR ".join(lang_queries)

    query_parts = [
        "state:open",
        "label:\"good first issue\",\"help wanted\"",
        "no:assignee",
        f"({language_query_part})"
    ]
    
    query = " ".join(query_parts)
    print(f"Constructed GitHub Query: {query}")
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {os.getenv('GITHUB_TOKEN')}"
    }
    
    params = {
        "q": query,
        "sort": "updated",
        "order": "desc",
        "per_page": 50  # Fetch more issues to get a wider selection
    }
    
    try:
        response = requests.get(GITHUB_API_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        issues = data.get('items', [])
        print(f"Found {len(issues)} issues from GitHub API.")
        all_issues.extend(issues)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from GitHub API: {e}")
        return []

    return all_issues

repo_cache = {}
headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"token {os.getenv('GITHUB_TOKEN')}"
}

def find_good_first_issues(languages):
    """
    Finds and analyzes good first issues from GitHub.
    """
    try:
        issues = search_github_issues(languages)
        
        if not issues:
            print("No issues received from search_github_issues.")
            return []
        
        print(f"Received {len(issues)} issues to analyze.")

        analyzed_issues = []
        for i, issue in enumerate(issues):
            print(f"Processing issue {i+1}/{len(issues)}: {issue.get('html_url')}")
            
            # Limit to 20 issues to balance speed and results
            if len(analyzed_issues) >= 20:
                print("-> Reached the limit of 20 analyzed issues. Stopping.")
                break

            repo_url = issue.get('repository_url')
            if not repo_url:
                print(f"  -> Skipping issue {i+1} because it has no 'repository_url'.")
                continue

            # Fetch repository details if not in cache
            if repo_url in repo_cache:
                print(f"  -> Found repo details in cache for {repo_url}")
                issue['repository'] = repo_cache[repo_url]
            else:
                try:
                    print(f"  -> Fetching repository details from {repo_url}...")
                    repo_response = requests.get(repo_url, headers=headers)
                    repo_response.raise_for_status()
                    repo_data = repo_response.json()
                    issue['repository'] = repo_data
                    repo_cache[repo_url] = repo_data
                    print(f"  -> Successfully fetched and cached repo details.")
                except requests.exceptions.RequestException as e:
                    print(f"  -> ERROR: Could not fetch repo details for {repo_url}: {e}")
                    continue # Skip this issue if we can't get repo details

            analysis = None
            try:
                print(f"  -> Analyzing issue {i+1} with AI...")
                analysis = analyze_and_summarize_issue(issue)
                print(f"  -> AI analysis complete for issue {i+1}.")
            except Exception as e:
                print(f"  -> ERROR: Could not analyze issue {issue.get('html_url')}: {e}")
                analysis = {
                    "summary": "Could not analyze this issue, but it might be a good starting point.",
                    "classification": "Unknown"
                }

            issue_details = {
                'title': issue['title'],
                'url': issue['html_url'],
                'repo_name': issue['repository']['full_name'],
                'stars': issue['repository']['stargazers_count'],
                'labels': [label['name'] for label in issue['labels']],
                'updated_at': issue['updated_at'],
                'analysis': analysis
            }
            analyzed_issues.append(issue_details)
            print(f"  -> Successfully processed and added issue {i+1}.")

        print(f"Returning {len(analyzed_issues)} analyzed issues to the frontend.")
        return analyzed_issues
    except Exception as e:
        print(f"An error occurred in find_good_first_issues: {e}")
        return []

def analyze_and_summarize_issue(issue):
    """
    Uses an AI model to analyze an issue and determine if it's a good fit for a beginner.
    Generates a user-friendly summary and a classification.
    """
    prompt = f"""
    You are an expert open-source contributor helping a student find their first issue.
    Analyze the following GitHub issue. First, classify it as "Good" or "Not Good" for a beginner, followed by a newline. Then, provide a one-paragraph summary explaining your reasoning.

    A "Good" issue has a clear description, seems self-contained, and doesn't require deep system knowledge.
    A "Not Good" issue might be vague, require too much context, or show signs of complex dependency.

    Format your response EXACTLY like this:
    Classification: [Good/Not Good]
    Summary: [Your one-paragraph explanation here]

    **Issue Title:** {issue['title']}
    **Issue Body:**
    {issue['body']}
    """
    
    try:
        # This is the updated syntax for the openai library v1.0.0+
        response = client.chat.completions.create(
            model="meta-llama/llama-3-8b-instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=250
        )
        raw_text = response.choices[0].message.content.strip()
        
        # Parse the structured response
        lines = raw_text.split('\n', 1)
        classification = "Not Good"
        summary = "Could not fully analyze this issue. Please review it carefully."

        if len(lines) == 2:
            class_part, summary_part = lines
            if "Good" in class_part:
                classification = "Good"
            
            if summary_part.startswith("Summary:"):
                summary = summary_part.replace("Summary:", "").strip()

        return {"classification": classification, "summary": summary}

    except Exception as e:
        print(f"Error with AI model: {e}")
        return {"classification": "Not Good", "summary": "Could not analyze this issue due to an error. It might be a good fit, but please review it carefully."}
