from pydantic import BaseModel
from typing import Optional

class TaxInfo(BaseModel):
    totalIncome: float              # รายได้รวม
    taxBeforeDeduction: float       # ภาษีก่อนลดหย่อน
    taxAfterDeduction: float        # ภาษีหลังลดหย่อน
    totalDeduction: float           # ค่าลดหย่อนรวม
    ssfAmount: float               # ลงทุน SSF
    rmfAmount: float               # ลงทุน RMF 
    esgAmount: float               # ลงทุน ESG
    donationAmount: float          # เงินบริจาค
    homeLoanAmount: float          # ดอกเบี้ยบ้าน