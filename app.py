from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import asyncio
from mail_gen1 import generate_email

app = FastAPI()

### 🔹 Feature 1: AI Email Drafting from Prompt ###
class EmailPrompt(BaseModel):
    prompt: str
    context: dict = None

@app.post("/generate-email")
async def generate_email_endpoint(prompt: EmailPrompt, background_tasks: BackgroundTasks):
    """Generate an email based on the user's prompt."""
    try:
        email_content = generate_email(prompt.prompt, prompt.context)
        return {"status": "success", "email": email_content}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002)
