import torch
from transformers import AutoTokenizer, AutoProcessor, LlavaForConditionalGeneration, BitsAndBytesConfig,\
AutoModelForSeq2SeqLM
from PIL import Image
from fastapi import FastAPI
import gradio as gr
import os
import torch

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



def gujarati_to_english(gujarati_text: str) -> str:
    """
    Function to translate  Gujarati text to English.\n
    Args:
        gujarati_text: str = Gujarati Text
    Returns:
        question_english
    """

    tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M", use_auth_token=False, src_lang= "gu_IN")
    model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M", use_auth_token=False)

    inputs = tokenizer(gujarati_text, return_tensors="pt")

    translated_tokens = model.generate(**inputs, forced_bos_token_id=tokenizer.lang_code_to_id["eng_Latn"], max_length=100)

    question_english = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]

    return question_english


def english_to_gujarati(english_text: str):
    """
    Function to translate English to Gujarati
    Args:
        english_text: str = English Text
    Returns:
        answer_english
    """

    tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M", use_auth_token=False, src_lang= "eng_Latn")
    model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M", use_auth_token=False)

    inputs = tokenizer(english_text, return_tensors="pt")

    translated_tokens = model.generate(**inputs, forced_bos_token_id=tokenizer.lang_code_to_id["guj_Gujr"], max_length=100)

    answer_gujarati = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]

    return answer_gujarati


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
    # inputs = inputs.to(device)
    generate_ids = model.generate(**inputs, max_new_tokens=200)
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

