# Yeoginamgim Profanity Filter

FastAPI 기반 욕설/비속어 검사 서비스입니다. 프론트엔드는 이 서비스를 직접 호출하지 않고, 호출 흐름은 `Frontend -> Spring Backend -> FastAPI`로 유지합니다.

## API

- `POST /api/profanity`
  - 요청: `{ "texts": ["검사할 문장"] }`
  - 응답: `{ "blocked": true|false, "results": [...] }`
- `GET /health`
  - 응답: `{ "status": "ok", "modelLoaded": true|false }`
  - 프로세스 alive와 모델 로딩 여부 확인용입니다.

## 로컬 실행

```powershell
cd Yeoginamgim-Python
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --host 127.0.0.1 --port 8001 --reload
```

백엔드는 기본 설정으로 `http://127.0.0.1:8001/api/profanity`를 호출합니다.

## 운영 실행 예시

```bash
cd Yeoginamgim-Python
uvicorn app:app --host 0.0.0.0 --port 8001
```

운영에서는 FastAPI를 공용 인터넷에 직접 노출하지 않는 구성을 우선합니다. 같은 서버의 loopback, 사설망, Docker Compose 내부 네트워크처럼 Spring Backend만 접근 가능한 주소를 사용하세요.

Spring Backend에는 다음 환경변수를 맞춥니다.

```bash
PROFANITY_API_URL=http://127.0.0.1:8001/api/profanity
PROFANITY_CONNECT_TIMEOUT=2s
PROFANITY_READ_TIMEOUT=5s
PROFANITY_FAIL_OPEN=false
```

운영 기본 정책은 fail-closed입니다. `PROFANITY_FAIL_OPEN=false`이면 필터 서버 장애, timeout, 비정상 응답 시 흔적 생성/수정을 막습니다. 로컬 개발에서만 필요하면 `PROFANITY_FAIL_OPEN=true`로 임시 우회할 수 있습니다.

## Python 환경변수

```bash
PROFANITY_MODEL_PATH=/app/kcelectra-profanity-model
PROFANITY_THRESHOLD=0.8
```

- `PROFANITY_MODEL_PATH` 기본값은 `Yeoginamgim-Python/kcelectra-profanity-model`입니다.
- 모델 파일이 크면 Git 저장소에 새로 추가하지 말고 운영 서버 또는 컨테이너 볼륨에 배치한 뒤 `PROFANITY_MODEL_PATH`로 지정하세요.
- 컨테이너 이미지에 포함할 경우 이미지 크기와 배포 시간을 감안하세요. 운영에서는 읽기 전용 볼륨 마운트를 권장합니다.

## 수동 검증

```bash
curl http://127.0.0.1:8001/health
curl -X POST http://127.0.0.1:8001/api/profanity \
  -H "Content-Type: application/json" \
  -d '{"texts":["좋은 기억"]}'
```

`/health`의 `modelLoaded`는 모델이 아직 로딩되지 않았으면 `false`일 수 있습니다. `/api/profanity` 첫 호출에서 모델을 로딩한 뒤 다시 확인하면 `true`가 됩니다.

## CORS

프론트엔드가 FastAPI를 직접 호출하지 않으므로 FastAPI에는 CORS를 열지 않습니다. 브라우저 요청은 Spring Backend로만 보내고, Spring Backend가 서버 간 통신으로 FastAPI를 호출합니다.
