import os
from pathlib import Path # 폴더 경로를 가져오는 import
import torch
from model_storage import ensure_model_available
# AutoTokenizer: 문장을 모델이 이해할 수 있는 숫자 토큰으로 바꿈
# AutoModelForSequenceClassification: 문장 분류용 Transformer 모델을 불러옴
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# 한 단어만 들어올 때 정상단어인데 욕설 처리되는 단어들 예외처리
ALLOW_EXACT_WORDS = {
    # 사발 계열
    '사발',
    '사발면',
    '물사발',
    '밥사발',
    '국사발',
    '대접사발',
    '사발통문',

    # 시발 계열 정상 단어
    '시발점',
    '시발역',
    '시발지',
    '시발차',

    # 씨- 계열 정상 단어
    '씨앗',
    '씨알',
    '씨눈',

    # 병- 계열 정상 단어
    '병식',
    '병아리',
    '병어',
    '병풍',
    '병충해',
    '병정',

    # 지- 계열 정상 단어
    '지라',
    '지리',

    # 개- 계열 정상 단어
    '개나리',
    '개념',
    '개구쟁이',
    '개불',
    '개살구',
    '개암',
    '개망초',
    '개복치',
    '개비',

    # 일반 정상 단어
    '만년',
    '닭살',
    '닭장',
    '망태기',
    '멍울',
    '변기',
    '변소',
    '새끼줄',
    '십오',
    '십육',
    '시바견',
    '자지러지다',
    '자지러짐',
    '젖병',
    '젖니',
    '젖먹이',
    '젖산',
    '젓갈',
    '조개',
    '토막',
    '항문',
}

class ProfanityService:
    def __init__(self):
        default_model_path = Path(__file__).parent / 'kcelectra-profanity-model'
        self.model_path = Path(os.getenv('PROFANITY_MODEL_PATH', default_model_path)).expanduser()
        self.threshold = float(os.getenv('PROFANITY_THRESHOLD', '0.8')) # 욕설 판단 기준
        self.tokenizer = None # 토크나이저
        self.model = None # 사용할 모델

    def isModelLoaded(self):
        return self.model is not None and self.tokenizer is not None

    # 모델 로딩하는 함수
    def loadModel(self):
        # 모델 로딩이 이루어져 이미 채워져 있다면 반환
        if self.model is not None and self.tokenizer is not None:
            return

        ensure_model_available(self.model_path)

        # 저장된 모델의 토크나이저 불러오기( tokenizer )
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, use_fast=True)
        # 문장 분류 모델 불러오기
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
        # 학습모드가 아닌 추론 모드로
        self.model.eval()

    async def checkProfanity(self, request_data: dict):
        # 초기 모델 로딩
        self.loadModel()

        # 백엔드에서 가져온 문장 넣기( 예측 데이터 )
        texts = request_data.get('texts', [])

        # 문자열이 하나만 온 경우 리스트로 반환하여 처리
        if isinstance(texts, str):
            texts = [texts]

        # 문자열 빈 값 제거 및 공백 정리
        texts = [text.strip() for text in texts if isinstance(text, str) and text.strip()]

        # 검사할 문장이 없는 경우
        if len(texts) == 0:
            return {
                'blocked': False,
                'results': []
            }

        # 본격적인 문장 토크나이징
        inputs = self.tokenizer(
            texts,
            return_tensors='pt', # PyTorch tensor 형태로 반환
            truncation=True,
            max_length=512,
            padding=True
        )

        # 욕설 판별
        with torch.no_grad():
            outputs = self.model(**inputs)
            # 소프트맥스 함수로 원시 점수를 0~1의 확률값으로 바꿈
            probabilities = torch.softmax(outputs.logits, dim=-1)

        results = []

        # 결과에 대한 판정 0.7 이상이면 is_profanity True
        for text, probability in zip(texts, probabilities):

            # 욕설로 잡히는 한글자 정상 단어 예외 단어장에 걸릴 경우
            if text in ALLOW_EXACT_WORDS:
                results.append({
                    'text': text,
                    'isProfanity': False,
                    'score': 0.0
                })
                continue
            
            profanity_score = float(probability[1])
            is_profanity = profanity_score >= self.threshold

            # 결과리스트에 추가
            results.append({
                'text': text,
                'isProfanity': is_profanity,
                'score': profanity_score
            })

        return {
            # 어떠한 result가 욕설일 확률이 0.7 이상이면
            'blocked': any(result['isProfanity'] for result in results),
            'results': results
        }


profanityService = ProfanityService()
