#
# Local LLM-based Voice Assistant running on Raspberry Pi
# 
# Ping Zhou
# https://github.com/zhoupingjay/llm_voice_chatbot_rpi
#
# It is inspired and based on Nick Bild's "Local LLM Assistant", with some enhancements:
# https://github.com/nickbild/local_llm_assistant


import os
from openai import OpenAI
import pyaudio
import wave
import whisper
import RPi.GPIO as GPIO
import time
import argparse
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--llm_port', default=8080, help='Local port of the LLM server.', type=int)
parser.add_argument('--tts', default='~/piper/piper', help='TTS program to use for speaking back.', type=str)
parser.add_argument('--tts_model', default='~/piper/en_US-amy-medium.onnx', help='TTS model to use for speaking back.', type=str)

args = parser.parse_args()

BUTTON = 8
GPIO.setmode(GPIO.BOARD)
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Available models:
# ['tiny.en', 'tiny', 'base.en', 'base', 'small.en', 'small', 'medium.en', 'medium', 'large-v1', 'large-v2', 'large-v3', 'large']
asr_model = whisper.load_model("base")

def record_wav():
    form_1 = pyaudio.paInt16
    chans = 1
    samp_rate = 16000
    chunk = 4096
    wav_output_filename = 'input.wav'

    audio = pyaudio.PyAudio()

    # Create pyaudio stream.
    stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                        # input_device_index = 1,\
                        input = True, \
                        frames_per_buffer=chunk)
    print("recording")
    frames = []

    # Push-to-talk style: record until the button is released.
    while GPIO.input(BUTTON) == GPIO.LOW:
        data = stream.read(chunk)
        frames.append(data)

    print("finished recording")

    # Stop the stream, close it, and terminate the pyaudio instantiation.
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the audio frames as .wav file.
    wavefile = wave.open(wav_output_filename,'wb')
    wavefile.setnchannels(chans)
    wavefile.setsampwidth(audio.get_sample_size(form_1))
    wavefile.setframerate(samp_rate)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()

    return frames

def main():
    client = OpenAI(
        base_url=f"http://127.0.0.1:{args.llm_port}/v1",
        api_key = "sk-no-key-required"
    )

    while(True):
        print("Ready, push to talk...")
        if GPIO.input(BUTTON) == GPIO.LOW:
            # Record and transcribe the request.
            record_wav()
            result = asr_model.transcribe("input.wav")
            print("Transcription: {0}".format(result["text"]))
            request = result["text"]

            # Send the query to LLM.
            completion = client.chat.completions.create(
                model="LLaMA_CPP",
                messages=[
                    {"role": "system", "content": "Your name is Amy. You are an AI assistant. Your priority is helping users with their requests."},
                    {"role": "user", "content": request}
                ],
                # temperature = 0.7,
            )

            # Speak back the response.
            # Remove the double quote signs from the string, so it can be passed to the shell for TTS.
            response_quoted = completion.choices[0].message.content.replace('"', '')
            print("LLM response: ")
            print("=========================")
            print(response_quoted)
            print("=========================")
            os.system('echo "{0}" | {1} --model {2} --output-raw | aplay -r 22050 -f S16_LE -t raw -'.format(response_quoted, args.tts, args.tts_model))
        else:
            # So we don't occupy the CPU...
            time.sleep(0.2)


if __name__ == "__main__":
    main()
