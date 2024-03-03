# Local LLM-based Voice Chatbot on Raspberry Pi

This is a demo of an LLM-based voice chatbot that runs locally on Raspbbery Pi.
It is based on Nick Bild's [Local LLM Assistant](https://github.com/nickbild/local_llm_assistant) project, with some modifications and enhancements.

## Introduction

The pipeline is fairly simple:

- ASR: OpenAI Whisper, "base" model.
- LLM: TinyLlama 1.1B, wrapped using [llamafile](https://github.com/Mozilla-Ocho/llamafile)
- TTS: Replaced `espeak` with [piper](https://github.com/rhasspy/piper), which has a much better voice quality.

The control of the bot is also enhanced. Originally it was "push-to-trigger" mode with a fixed (3-second) length of recording.
I changed it into a true "push-to-talk" mode, allowing me to record voice with arbitrary length.

## Usage

### Hardware setup

I used Raspberry Pi 4 (4GB RAM), but 3 might also work if it has enough RAM.

For audio you need a USB microphone and a speaker.

For the push button:
- Connect the "button" wire to GPIO 8
- Connect the "ground" wire to GPIO 6

### Install Ubuntu server on Raspberry Pi

I used the pre-installed ARM64 image:

https://cdimage.ubuntu.com/releases/jammy/release/

### Install dependencies

```bash
sudo apt update
sudo apt install ffmpeg espeak python3-pip python3-pyaudio cmake

# Rust may also be needed
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"

pip3 install openai openai-whisper RPi.GPIO pyaudio
```

### Download LLM model

Download the TinyLlama model wrapped with [llamafile](https://github.com/Mozilla-Ocho/llamafile), which can be executed directly on Raspberry Pi.

Go to [llamafile](https://github.com/Mozilla-Ocho/llamafile) website and download the [TinyLlama image](https://huggingface.co/jartine/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/TinyLlama-1.1B-Chat-v1.0.Q5_K_M.llamafile?download=true).

Make sure it is executable:

```bash
chmod +x TinyLlama-1.1B-Chat-v1.0.Q5_K_M.llamafile
```

### Launch the LLM in server mode

```bash
./TinyLlama-1.1B-Chat-v1.0.Q5_K_M.llamafile
```

By default, it will launch a server listening on local port 8080.

### Install TTS program and model (piper)

Download the [ARM64 binary](https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_arm64.tar.gz), extra it to `/home/ubuntu`.
The `piper` binary should be located in `/home/ubuntu/piper/`.

Download the TTS model, for example:

https://huggingface.co/rhasspy/piper-voices/tree/v1.0.0/en/en_US/amy/medium

Download both `onnx` and `json` files, and put them under `/home/ubuntu/piper`.

### Launch the voice chatbot

```
python3 chatbot.py
```

### Talk to the chatbot

Push the button, speaker your request, and release the button.

Be paitent - it will take a while for the device to transcribe the request and generate a response.

## Roadmap

To be added.

## Known Issues

I've seen the bot to get stuck on some queries. Need more debugging to understand why...
