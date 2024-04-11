import gradio as gr

from modules import shared, text_generation
from modules.models import load_model, clear_torch_cache
from modules.text_generation import _generate_reply
from modules.logging_colors import logger

params = {
    "display_name": "Model Ducking",
    "activate": True,
    "last_model": ""
}

def load_last_model():
    if not params['activate']:
        return False
    
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

def output_modifier(string, state, is_chat=False):
    if not params['activate']:
        return string
    
    unload_model_except_tokenizer()
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
