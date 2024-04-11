# Model Ducking

An extension for [oobabooga/text-generation-webui](https://github.com/oobabooga/text-generation-webui) that allows the currently loaded model to automatically unload itself immediately after a prompt is processed, thereby freeing up VRAM for use in other programs. It automatically reloads the last model upon sending another prompt.

This helps systems with limited VRAM run multiple VRAM-dependent programs at the same time.

Example use-case:
1. Create prompt. System generates a response.
    - Model Ducking then unloads the model.
2. TTS is used to speak the response. 
3. Run Stable-Diffusion to generate image based on response.
4. Create another prompt.
    - Model Ducking then reloads the model.
    