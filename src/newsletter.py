import git
from datetime import datetime, timedelta
from brain import ResearchBrain
from config import VAULT_DIR
from logger import get_logger
from prompt_manager import load_prompt

logger = get_logger(__name__)

# Configuration
NEWSLETTER_OUTPUT = VAULT_DIR / "Newsletter"

def get_weekly_delta():
    repo = git.Repo(VAULT_DIR)
    # Get commits from the last 7 days
    since_date = datetime.now() - timedelta(days=7)
    commits = list(repo.iter_commits(since=since_date.isoformat()))
    
    delta_text = ""
    processed_files = set()

    for commit in commits:
        for file in commit.stats.files:
            if file.endswith(".md") and file not in processed_files:
                # Get the content of the file as it stands now
                file_path = VAULT_DIR / file
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        delta_text += f"\n--- {file} ---\n{f.read()}\n"
                processed_files.add(file)
    
    return delta_text

def generate_newsletter():
    brain = ResearchBrain()
    logger.info("Auditing the last 7 days of research...")
    
    try:
        delta = get_weekly_delta()
    except Exception as e:
        logger.error(f"Error getting weekly delta (ensure VAULT_DIR is a valid git repo): {e}")
        return
        
    if not delta:
        logger.info("No changes found in the last 7 days.")
        return

    logger.info("Brain is synthesizing the Weekly Delta...")
    
    try:
        prompt_config = load_prompt("weekly_newsletter.yaml")
    except Exception as e:
        logger.error(f"Error loading prompt: {e}")
        return

    result = brain.process_chunk(delta, prompt_config)
    
    if "error" in result:
        logger.error(f"Failed to generate newsletter: {result['error']}")
        return
        
    # Ensure directory exists
    NEWSLETTER_OUTPUT.mkdir(parents=True, exist_ok=True)
    
    # Save the Newsletter to the Vault
    week_num = datetime.now().strftime("%Y-W%W")
    filename = NEWSLETTER_OUTPUT / f"Weekly_Brief_{week_num}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(result['content'])
    
    logger.info(f"Newsletter generated: {filename}")

if __name__ == "__main__":
    generate_newsletter()