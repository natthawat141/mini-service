from fastapi import APIRouter, HTTPException
from app.models.request_models import TaxInfo
from app.models.response_models import RecommendationResponse
import together
from datetime import datetime
from app.config.settings import Settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
settings = Settings()
together.api_key = settings.TOGETHER_API_KEY

@router.post("/recommend", response_model=RecommendationResponse)
async def get_tax_recommendation(tax_info: TaxInfo):
    try:
        # สร้าง system prompt
        system_prompt = "นี่คือผู้เชี่ยวชาญด้านการวางแผนภาษีที่ให้คำแนะนำเป็นภาษาไทย"
        
        # สร้าง user prompt
        user_prompt = f"""กรุณาวิเคราะห์และให้คำแนะนำการลดหย่อนภาษีจากข้อมูลต่อไปนี้:

1. ข้อมูลรายได้และภาษี:
- รายได้รวมต่อปี: {tax_info.totalIncome:,.2f} บาท
- ลดหย่อนรวม: {tax_info.totalDeduction:,.2f} บาท

2. การลงทุนและลดหย่อนปัจจุบัน:
- SSF: {tax_info.ssfAmount:,.2f} บาท
- RMF: {tax_info.rmfAmount:,.2f} บาท
- ESG: {tax_info.esgAmount:,.2f} บาท
- เงินบริจาค: {tax_info.donationAmount:,.2f} บาท
- ดอกเบี้ยบ้าน: {tax_info.homeLoanAmount:,.2f} บาท

โปรดวิเคราะห์และแนะนำ:
"""

        # เตรียม messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        logger.info("Sending request to Together API")
        
        # เรียกใช้ API ด้วย format ใหม่
        completion = together.Complete.create(
            model="mistralai/Mistral-7B-Instruct-v0.1",  # เปลี่ยนเป็น model ที่รองรับ
            prompt=messages,
            temperature=0.7,
            max_tokens=800,
            top_k=50,
            top_p=0.7
        )

        if 'output' not in completion or 'choices' not in completion['output']:
            raise ValueError("Invalid API response format")

        recommendation = completion['output']['choices'][0]['text'].strip()

        if not recommendation:
            raise ValueError("Empty response from API")

        logger.info("Successfully received recommendation")

        return RecommendationResponse(
            recommendation=recommendation,
            timestamp=datetime.now()
        )

    except Exception as e:
        logger.error(f"Error in get_tax_recommendation: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )