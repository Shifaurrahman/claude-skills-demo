import anthropic
from dotenv import load_dotenv
import os

load_dotenv()

client = anthropic.Anthropic()

print("🎨 Creating PowerPoint presentation...")

response = client.beta.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    betas=["code-execution-2025-08-25", "skills-2025-10-02", "files-api-2025-04-14"],
    container={
        "skills": [
            {
                "type": "anthropic",
                "skill_id": "pptx",  # PowerPoint skill
                "version": "latest"
            }
        ]
    },
    messages=[{
        "role": "user",
        "content": "Create a professional 5-slide presentation about AI in healthcare. Include: title slide, 3 content slides about diagnosis/treatment/patient care, and a conclusion slide. Use a modern color scheme."
    }],
    tools=[{
        "type": "code_execution_20250825",
        "name": "code_execution"
    }]
)

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

for file_id in extract_file_ids(response):
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