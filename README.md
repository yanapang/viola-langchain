# LangChain RAG System with Local Wiki

A retrieval-augmented generation (RAG) system that connects your local markdown wiki with an LLM using LangChain. Ask questions about your wiki and get answers grounded in your knowledge base.

## Features

- **Local-first**: Default Ollama setup — no API keys required
- **Korean support**: Korean prompts and `bge-m3` embeddings for multilingual wikis
- **Multi-provider**: Ollama, Hugging Face, OpenAI, or Cursor (optional)
- **Persistent index**: Cached vectorstore in `.chroma/` for fast restarts
- **Auto-reindex**: Rebuilds when the embedding model changes

## 시작하기 (필수 작업)

아래 순서대로 진행하세요.

- [ ] **Ollama 설치 및 실행** — [ollama.ai](https://ollama.ai)에서 설치 후 앱/서비스를 켜 둡니다.
- [ ] **모델 다운로드** — 답변용·검색용 모델 **둘 다** 필요합니다 (역할이 다름).

  ```bash
  ollama pull qwen2.5:7b   # 답변 생성 (LLM)
  ollama pull bge-m3       # 위키 검색 (Embedding)
  ```

  > `bge-m3`를 `OLLAMA_LLM_MODEL`에 넣지 마세요. Embedding 모델은 채팅을 지원하지 않습니다.

- [ ] **가상환경 및 패키지 설치**

  ```bash
  cd langchain-llm
  python3 -m venv venv
  source venv/bin/activate          # Windows: venv\Scripts\activate
  pip install -r requirements-ollama.txt
  ```

  Hugging Face / Cursor 프로바이더가 필요하면: `pip install -r requirements-extra.txt`

- [ ] **환경 변수 설정**

  ```bash
  cp .env.example .env
  ```

  **`.env`에서 `WIKI_DIR`을 본인 위키 폴더 경로로 수정하세요.**  
  `./wiki`는 샘플용 placeholder입니다. 실제 `.md` 위키가 있는 경로(절대/상대 경로)를 넣어야 합니다.

  개인 설정만 분리하려면 `.env.local`을 만들 수 있습니다 (`.env`보다 우선 적용).

- [ ] **실행**

  ```bash
  python src/app.py
  ```

  첫 실행은 위키 인덱싱 때문에 시간이 걸릴 수 있습니다.

### 위키를 수정한 경우

```bash
python src/app.py --rebuild
```

| 상황 | 필요한 작업 |
|------|-------------|
| 위키 `.md` 추가·삭제·수정 | `python src/app.py --rebuild` |
| `OLLAMA_EMBED_MODEL` 또는 `EMBED_PROVIDER` 변경 | 다음 실행 시 **자동** rebuild |
| `OLLAMA_LLM_MODEL`만 변경 | rebuild **불필요**, 다시 실행만 하면 됨 |

### Cursor / VS Code

인터프리터를 `./venv/bin/python`으로 지정하면 터미널에서 venv 활성화 없이도 동일 환경으로 실행됩니다.

## Usage

```bash
source venv/bin/activate
python src/app.py
```

```
Ask a question: 비올라 프로젝트 구조는?
Searching...

Answer: (한국어로 위키 맥락 기반 답변)
```

`exit` 입력 시 종료.

## Configuration

`.env.example`을 복사한 뒤 아래 항목을 확인하세요.

### 사용자가 직접 설정해야 하는 항목

| 변수 | 설명 |
|------|------|
| **`WIKI_DIR`** | **본인 위키 폴더 경로** (필수). 팀마다 경로가 다릅니다. |
| `OLLAMA_LLM_MODEL` | 답변 생성용 채팅 모델 (기본: `qwen2.5:7b`) |
| `OLLAMA_EMBED_MODEL` | 검색용 임베딩 모델 (기본: `bge-m3`) |
| `RESPONSE_LANGUAGE` | 답변 언어 — `ko` 또는 `en` (기본: `ko`) |

### Ollama 기본값

| Variable | Default | Description |
|----------|---------|-------------|
| `WIKI_DIR` | `./wiki` | 위키 경로 (**반드시 본인 경로로 변경**) |
| `PERSIST_DIR` | `.chroma` | 벡터 DB 저장 경로 |
| `LLM_PROVIDER` | `ollama` | `ollama` \| `huggingface` \| `openai` \| `cursor` |
| `EMBED_PROVIDER` | `ollama` | `ollama` \| `huggingface` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama 엔드포인트 |
| `OLLAMA_LLM_MODEL` | `qwen2.5:7b` | Chat model (answers) |
| `OLLAMA_EMBED_MODEL` | `bge-m3` | Embedding model (retrieval) |
| `RESPONSE_LANGUAGE` | `ko` | Answer language |

Legacy aliases `LLM_MODEL` / `EMBED_MODEL` still map to the Ollama settings above.

### 모델 선택 가이드

**Chat (답변)** — `OLLAMA_LLM_MODEL`:
- `qwen2.5:7b` — 기본, 가볍고 한국어 양호 (~5 GB)
- `qwen2.5:3b` — 더 가벼움 (~2 GB)
- `qwen3.6:27b` — 품질 우선, 느림 (~17 GB). `qwen3.6:7b` 태그는 없음.

**Embedding (검색)** — `OLLAMA_EMBED_MODEL`:
- `bge-m3` — 한국어/다국어 위키 권장
- `nomic-embed-text` — 영어 위키 위주

### Other Providers

| Provider | Packages | API key |
|----------|----------|---------|
| Ollama | `requirements-ollama.txt` | None |
| Hugging Face | `requirements-extra.txt` | `HUGGINGFACEHUB_API_TOKEN` |
| OpenAI | `requirements-extra.txt` | `OPENAI_API_KEY` |
| Cursor | `requirements-extra.txt` | `CURSOR_API_KEY` |

See `.env.example` for `HF_*`, `OPENAI_*`, `CURSOR_*` variables.

## Project Structure

```
src/
├── app.py          # CLI entry point
├── config.py       # .env / .env.local settings
├── loader.py       # Load & chunk markdown
├── vectorstore.py  # Chroma build/load
├── chain.py        # RAG chain (ko/en prompts)
└── providers/      # LLM & embedding factories, Ollama health check
```

## Architecture

```
Wiki (.md) → loader → embeddings → Chroma (.chroma/) → RAG chain → LLM answer
```

On startup, `app.py` validates Ollama models, loads or rebuilds the index, and runs an interactive Q&A loop. Top 3 similar chunks are retrieved per question.

## Troubleshooting

### Ollama에 연결되지 않음

**증상**: `Connection refused`, `Cannot reach Ollama`

```bash
ollama list   # Ollama가 실행 중인지 확인
```

macOS는 Ollama 앱 실행, Linux는 `systemctl start ollama`. `.env`의 `OLLAMA_BASE_URL`도 확인하세요.

### 모델을 찾을 수 없음

**증상**: `model "qwen2.5:7b" not found`, `Required Ollama model(s) are not installed`

RAG에는 **채팅 모델 1개 + 임베딩 모델 1개**가 필요합니다. 앱 시작 시 `ollama pull` 명령을 안내합니다.

```bash
ollama pull qwen2.5:7b
ollama pull bge-m3
python src/app.py --rebuild
```

### `"bge-m3" does not support chat`

**원인**: Embedding 모델을 `OLLAMA_LLM_MODEL`에 설정함.

```env
OLLAMA_LLM_MODEL=qwen2.5:7b    # chat
OLLAMA_EMBED_MODEL=bge-m3      # embedding
```

### 패키지 / venv 오류

**증상**: `No module named 'dotenv'`, `externally-managed-environment`

```bash
source venv/bin/activate
pip install -r requirements-ollama.txt
python src/app.py
```

또는 `./venv/bin/python src/app.py`

### 벡터 DB 오류 / 검색 품질 저하

```bash
rm -rf .chroma
python src/app.py
```

임베딩 모델을 바꾼 뒤에도 이상하면 위 명령으로 전체 재인덱싱하세요.

### 답변 품질이 낮음

- 위키에 해당 내용이 있는지 확인
- 한국어 위키: `OLLAMA_EMBED_MODEL=bge-m3` 유지
- LLM만 업그레이드: `OLLAMA_LLM_MODEL=qwen3.6:27b` (느려짐)

## License

This project is provided as-is for personal use.
