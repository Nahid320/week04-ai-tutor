# Week 4: Deployable AI Tutor (Portfolio Project)

An LLM-powered Streamlit chat interface using the OpenAI Responses API, with:

- **Streaming** through `response.output_text.delta`
- **Conversation memory**: recent-window or summarization mode
- **Reliability**: SDK automatic transient-failure retries; explicit stream completion checks
- **Monitoring**: session-level input/output token counters
- **Evaluation**: six-question live smoke test (optional, billed)
- **Offline CI**: unit tests running on GitHub Actions
- **Deployment**: Streamlit Community Cloud (keep the hosted app private)

## Local setup: Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set `OPENAI_API_KEY` to a real key. Do not commit it.
Run:

```powershell
streamlit run app.py
```

For tests (no API requests):

```powershell
python -m unittest discover -s tests -v
```

Optional live smoke-test (six API requests):

```powershell
python evaluate_live.py
```

The local `outputs/` directory is ignored by Git; never upload private prompts or conversation data.

## Publish repository to GitHub

Create an **empty** repository called `week04-ai-tutor` on GitHub (no generated README).
Then execute these commands from the project folder:

```powershell
git init
git branch -M main
git add .
git diff --cached --name-only
# Check carefully: neither .env nor .venv nor .streamlit/secrets.toml should appear.
git commit -m "Build reliable cloud-deployable AI tutor"
git remote add origin https://github.com/YOUR-USERNAME/week04-ai-tutor.git
git push -u origin main
```

If you have already initialized this repository, do **not** run `git init` and `git remote add origin` again. Instead, just add, commit, and push. Never push credentials.

GitHub Actions runs `python -m unittest discover -s tests -v` on every push and pull request.
The CI workflow does **not** require an API key because tests use simulated model responses.

## Deploy on Streamlit Community Cloud

1. Open https://share.streamlit.io/ and link your GitHub account.
2. Select **Create app** and choose the repository `week04-ai-tutor`, branch `main`, entrypoint `app.py`.
3. In **Advanced settings → Secrets**, add the following TOML (**with your real key**, not the placeholder):

   ```toml
   OPENAI_API_KEY = "YOUR_PRIVATE_KEY"
   OPENAI_MODEL = "gpt-6-luna"
   ```

   Root-level Streamlit secrets are exposed as environment variables, which the app reads via `os.getenv()`.
4. Deploy the app and open the assigned `*.streamlit.app` URL.
5. In **App settings → Sharing**, select **Only specific people can view this app** and verify access. A public GitHub repo does not require a public running app.
6. Set a conservative **enforced hard spend limit** on the OpenAI API project at https://platform.openai.com/ . An alert alone doesn't limit charges.
7. Test with a fictional prompt and inspect logs if deployment fails. Never send secrets to logs or chats.

**Warning:** If your app is public, anyone may trigger paid model calls under your key. This demo does not implement robust authentication, rate limiting, or abuse prevention. Keep the hosted app private; do not present it as a secure multi-tenant production service. Streamlit Community Cloud currently allows only one private app per account; confirm current limitations before relying on it.

## Code architecture

| File | Purpose |
|------|---------|
| `app.py` | Minimal UI and session state |
| `conversation.py` | Sliding window and summary context |
| `llm_backend.py` | Response streaming and summarization API calls |
| `error_policy.py` | Safe error descriptions |
| `evaluate_live.py` | Six-question live smoke test |
| `quality_eval.py`, `eval_cases.json` | Metrics and test inputs |
| `tests/` | Offline automated tests |
| `.github/workflows/tests.yml` | GitHub Actions CI |

## Reliability caveats

- Sliding windows bound **message count**, not strict token count.
- Summarizing old context can lose detail and adds token usage.
- Streamed partial replies are not retained unless the response completes.
- Session counters aren't a billing ledger; inspect the API usage dashboard.
- `store=False` controls response storage for later retrieval, not all provider-side retention.
- The live smoke test is illustrative, not a comprehensive benchmark.

## Future upgrades

Add proper user authentication, rate limiting, stronger budget controls, evaluation on a representative dataset, tracing and monitoring, and server-side persistence.
