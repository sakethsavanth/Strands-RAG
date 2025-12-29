import gradio as gr
import requests

def ask(question):
    r = requests.post(
        "http://localhost:8000/query",
        json={"question": question}
    )
    return r.json()["answer"]

gr.Interface(
    fn=ask,
    inputs=gr.Textbox(lines=3, label="Ask your document"),
    outputs=gr.Textbox(lines=10, label="Answer"),
    title="Advanced Multi-Agent RAG"
).launch()
