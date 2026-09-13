# LLM Integration Healthcare Chatbot

A safety-first healthcare conversation API built with Python, FastAPI, and a provider-agnostic LLM adapter.

> **Important:** This is an educational software project, not a medical device or a source of medical advice. It must not be used for diagnosis, treatment decisions, prescriptions, or emergency response.

## What is included

- FastAPI service with `/health` and `/chat` endpoints.
- Provider-agnostic LLM client using an OpenAI-compatible HTTP API.
- Deterministic mock mode for local demos and CI.
- Emergency-language detection with a fixed escalation response.
- System instructions that limit diagnosis, prescriptions, and collection of identifiers.
- Pydantic request/response validation and bounded message length.
- Tests for safety behavior and HTTP behavior.
- GitHub Actions CI using Python 3.11.
- No patient data, credentials, or external service keys in the repository.

## Architecture

```text
HTTP client
    |
    v
FastAPI route  --->  safety assessment  --->  emergency response (if needed)
    |                         |
    |                         +------------> safe system policy + user message
    v                                                   |
LLM client protocol <----------------------------------+
    |
    +--> mock provider (default)
    +--> OpenAI-compatible provider (configured by environment)
```

The safety gate runs before the model call. A production implementation should add a human escalation workflow, identity and consent controls, audit logging with a documented retention policy, a clinical review process, and formal security/compliance review before handling protected health information.

## Quick start

Requires Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload
```

The API starts at `http://127.0.0.1:8000`.

Try the mock provider:

```bash
curl http://127.0.0.1:8000/health

curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What are common ways to prepare for a primary-care visit?"}'
```

To use an OpenAI-compatible provider, set these values in `.env`:

```dotenv
LLM_PROVIDER=openai_compatible
LLM_BASE_URL=https://your-provider.example/v1
LLM_API_KEY=replace-me
LLM_MODEL=your-model-name
```

The adapter sends a standard `POST /chat/completions` request. Keep secrets in a local environment or a managed secret store; never commit `.env`.

## API contract

### `GET /health`

Returns service status and the selected provider without exposing credentials.

### `POST /chat`

Request:

```json
{
  "message": "What questions should I ask my doctor about sleep?"
}
```

Response shape:

```json
{
  "answer": "...",
  "safety_notice": "Educational information only; not medical advice.",
  "escalation_required": false,
  "blocked": false,
  "flags": [],
  "request_id": "..."
}
```

Emergency language produces a non-model response with `escalation_required: true`. The message directs the person to local emergency services rather than attempting triage or treatment.

## Safety and privacy decisions

- The service does not log request text.
- The API does not ask for names, contact details, medical record numbers, or other identifiers.
- Input is length-bounded to reduce accidental data transfer and prompt abuse.
- Emergency keywords are a conservative signal, not a clinical classifier.
- The model is instructed to state limitations, avoid diagnosis, and avoid medication dosing or prescription instructions.
- A real deployment still needs authentication, rate limiting, abuse monitoring, encrypted transport, a reviewed data-retention policy, and appropriate legal/compliance controls.

## Test and quality checks

```bash
pytest
```

Run the same test command in CI on every push and pull request.

## Roadmap for a production handoff

1. Add authentication, consent, rate limiting, and request correlation.
2. Add a reviewed escalation integration with human operators.
3. Add evaluation fixtures for refusal, hallucination, prompt injection, and emergency-language cases.
4. Add retrieval over reviewed public health content with source citations.
5. Add red-team testing, threat modeling, monitoring, and a formal privacy review.

## License

MIT. See `LICENSE`.