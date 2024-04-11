# Model Ducking

An extension for [oobabooga/text-generation-webui](https://github.com/oobabooga/text-generation-webui) that allows the currently loaded model to automatically unload itself immediately after a prompt is processed, thereby freeing up VRAM for use in other programs. It automatically reloads the last model upon sending another prompt.

This should theoretically help systems with limited VRAM run multiple VRAM-dependent programs in parallel.

## Example Scenario

The following scenario should paint a clearer picture of what the extension does.

1. User creates prompt. System generates a response.
2. __Model Ducking__ unloads the current model, freeing up VRAM.
3. System runs Local TTS program (i.e. XTTSv2) to automatically voice the system's response. 
4. User runs Stable-Diffusion to generate an image based on response.
5. User creates another prompt.
6. __Model Ducking__ reloads the last model. VRAM is taken up by the model again.
7. System generates a response.
8. __Model Ducking__ unload the model again, freeing up VRAM.

## Side-effect

There is an obvious additional latency after subsequent prompts to reload the last model used. Do note that the latency is limited to the reloading of the last model, and does not directly impact the model's ability to generate responses (i.e. tokens per second).

Because of this side-effect, I do not recommend turning on features that automatically asks the AI to "continue" their response (i.e. SillyTavern's Auto-Continue feature), as Model Ducking will unload and reload your model in between the intitially generated response and the subsequent attempts to continue.