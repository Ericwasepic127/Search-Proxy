# AI-Proxy - Proxy server!
This is a Proxy Server, mainly for TermiAI

# How to use?
Click use this template above or `git clone https://github.com/Ericwasepic127/AI-Proxy.git`

Then, edit env.example file, rename to .env and follow instructions (like set GROQ_API_KEY)

After that, do
```shell
pip install -r requirements.txt
gunicorn app:app
```
**OR**

Host on platform like [Render](render.com)

and get your URL like https://ai-proxy-wk3r.onrender.com/
