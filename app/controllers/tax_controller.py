from fastapi import APIRouter, HTTPException
from app.models.request_models import TaxInfo
from app.models.response_models import RecommendationResponse
import together
from datetime import datetime
from app.config.settings import Settings
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
settings = Settings()
together.api_key = settings.TOGETHER_API_KEY

@router.post("/recommend", response_model=RecommendationResponse)
async def get_tax_recommendation(tax_info: TaxInfo):
    try:
        # สร้าง prompt
        ai_prompt = f"""จากข้อมูลการเงินต่อไปนี้ กรุณาวิเคราะห์และให้คำแนะนำ:
รายได้: {tax_info.totalIncome:,.0f} บาท
ภาษี: {tax_info.taxBeforeDeduction:,.0f} บาท
SSF: {tax_info.ssfAmount:,.0f} บาท
RMF: {tax_info.rmfAmount:,.0f} บาท
ESG: {tax_info.esgAmount:,.0f} บาท
บริจาค: {tax_info.donationAmount:,.0f} บาท

1. แนะนำการลงทุนเพิ่มเติม
2. โอกาสลดหย่อนภาษี
3. คำแนะนำเฉพาะกรณี"""

        logger.info("Sending request to Together API")
        
        try:
            # เรียกใช้ Together API
            completion = together.Complete.create(
                model="scb10x/scb10x-llama3-typhoon-v1-5x-4f316",
                prompt=[{
                    "role": "system", 
                    "content": "คุณคือผู้เชี่ยวชาญด้านการวางแผนภาษีในประเทศไทย"
                }, {
                    "role": "user",
                    "content": ai_prompt
                }],
                max_tokens=512,
                temperature=0.7,
                top_p=0.7,
                top_k=50
            )
            
            if not completion or 'output' not in completion or 'choices' not in completion['output']:
                raise ValueError("Invalid API response format")

            recommendation = completion['output']['choices'][0]['text'].strip()
            
            if not recommendation:
                raise ValueError("Empty API response")

            return RecommendationResponse(
                recommendation=recommendation,
                timestamp=datetime.now()
            )
            
        except Exception as api_error:
            logger.error(f"API Error: {str(api_error)}")
            
            # ถ้า API มีปัญหาใช้ mock response
            mock_response = f"""
            จากข้อมูลของคุณ แนะนำดังนี้:

            1. การลงทุนเพิ่มเติม:
               - SSF: สามารถลงทุนเพิ่มได้ {min(tax_info.totalIncome * 0.3, 200000) - tax_info.ssfAmount:,.0f} บาท
               - RMF: สามารถลงทุนเพิ่มได้ {min(tax_info.totalIncome * 0.3, 500000) - tax_info.rmfAmount:,.0f} บาท

            2. โอกาสลดหย่อนภาษี:
               - เงินบริจาค: เพิ่มได้อีก {tax_info.totalIncome * 0.1 - tax_info.donationAmount:,.0f} บาท
               - ประกันชีวิต: ลดหย่อนได้สูงสุด 100,000 บาท
               - ประกันสุขภาพ: ลดหย่อนได้สูงสุด 25,000 บาท

            3. คำแนะนำเฉพาะ:
               - ควรพิจารณาลงทุน SSF/RMF เพิ่มเติม
               - ศึกษาสิทธิประโยชน์อื่นๆ เช่น ดอกเบี้ยบ้าน การศึกษาบุตร
               - วางแผนการลงทุนระยะยาวเพื่อผลตอบแทนและสิทธิประโยชน์ทางภาษี
            """
            
            return RecommendationResponse(
                recommendation=mock_response,
                timestamp=datetime.now()
            )

    except Exception as e:
        logger.error(f"General Error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"เกิดข้อผิดพลาด: {str(e)}"
        )