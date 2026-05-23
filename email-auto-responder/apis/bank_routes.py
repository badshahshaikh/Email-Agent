# apis/bank_routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from apis.bank_services import BankAPI

router = APIRouter(prefix="/bank", tags=["Direct Banking Operations"])
bank_service = BankAPI()

# --- Request Models ---
class AccountRequest(BaseModel):
    account_number: str

class CardRequest(BaseModel):
    card_number: str

class TransactionRequest(BaseModel):
    card_number: str
    count: int = 5

# --- Routes ---

@router.post("/validate-account")
async def validate_account(req: AccountRequest):
    result = bank_service.ValidateAccountAPI(req.account_number)
    if result["status"] != "VALID":
        raise HTTPException(status_code=404, detail=result.get("error"))
    return result

@router.post("/validate-card")
async def validate_card(req: CardRequest):
    result = bank_service.ValidateCardAPI(req.card_number)
    if result["status"] != "VALID":
        raise HTTPException(status_code=404, detail=result.get("error"))
    return result

@router.post("/balance")
async def get_balance(req: AccountRequest):
    result = bank_service.GetAccountBalanceAPI(req.account_number)
    if result["status"] != "SUCCESS":
        raise HTTPException(status_code=404, detail=result.get("error"))
    return result

@router.post("/card-transactions")
async def get_card_transactions(req: TransactionRequest):
    result = bank_service.GetCardTransactionsAPI(req.card_number, req.count)
    if result["status"] != "SUCCESS":
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result

@router.post("/statement")
async def get_statement(req: AccountRequest):
    result = bank_service.GetStatementAPI(req.account_number)
    if result["status"] != "SUCCESS":
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result