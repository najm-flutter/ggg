from fastapi import FastAPI, HTTPException, File , UploadFile ,Header
from typing import Annotated
from youtube_transcript_api import YouTubeTranscriptApi
from enum import Enum
from pydantic import BaseModel,Field
import os , shutil
import httpx
from bs4 import BeautifulSoup

app = FastAPI()
class Image(BaseModel):
    url: str
    name: str


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    image: Image | None = None
    model_config = {
        "json_schema_extra":{
            "examples" : [
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                    "tags": ["rock", "metal", "bar"],
                    "image": {
                        "url": "http://example.com/baz.jpg",
                        "name": "The Foo live"
                    }
                }
            ]
        }
    }
@app.get("/get_transcript/")
async def get_transcript(video_id:  str, language: str = "en"):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["en","ar"])
        return {"video_id": video_id, "transcript": transcript}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/file/")
async def read_users(f: UploadFile=File()):
    print(os.getcwd())
    p = os.getcwd()+"/ub"
    paath = os.path.join(p,f.filename)
    with open(paath,'wb')as fiil:
        shutil.copyfileobj(f.file,fiil)
    
    return {"file_size": True}
@app.get("/api/")
async def get_url_content(url: str):
    try:
     async with httpx.AsyncClient() as client:
        r = await client.get(url ,timeout=10)
    except httpx.HTTPStatusError:
        return {"content": "Failed to fetch the URL, HTTP error."}
    soup = BeautifulSoup(r.text, 'html.parser')
    text = soup.get_text(separator="\n")
    cleaned_text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    return {"content": cleaned_text[1500:]}