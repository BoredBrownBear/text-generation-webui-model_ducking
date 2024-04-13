import gradio as gr
import time
import os

from modules import shared, text_generation
from modules.models import load_model, clear_torch_cache
from modules.text_generation import _generate_reply
from modules.logging_colors import logger

params = {
    "display_name": "Model Ducking",
    "activate": True,
    "last_model": "",
    "timeout_seconds": int(os.getenv("MODEL_DUCKING_TIMEOUT_SECONDS", 0)),
    "in_flight": False
}

def load_last_model():
    if not params['activate']:
        return False

    reset_timeout()

    if shared.model_name != 'None' or shared.model is not None:
        logger.info(f"\"{shared.model_name}\" is currently loaded. No need to reload the last model.")
        return False

    if params['last_model']:
        shared.model, shared.tokenizer = load_model(params['last_model'])

    return True

def unload_model_except_tokenizer():
    params['last_model'] = shared.model_name

    shared.model = None
    shared.model_name = 'None'
    shared.lora_names = []
    shared.model_dirty_from_training = False
    clear_torch_cache()

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
    unload_model_except_tokenizer()
    logger.info("Model has been unloaded due to timeout.")

def output_modifier(string, state, is_chat=False):
    if not params['activate']:
        return string

    params['in_flight'] = True # request in progress
    params['timeout_start'] = time.time()
    unload_model_except_tokenizer()
    params['in_flight'] = False # request completed
    timeout_unload_model()
    logger.info("Model has been temporarily unloaded until next prompt.")

    return string

def ui():
    with gr.Row():
        activate = gr.Checkbox(value=params['activate'], label='Activate Model Ducking')

    activate.change(lambda x: params.update({"activate": x}), activate, None)

def model_ducking__generate_reply(*args, **kwargs):
    load_last_model()

    return _generate_reply(*args, **kwargs)

def model_ducking_generate_reply(*args, **kwargs):
    load_last_model()

    shared.generation_lock.acquire()
    try:
        for result in model_ducking__generate_reply(*args, **kwargs):
            yield result
    finally:
        shared.generation_lock.release()

text_generation.generate_reply = model_ducking_generate_reply
