import anthropic
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Verify the key is loaded (optional - for debugging)
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("❌ Error: ANTHROPIC_API_KEY not found in environment variables")
    exit()
else:
    print(f"✅ API Key loaded: {api_key[:20]}...")  # Shows first 20 chars only

# Initialize client
client = anthropic.Anthropic()

# Create a message with Excel skill
response = client.beta.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    betas=["code-execution-2025-08-25", "skills-2025-10-02", "files-api-2025-04-14"],
    container={
        "skills": [
            {
                "type": "anthropic",
                "skill_id": "xlsx",
                "version": "latest"
            }
        ]
    },
    messages=[{
        "role": "user",
        "content": "Create a simple budget spreadsheet with categories: Rent, Food, Transport, Entertainment. Add sample data for 3 months."
    }],
    tools=[{
        "type": "code_execution_20250825",
        "name": "code_execution"
    }]
)

# Extract file IDs from response
def extract_file_ids(response):
    file_ids = []
    for item in response.content:
        if item.type == 'bash_code_execution_tool_result':
            content_item = item.content
            if content_item.type == 'bash_code_execution_result':
                for file in content_item.content:
                    if hasattr(file, 'file_id'):
                        file_ids.append(file.file_id)
    return file_ids

# Download the created Excel file
file_ids = extract_file_ids(response)
if file_ids:
    for file_id in file_ids:
        file_metadata = client.beta.files.retrieve_metadata(
            file_id=file_id,
            betas=["files-api-2025-04-14"]
        )
        
        file_content = client.beta.files.download(
            file_id=file_id,
            betas=["files-api-2025-04-14"]
        )
        
        file_content.write_to_file(file_metadata.filename)
        print(f"✅ Successfully downloaded: {file_metadata.filename}")
else:
    print("⚠️ No files were created")