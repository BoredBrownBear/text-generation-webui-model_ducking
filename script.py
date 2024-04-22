import sys

from fastapi import Request
from fastapi.responses import StreamingResponse

import gradio as gr
import time
import os

from extensions.openai import script
from modules import shared
from modules.logging_colors import logger
from modules.models import load_model, unload_model

params = {
    "display_name": "Model Ducking",
    "last_model": "",
    "timeout_seconds": int(os.getenv("MODEL_DUCKING_TIMEOUT_SECONDS", 0)),
    "in_flight": False,
    "activate": False,
    "is_api": False,
    "last_model": "",
}


def load_last_model():
    if not params["activate"]:
        return False

    reset_timeout()

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

def reset_timeout():
    params['timeout_start'] = time.time()

def timeout_unload_model():
    if not params['activate'] or params['in_flight']:
        return
    if params['timeout_seconds'] == 0:
        return
    if time.time() - params['timeout_start'] < params['timeout_seconds']:
        return
    if shared.model is None or shared.model_name == "None":
        return

    unload_model()
    logger.info("Model has been unloaded due to timeout.")

def output_modifier(string, state, is_chat=False):
    if not params["activate"]:
        return string

    params['in_flight'] = True # request in progress
    params['timeout_start'] = time.time()
    if not params["is_api"]:
        params['in_flight'] = False # request completed
        timeout_unload_model()

    logger.info("Model has been temporarily unloaded until next prompt.")
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
