from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
from pathlib import Path
import together
from .controllers.tax_controller import router as tax_router
from .config.settings import Settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# กำหนด BASE_DIR 
BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
   title="Tax Calculation API",
   description="API สำหรับคำนวณและแนะนำการลดหย่อนภาษี",
   version="1.0.0"
)

settings = Settings()

# CORS
app.add_middleware(
   CORSMiddleware,
   allow_origins=["*"],
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)

# สร้างโฟลเดอร์ถ้ายังไม่มี
templates_dir = BASE_DIR / "templates"
static_dir = BASE_DIR / "static"

templates_dir.mkdir(exist_ok=True)
static_dir.mkdir(exist_ok=True)

# Static files
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Templates
templates = Jinja2Templates(directory=str(templates_dir))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
   try:
       return templates.TemplateResponse(
           "index.html",
           {"request": request}
       )
   except Exception as e:
       logger.error(f"Error loading template: {str(e)}")
       return HTMLResponse(content="Error loading template", status_code=500)

# Chat endpoint
@app.post("/api/chat")
async def chat_with_tax_expert(request: Request):
   """
   Endpoint สำหรับแชทกับผู้เชี่ยวชาญภาษี AI
   """
   try:
       data = await request.json()
       message = data.get('message')
       
       if not message:
           return HTMLResponse(
               content="กรุณาระบุข้อความที่ต้องการถาม",
               status_code=400
           )

       logger.info(f"Received chat message: {message}")

       # กำหนด system prompt
       system_prompt = {
           "role": "system",
           "content": """คุณคือผู้เชี่ยวชาญด้านภาษีและการวางแผนภาษีในประเทศไทย 
           มีความเชี่ยวชาญในเรื่อง:
           - การลดหย่อนภาษีทุกประเภท
           - การลงทุนเพื่อประหยัดภาษี (SSF, RMF, ESG)
           - กฎหมายภาษีและการยื่นภาษี
           - การวางแผนภาษีสำหรับบุคคลและธุรกิจ
           ให้คำแนะนำที่เป็นประโยชน์และเข้าใจง่าย"""
       }

       # User message
       user_message = {"role": "user", "content": message}

       try:
           # เรียกใช้ Together API
           completion = together.Complete.create(
               model="scb10x/scb10x-llama3-typhoon-v1-5x-4f316",
               prompt=[system_prompt, user_message],
               max_tokens=1024,
               temperature=0.7,
               top_p=0.8,
               top_k=50,
               repetition_penalty=1.1
           )
           
           response = completion['output']['choices'][0]['text'].strip()
           logger.info("Successfully received API response")
           
           return {"response": response}
           
       except Exception as api_error:
           logger.error(f"API Error: {str(api_error)}")
           
           # ถ้า API มีปัญหา ส่ง mock response
           mock_response = f"""
           ขออภัย ไม่สามารถประมวลผลคำถาม "{message}" ได้ในขณะนี้
           
           แนะนำให้:
           1. ปรึกษาผู้เชี่ยวชาญด้านภาษีโดยตรง
           2. ศึกษาข้อมูลเพิ่มเติมที่เว็บไซต์กรมสรรพากร (www.rd.go.th)
           3. ลองถามคำถามในรูปแบบอื่น หรือแบ่งคำถามเป็นส่วนย่อยๆ
           """
           return {"response": mock_response}

   except Exception as e:
       logger.error(f"General Error: {str(e)}")
       return HTMLResponse(
           content=f"เกิดข้อผิดพลาด: {str(e)}",
           status_code=500
       )
@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """
    แสดงหน้าแชท
    """
    try:
        return templates.TemplateResponse(
            "chat.html",
            {"request": request}
        )
    except Exception as e:
        logger.error(f"Error loading chat template: {str(e)}")
        return HTMLResponse(content="Error loading chat page", status_code=500)
    
# API routes
app.include_router(tax_router, prefix="/api/tax", tags=["tax"])

# Error handler
@app.exception_handler(500)
async def internal_server_error(request: Request, exc: Exception):
   logger.error(f"Internal Server Error: {str(exc)}")
   return HTMLResponse(
       content="Internal Server Error",
       status_code=500
   )

# Run app
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))  # ใช้ PORT จาก environment variable หรือ default เป็น 10000
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # ต้องเป็น 0.0.0.0 เพื่อให้เข้าถึงได้จากภายนอก
        port=port,
        reload=True
    )