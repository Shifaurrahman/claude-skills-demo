import anthropic
from dotenv import load_dotenv
import os

load_dotenv()

client = anthropic.Anthropic()

# Get user input
print("📝 Custom Document Generator")
print("-" * 40)
doc_type = input("What type of document? (excel/powerpoint/word): ").lower()
topic = input("What topic/content? : ")

# Map document types to skills
skill_map = {
    "excel": "xlsx",
    "powerpoint": "pptx",
    "word": "docx"
}

if doc_type not in skill_map:
    print("❌ Invalid document type. Choose: excel, powerpoint, or word")
    exit()

print(f"\n🔧 Creating {doc_type} document about '{topic}'...")

response = client.beta.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    betas=["code-execution-2025-08-25", "skills-2025-10-02", "files-api-2025-04-14"],
    container={
        "skills": [
            {"type": "anthropic", "skill_id": skill_map[doc_type], "version": "latest"}
        ]
    },
    messages=[{
        "role": "user",
        "content": f"Create a professional {doc_type} document about {topic}. Make it comprehensive and well-structured."
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

files_created = []
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
    files_created.append(file_metadata.filename)
    print(f"✅ Downloaded: {file_metadata.filename}")

print("\n✅ All files downloaded successfully:")
for file in files_created:
    print(f"- {file}")