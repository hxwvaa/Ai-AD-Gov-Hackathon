from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
from datetime import datetime
import uuid
import PyPDF2
import docx
from typing import List, Optional, Dict
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import warnings
import gc
from dotenv import load_dotenv 

warnings.filterwarnings('ignore')

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure upload settings
UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt"}

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

load_dotenv()
# Configure Google AI Studio
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

genai.configure(api_key=GOOGLE_API_KEY)

# Configure the model
model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config={
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40,
        "max_output_tokens": 2048,
    },
    safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
)

class DocumentResponse:
    def __init__(self, filename: str, file_id: str, upload_time: str, file_size: int):
        self.filename = filename
        self.file_id = file_id
        self.upload_time = upload_time
        self.file_size = file_size

class AnalysisResponse(BaseModel):
    summary: str
    key_points: List[str]
    recommendations: List[str]
    confidence_score: int
    risks: List[str]
    next_steps: List[str]

async def generate_gemini_response(prompt: str) -> str:
    """Generate response using Gemini model."""
    try:
        formatted_prompt = f"""You are an expert government policy analyst. 
        Analyze this document and provide a structured opinion:

        {prompt}

        Please format your response with clear section headers:
        - Executive Summary
        - Key Points
        - Recommendations
        - Risks
        - Next Steps"""

        response = await model.generate_content_async(formatted_prompt)
        return response.text

    except Exception as e:
        raise Exception(f"Error in Gemini inference: {str(e)}")

def extract_text_from_file(file_path: str) -> str:
    """Extract text content from different file types."""
    file_ext = os.path.splitext(file_path)[1].lower()

    try:
        if file_ext == '.pdf':
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ''
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text

        elif file_ext in ['.doc', '.docx']:
            doc = docx.Document(file_path)
            text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            return text

        elif file_ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()

        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

    except Exception as e:
        raise Exception(f"Error extracting text from file: {str(e)}")

async def analyze_text(text: str) -> AnalysisResponse:
    """Analyze document content using Gemini."""
    try:
        # Generate response using Gemini
        gemini_response = await generate_gemini_response(text)

        # Parse the response
        sections = parse_ai_response(gemini_response)

        return AnalysisResponse(
            summary=sections['summary'],
            key_points=sections['key_points'],
            recommendations=sections['recommendations'],
            confidence_score=calculate_confidence(sections),
            risks=sections['risks'],
            next_steps=sections['next_steps']
        )

    except Exception as e:
        raise Exception(f"Error in document analysis: {str(e)}")

def parse_ai_response(content: str) -> Dict[str, any]:
    """Parse the AI response into structured sections."""
    lines = content.split('\n')
    sections = {
        'summary': '',
        'key_points': [],
        'recommendations': [],
        'risks': [],
        'next_steps': []
    }

    current_section = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check for section headers
        lower_line = line.lower()
        if 'executive summary' in lower_line:
            current_section = 'summary'
            continue
        elif 'key points' in lower_line:
            current_section = 'key_points'
            continue
        elif 'recommendations' in lower_line:
            current_section = 'recommendations'
            continue
        elif 'risks' in lower_line:
            current_section = 'risks'
            continue
        elif 'next steps' in lower_line:
            current_section = 'next_steps'
            continue

        # Add content to appropriate section
        if current_section:
            if current_section == 'summary':
                sections['summary'] += line + ' '
            else:
                # Remove bullet points and numbers
                cleaned_line = line.lstrip('•- 1234567890.)')
                if cleaned_line:
                    sections[current_section].append(cleaned_line.strip())

    return sections

def calculate_confidence(sections: Dict) -> int:
    """Calculate confidence score based on analysis completeness."""
    score = 100

    # Check for section completeness
    if not sections['summary'].strip():
        score -= 20
    if len(sections['key_points']) < 3:
        score -= 15
    if len(sections['recommendations']) < 3:
        score -= 15
    if len(sections['risks']) < 2:
        score -= 15
    if len(sections['next_steps']) < 3:
        score -= 15

    return max(score, 0)

class AnalysisRequest(BaseModel):
    file_id: str

@app.post("/analyze/", response_model=AnalysisResponse)
async def analyze_document(request: AnalysisRequest):
    try:
        file_path = os.path.join(UPLOAD_DIR, request.file_id)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        # Extract text from document
        text = extract_text_from_file(file_path)

        # Analyze the text
        analysis = await analyze_text(text)

        return analysis
    except Exception as e:
        print(f"Error during document analysis: {str(e)}")  # Log the error for debugging
        raise HTTPException(status_code=500, detail="Error during document analysis")

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Validate file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Get file size
        file_size = os.path.getsize(file_path)

        return {
            "filename": file.filename,
            "file_id": unique_filename,
            "upload_time": datetime.now().isoformat(),
            "file_size": file_size
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/")
async def list_files():
    files = []
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        files.append({
            "filename": filename,
            "upload_time": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
            "file_size": os.path.getsize(file_path)
        })
    return files