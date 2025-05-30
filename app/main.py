from fastapi import FastAPI, HTTPException,Depends, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import httpx
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
origins = [
    "https://nasser-qu.web.app",
    "https://nasser-qu.web.app/#",
    
    "https://nasser-qu.web.app/:8080",
]

app = FastAPI()
api_key_header = APIKeyHeader(name="Authorization", auto_error=True)

SECRET_API_TOKEN = "FUYTFGLijoijOJOIjOIJhGftreSREIUyIHJNBHVGCXES6GNbfghygnftbDRVGbvcFGH"

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != f"Bearer {SECRET_API_TOKEN}":
        raise HTTPException(status_code=403, detail="Invalid API token")
    return api_key


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class Content(BaseModel):
    content: str
    urls:list

class UrlFetch(BaseModel):
    url: str
    title: str

@app.post("/api/")
async def get_url_content(url: str , api_key: str = Depends(verify_api_key))-> Content:
    try:
     async with httpx.AsyncClient() as client:
        r = await client.get(url ,timeout=10)
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=404, detail="URL not found")
    if r.status_code != 200 or r.text == 201:
        raise HTTPException(status_code=404, detail="URL not found")
    
    soup = BeautifulSoup(r.text, 'html.parser')
    text = ""
    if soup.find('article'):
        
        text = soup.find('article').get_text(separator="\n")
    else:
        text = soup.get_text(separator="\n")
    
    ls:list[UrlFetch] = [ UrlFetch(url=link.get("href") , title=link.get("title")) for link in soup.find_all('a', href=True) if link.get("title")] 
    cleaned_text = " \n ".join(line.strip() for line in text.splitlines() if line.strip())
    return Content(content=cleaned_text, urls=urls_fillters(ls))


def urls_fillters (urls: list[UrlFetch]):
    url_get:list[UrlFetch] = []
    for u in urls:
        if u.url.endswith(".aspx"):
          url_get.append(UrlFetch(url= "https://www.qu.edu.qa"+u.url , title=u.title)) 
        elif u.url.startswith("mailto") or u.url.startswith("http"):
            url_get.append(UrlFetch(url= u.url , title=u.title)) 
        else:
            url_get.append(UrlFetch(url= "https://www.qu.edu.qa"+u.url , title=u.title))
    return url_get