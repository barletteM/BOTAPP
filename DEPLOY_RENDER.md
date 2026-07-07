# Deploy The Demo On Render

This demo can run as one Render Web Service. The Python server serves both:

- `/` and `/demo.html` for the chat page
- `/api/...` for bot answers

## Steps

1. Put this `glowdom-reception-assistant` folder in a GitHub repository.
2. Go to [Render Dashboard](https://dashboard.render.com/).
3. Click **New +** then **Web Service**.
4. Connect the GitHub repository.
5. Use these settings:

```text
Runtime: Python
Build Command: leave blank
Start Command: python backend/demo_api_server.py
Plan: Free
```

6. Click **Deploy Web Service**.
7. Render will give you a public URL like:

```text
https://glowdom-reception-demo.onrender.com
```

Share that link on WhatsApp.

## Optional OpenAI

If you want OpenAI rewriting, add this Environment Variable in Render:

```text
OPENAI_API_KEY=your_key_here
```

The demo still works without it.
