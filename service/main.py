from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from transformers import T5Tokenizer, T5ForConditionalGeneration
from pydantic import BaseModel
import os
from transformers import set_seed
import random


random.seed(42)
set_seed(42)

tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")
model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")


class request(BaseModel):
    title: str = "Clean energy is a Danish passion"
    tone: str = "Creative"
    vertical: str = "Energy"
    content_format: str = "Blogpost"
    max_length: int = 1000
    min_length: int = 400


class response(BaseModel):
    max_length: int
    min_length: int
    prompt: str
    draft: str
    hostname: str


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.get("/")
def root():
    return {
        "message": "This is a root endpoint. Please use /docs for API documentation"
    }


@app.get("/health", summary="Check that the service is operational")
async def health():
    return {"status": "ok"}


@app.post("/generate_draft", tags=["Model"])
async def generate_draft(request: request, token: str) -> response:
    if token != "cTAD1TIT7wYa6yK5KlayxLvv0WqIiHiRFEPZjPFdeVXSRqELeTt6iTUI5lC2AakW":
        return {"403 Forbidden": "Invalid token"}

    request = dict(request)
    print(request)

    query = request["title"]
    max_length = request["max_length"]
    min_length = request["min_length"]
    min_length = request["min_length"]
    num_return_sequences = 1
    top_k = 50
    top_p = 0.95
    tone = request["tone"]
    vertical = request["vertical"]
    content_format = request["content_format"]

    parameters = {
        "max_length": max_length,
        "max_length": max_length,
        "min_length": min_length,
        "num_return_sequences": num_return_sequences,
        "top_k": top_k,
        "top_p": top_p,
        "do_sample": True,
    }

    prompts = [
        f"""Title: \"{query}\"\\nGiven the above title of an imaginary article, imagine the article.\\n 
    The article is for the business of {vertical}, and 
    the tone of the text should be {tone}.\\n The generated content is to be used in {content_format}"""
    ]
    input_ids = tokenizer(prompts, return_tensors="pt").input_ids
    outputs = model.generate(input_ids, **parameters)
    draft = tokenizer.decode(outputs[0], skip_special_tokens=True)

    parameters.pop("do_sample")
    parameters.pop("num_return_sequences")
    parameters.pop("top_k")
    parameters.pop("top_p")

    parameters["prompt"] = prompts[0]
    parameters["draft"] = draft
    parameters["hostname"] = os.getenv("HOSTNAME") if os.getenv("HOSTNAME") is not None else "local"
    return parameters
