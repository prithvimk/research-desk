import git
from datetime import datetime, timedelta
from brain import ResearchBrain

# Configuration
VAULT_PATH = "./data/04_obsidian_vault"
NEWSLETTER_OUTPUT = f"{VAULT_PATH}/Newsletter"

WEEKLY_SYSTEM_PROMPT = """
You are a Research Director. I will provide you with the 'Delta' (changes) 
from my personal research wiki over the last 7 days.
Your goal: Write a high-level executive summary.
- Group updates by Theme (e.g., AI, Biology, Personal Projects).
- Highlight "New Connections": Did a new note on Topic A change the context of existing Topic B?
- Suggest 3 follow-up research questions for next week.
Format: Professional Markdown.
"""

def get_weekly_delta():
    repo = git.Repo(VAULT_PATH)
    # Get commits from the last 7 days
    since_date = datetime.now() - timedelta(days=7)
    commits = list(repo.iter_commits(since=since_date.isoformat()))
    
    delta_text = ""
    processed_files = set()

    for commit in commits:
        for file in commit.stats.files:
            if file.endswith(".md") and file not in processed_files:
                # Get the content of the file as it stands now
                with open(f"{VAULT_PATH}/{file}", 'r') as f:
                    delta_text += f"\n--- {file} ---\n{f.read()}\n"
                processed_files.add(file)
    
    return delta_text

def generate_newsletter():
    brain = ResearchBrain()
    print("📊 Auditing the last 7 days of research...")
    delta = get_weekly_delta()
    
    if not delta:
        print("📭 No changes found in the last 7 days.")
        return

    print("🧠 Gemma is synthesizing the Weekly Delta...")
    # Using the Reasoning mode of Gemma 4
    result = brain.process_chunk(delta, WEEKLY_SYSTEM_PROMPT)
    
    # Save the Newsletter to the Vault
    week_num = datetime.now().strftime("%Y-W%W")
    filename = f"{NEWSLETTER_OUTPUT}/Weekly_Brief_{week_num}.md"
    
    with open(filename, 'w') as f:
        f.write(result['content'])
    
    print(f"📧 Newsletter generated: {filename}")

if __name__ == "__main__":
    generate_newsletter()