import uvicorn
import traceback
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Shadow Layer entrypoint
from backend.shadow.chat_wrapper import ChatWrapper


# -------------------------------------------------
# FastAPI App
# -------------------------------------------------
app = FastAPI(
    title="Paladin AI - Shadow Layer API",
    description="Structural Interface for WLM 7-Layer Runtime",
    version="1.1.0"
)

# -------------------------------------------------
# CORS (Development – explicit ports)
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",

        "http://localhost:5500",
        "http://127.0.0.1:5500",

        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------
# Core Logic Instance
# -------------------------------------------------
chat = ChatWrapper()


# -------------------------------------------------
# Schemas
# -------------------------------------------------
class ChatPayload(BaseModel):
    conversation_id: str
    message: str
    api_key: Optional[str] = None
    metadata: Optional[dict] = None


# -------------------------------------------------
# CHAT ENDPOINTS
# -------------------------------------------------

# OPTIONS MUST COME FIRST
@app.options("/chat", tags=["Core"])
async def chat_options(request: Request):
    return {}

@app.post("/chat", tags=["Core"])
async def chat_api(payload: ChatPayload):
    """
    Primary interface for text-to-structure collapse.
    Triggers the 7-layer runtime and updates structural memory.
    """
    try:
        # Pass the message, conversation_id, and api_key to ChatWrapper
        response = chat.chat(
            payload.message,
            payload.conversation_id,
            api_key=payload.api_key
        )

        return {"status": "success", "data": response}

    except Exception as e:
        # --- THE DEBUGGER ---
        print("\n" + "="*50)
        print(">>> FATAL RUNTIME ERROR DETECTED <<<")
        traceback.print_exc() # This prints the line number and file causing the 500
        print("="*50 + "\n")
        
        raise HTTPException(
            status_code=500, 
            detail=f"Runtime Error: {str(e)}"
        )


# -------------------------------------------------
# WORLD ENDPOINTS
# -------------------------------------------------
@app.get("/world", tags=["Structural Memory"])
def get_world(conversation_id: str):
    try:
        world = chat.struct_mem.get_world(conversation_id)
        return {"conversation_id": conversation_id, "world": world}
    except Exception:
        raise HTTPException(status_code=404, detail="World state not found")


@app.post("/world", tags=["Structural Memory"])
def set_world(conversation_id: str, world: dict):
    try:
        chat.struct_mem.set_world(conversation_id, world)
        return {"status": "ok", "message": f"World metadata updated for {conversation_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------
# PERSONA ENDPOINTS
# -------------------------------------------------
@app.get("/persona", tags=["Identity"])
def get_persona(conversation_id: str):
    try:
        persona = chat.struct_mem.get_persona(conversation_id)
        return {"conversation_id": conversation_id, "persona": persona}
    except Exception:
        raise HTTPException(status_code=404, detail="Persona not found")


@app.post("/persona", tags=["Identity"])
def set_persona(conversation_id: str, persona: dict):
    try:
        chat.struct_mem.set_persona(conversation_id, persona)
        return {"status": "ok", "message": f"Persona updated for {conversation_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------
# WORKFLOW ENDPOINTS
# -------------------------------------------------
@app.get("/workflow", tags=["Process"])
def get_workflow(conversation_id: str):
    try:
        workflow = chat.struct_mem.get_workflow(conversation_id)
        return {"conversation_id": conversation_id, "workflow": workflow}
    except Exception:
        raise HTTPException(status_code=404, detail="Workflow not found")


@app.post("/workflow", tags=["Process"])
def set_workflow(conversation_id: str, workflow: dict):
    try:
        chat.struct_mem.set_workflow(conversation_id, workflow)
        return {"status": "ok", "message": f"Workflow updated for {conversation_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------------------------
# FILE TEXT EXTRACTION HELPERS
# -------------------------------------------------
import tempfile
from docx import Document
import pdfplumber

def extract_docx_text(bytes_data: bytes) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(bytes_data)
        tmp_path = tmp.name
    doc = Document(tmp_path)
    return "\n".join(p.text for p in doc.paragraphs)

def extract_pdf_text(bytes_data: bytes) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(bytes_data)
        tmp_path = tmp.name
    with pdfplumber.open(tmp_path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)


# -------------------------------------------------
# FILE UPLOAD
# -------------------------------------------------
@app.post("/upload", tags=["System"])
async def upload_file(conversation_id: str, file: UploadFile = File(...)):
    try:
        content = await file.read()
        filename = file.filename.lower()

        # ⭐ Detect file type and extract text properly
        if filename.endswith(".docx"):
            text = extract_docx_text(content)
        elif filename.endswith(".pdf"):
            text = extract_pdf_text(content)
        else:
            # fallback for .txt, .md, etc.
            text = content.decode("utf-8", errors="ignore")

        # ⭐ Accumulate text in structural memory
        existing = chat.struct_mem.get_file_input(conversation_id) or ""
        combined = existing + "\n\n" + text
        chat.struct_mem.set_file_input(conversation_id, combined)

        return {
            "status": "success",
            "filename": file.filename,
            "content": text
        }

    except Exception as e:
        print("UPLOAD ERROR:", e)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


# -------------------------------------------------
# ENTRY POINT
# -------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
