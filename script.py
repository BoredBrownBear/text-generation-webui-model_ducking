import sys

import gradio as gr
from fastapi import Request
from fastapi.responses import StreamingResponse

from extensions.openai import script
from modules import shared
from modules.logging_colors import logger
from modules.models import load_model, unload_model

params = {
    "display_name": "Model Ducking",
    "activate": False,
    "is_api": False,
    "last_model": "",
}


def load_last_model():
    if not params["activate"]:
        return False

    if shared.model_name != "None" or shared.model is not None:
        logger.info(
            f'"{shared.model_name}" is currently loaded. No need to reload the last model.'
        )
        return False

    if params["last_model"]:
        shared.model, shared.tokenizer = load_model(params["last_model"])

    return True


def unload_model_all():
    if shared.model is None or shared.model_name == "None":
        return

    params["last_model"] = shared.model_name

    unload_model()

    logger.info("Model has been temporarily unloaded until next prompt.")


def history_modifier(history):
    load_last_model()

    return history


def output_modifier(string, state, is_chat=False):
    if not params["activate"]:
        return string

    if not params["is_api"]:
        unload_model_all()

    return string


def ui():
    with gr.Row():
        activate = gr.Checkbox(value=params["activate"], label="Activate Model Ducking")
        is_api = gr.Checkbox(value=params["is_api"], label=" Using API")

    activate.change(lambda x: params.update({"activate": x}), activate, None)
    is_api.change(lambda x: params.update({"is_api": x}), is_api, None)


async def after_openai_completions(request: Request, call_next):
    if request.url.path in ("/v1/completions", "/v1/chat/completions"):
        load_last_model()

        response = await call_next(request)
        
        async def stream_chunks():
            async for chunk in response.body_iterator:
                yield chunk

            if params["activate"] and params["is_api"]:
                unload_model_all()

        return StreamingResponse(stream_chunks())

    return await call_next(request)


script_module = sys.modules["extensions.openai.script"]
script_module.app.middleware("http")(after_openai_completions)
