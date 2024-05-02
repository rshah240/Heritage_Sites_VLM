import torch
from transformers import AutoTokenizer, AutoProcessor, LlavaForConditionalGeneration, BitsAndBytesConfig
from PIL import Image
from fastapi import FastAPI
import gradio as gr
import os
from openai import OpenAI

model_id = "rshah240/llava_historical_images"
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16
)
model = LlavaForConditionalGeneration.from_pretrained(model_id,
                                                    quantization_config=quantization_config,
                                                    torch_dtype=torch.float16)
processor = AutoProcessor.from_pretrained("llava-hf/llava-1.5-7b-hf")


app = FastAPI()

client = OpenAI(api_key="")

def gujarati_to_english(gujarati_text):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Translate the following Gujarati text to English: {gujarati_text}",
            }
        ],
        model="gpt-3.5-turbo",
    )
    response = chat_completion.choices[0].message.content
    return response


def english_to_gujarati(english_text):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Translate the following English text to Gujarati: {english_text}",
            }
        ],
        model="gpt-3.5-turbo",
    )
    response_guj = chat_completion.choices[0].message.content
    return response_guj


def get_answer(image: Image, question_gujarati: str) -> str:
    """
    Function to get the answer the from the image and question
    Args:
        image: Image: = Input image
        question: str = Question asked to the VLM
    Returns:
        Answer
    """

    question_english = gujarati_to_english(question_gujarati)

    prompt =f"USER: <image>\n{question_english} ASSISTANT:"
    inputs = processor(text=prompt, images=image, return_tensors="pt")
    generate_ids = model.generate(**inputs, max_new_tokens=100)
    answer = processor.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    answer_english = answer.split("ASSISTANT:")[-1]

    answer_gujarati = english_to_gujarati(answer_english)

    return answer_gujarati


iface = gr.Interface(
    fn=get_answer,
    inputs=[gr.Image(type="pil"), gr.Textbox(label="Question")],
    outputs=gr.Textbox(label="Answer"),
    title="Visual Question Answering",
    description="Upload an image and ask a question related to the image. The AI will try to answer it."
)

gr.mount_gradio_app(app,iface, "/gradio")

