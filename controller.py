from fastapi import APIRouter
from service import profanityService

router = APIRouter(prefix='/api')


@router.post('/profanity')
async def checkProfanity(request_data: dict):
    return await profanityService.checkProfanity(request_data)