# retail-management-copilot

A self-contained retail operations copilot prototype for small store teams.

Run the Python backend locally, then open the app:

```bash
python3 server.py
```

Open http://localhost:3000. The demo includes three stores, catalogue and sales/inventory examples, an attention queue, and an evidence-backed question flow. The backend exposes `GET /api/dashboard` and `POST /api/ask`.

## Deploy to Vercel

Import this repository into Vercel. The static frontend is served from the project root, while `api/dashboard.py` and `api/ask.py` run as Python serverless functions. No build command or environment variables are required.

For a CLI deployment:

```bash
npx vercel
npx vercel --prod
```

## Deploy to Streamlit Community Cloud

1. Push this repository to GitHub.
2. Open [share.streamlit.io](https://share.streamlit.io/) and choose this repository.
3. Set the main file path to `streamlit_app.py`.
4. Deploy. Streamlit installs `requirements.txt` automatically.

Run it locally with:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
