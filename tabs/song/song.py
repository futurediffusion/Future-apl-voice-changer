import os
import json
import datetime
import requests
import gradio as gr

from assets.i18n.i18n import I18nAuto

i18n = I18nAuto()

SYSTEM_MESSAGE = (
    "Eres un asistente especializado en composici\xc3\xb3n musical. "
    "Eval\xc3\xbaas rima, m\xc3\xa9trica y coherencia tem\xc3\xa1tica en cada respuesta."
)

PROMPTS = {
    "Intro": (
        "Estructura una introducci\xc3\xb3n de canci\xc3\xb3n que transmita {text}. "
        "Mant\xc3\xa9n un patr\xc3\xb3n de rima ABAB y comenta la m\xc3\xa9trica y las s\xc3\xadlabas de cada l\xc3\xadnea."
    ),
    "Coro": (
        "Genera un coro pegajoso sobre {text} con rima consonante y entre 8-10 s\xc3\xadlabas por l\xc3\xadnea. "
        "Devuelve el texto y su an\xc3\xa1lisis de rima y m\xc3\xa9trica."
    ),
    "Estrofa": (
        "Escribe una estrofa que contin\xc3\xbae la historia de {text} en verso libre, "
        "analizando rimas y n\xc3\xbamero de s\xc3\xadlabas. Indica sugerencias de mejora."
    ),
    "Mejora": (
        "Revisa el siguiente fragmento para mejorar la rima, m\xc3\xa9trica y coherencia tem\xc3\xa1tica. "
        "Sugiere ajustes manteniendo la misma idea. {text}"
    ),
}


def _build_payload(content: str) -> str:
    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": content},
        ],
        "model": "llama-3.1-70b-versatile",
        "temperature": 0.6,
        "max_tokens": 600,
        "top_p": 1,
        "stream": False,
        "stop": None,
    }
    return json.dumps(payload)


def _call_groq(content: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "GROQ_API_KEY not configured"
    json_payload = _build_payload(content)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            data=json_payload,
            timeout=60,
        )
    except requests.RequestException as err:
        return f"API request failed: {err}"

    if response.status_code != 200:
        return f"API error: {response.status_code} {response.text}"

    try:
        text = response.json()["choices"][0]["message"]["content"]
    except Exception:
        return "Invalid API response"

    _save_response(text)
    return text


def _save_response(text: str) -> None:
    directory = os.path.join("assets", "lyrics_responses")
    os.makedirs(directory, exist_ok=True)
    filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S.txt")
    path = os.path.join(directory, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def generate_lyrics(category: str, user_text: str) -> str:
    template = PROMPTS.get(category)
    if not template:
        return "Categor\xc3\xada no v\xc3\xa1lida"
    prompt = template.format(text=user_text)
    return _call_groq(prompt)


def song_tab():
    gr.Markdown(i18n("## Generador de Canciones"))
    with gr.Column():
        category = gr.Radio(
            ["Intro", "Coro", "Estrofa", "Mejora"], label=i18n("Categor\xc3\xada"), value="Intro"
        )
        user_text = gr.Textbox(label=i18n("Tema o fragmento"))
        generate_button = gr.Button(i18n("Generar"))
        output_box = gr.Textbox(label=i18n("Resultado"), lines=8)
    generate_button.click(
        fn=generate_lyrics, inputs=[category, user_text], outputs=output_box
    )
