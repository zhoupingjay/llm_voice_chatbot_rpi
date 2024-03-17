#!/bin/bash

# Create the temp directory for audio recording
[ -d recording ] || mkdir recording
# If you want to mount the recording directory in RAM:
# sudo mount -t tmpfs -o size=10M none ./recording/

# Build ASR: whisper.cpp
if [ ! -e ./whisper.cpp/main ]; then
    echo "Building whisper.cpp"
    pushd whisper.cpp
    make -j main
    # ASR binary: ./whisper.cpp/main
    popd
else
    echo "whisper.cpp already built"
fi
# Download the ASR model (tiny)
if [ ! -e ./whisper.cpp/models/ggml-tiny.bin ]; then
    pushd whisper.cpp
    # The model will be downloaded to ./whisper.cpp/models/ggml-tiny.bin
    ./models/download-ggml-model.sh tiny
    popd
else
    echo "ASR model already downloaded"
fi

# Download TinyLlama-1.1B (llamafile wrap)
if [ ! -e llm/TinyLlama-1.1B-Chat-v1.0.Q5_K_M.llamafile ]; then
    echo "Downloading TinyLlama"
    [ -d llm ] || mkdir llm
    wget https://huggingface.co/jartine/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/TinyLlama-1.1B-Chat-v1.0.Q5_K_M.llamafile?download=true -O llm/TinyLlama-1.1B-Chat-v1.0.Q5_K_M.llamafile
    chmod +x llm/TinyLlama-1.1B-Chat-v1.0.Q5_K_M.llamafile
else
    echo "TinyLlama already downloaded"
fi

# Download TTS: Piper for Raspberry Pi 4 (ARM64)
if [ ! -e ./piper/piper ]; then
    echo "Downloading piper"
    wget https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_arm64.tar.gz
    # The binary will be under ./piper
    tar zxf piper_arm64.tar.gz
else
    echo "piper already downloaded"
fi
# Download the TTS model
if [ ! -e ./piper/en_US-amy-medium.onnx ]; then
    echo "Downloading TTS model"
    wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/medium/en_US-amy-medium.onnx?download=true -O ./piper/en_US-amy-medium.onnx
    wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/medium/en_US-amy-medium.onnx.json?download=true -O ./piper/en_US-amy-medium.onnx.json
else
    echo "TTS model already downloaded"
fi

