from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import openai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuizRequest(BaseModel):
    topics: List[str]
    questions_per_topic: int = 50

class QuizResponse(BaseModel):
    questions: dict

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.post("/generate-quiz")
async def generate_quiz(request: QuizRequest):
    try:
        all_questions = {}
        
        for topic in request.topics:
            # Prompt engineering for quiz generation
            prompt = f"""Generate {request.questions_per_topic} multiple choice questions about {topic}. 
            Format each question as a JSON object with the following structure:
            {{
                "question": "The question text",
                "options": ["option1", "option2", "option3", "option4"],
                "correct_answer": "The correct option",
                "explanation": "Brief explanation of the correct answer"
            }}
            Return the questions as a JSON array."""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates multiple choice questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            # Extract the generated questions from the response
            all_questions[topic] = response.choices[0].message.content

        return {"questions": all_questions}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 