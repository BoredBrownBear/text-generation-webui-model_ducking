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

Because of this side-effect, I do not recommend turning on features that automatically asks the AI to "continue" their response (i.e. SillyTavern's Auto-Continue feature), as Model Ducking will unload and reload your model in between the initially generated response and the subsequent attempts to continue.

## Timeout

There is a configurable timeout that can be set to only unload the model after a defined number of seconds have passed since the last prompt was processed. This is useful for users who want to keep the model loaded for a certain amount of time before unloading it, thus reducing the latency of reloading the model.

The default timeout is set to 0 seconds, meaning the model will be unloaded immediately after a prompt is processed.

You can set the timeout by setting the `MODEL_DUCKING_TIMEOUT_SECONDS` environment variable, e.g:

```shell
MODEL_DUCKING_TIMEOUT_SECONDS=300
```

## Installation

Clone this repository into the `extensions` folder of text-generation-webui, restart the app and enable the extension in the session settings.

```shell
cd /home/app/text-generation-webui/extensions
git clone --depth=1 https://github.com/BoredBrownBear/text-generation-webui-model_ducking model_ducking
```
