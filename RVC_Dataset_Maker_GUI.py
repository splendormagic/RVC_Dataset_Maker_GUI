# Settings

import os
import shutil
from pydub import AudioSegment
from pydub.silence import detect_silence
import subprocess

# Function to clear and recreate a directory
def clear_directory(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory, exist_ok=True)

# Function to merge uploaded audio files
def merge_audio_files(uploaded_files):
    clear_directory('uploads')
    clear_directory('merged')

    # Save uploaded files to the "uploads" directory
    for file in uploaded_files:
        filename = os.path.basename(file.name)
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext in ['.mp3', '.wav']:
            shutil.move(file.name, os.path.join('uploads', filename))

    # Merge the uploaded audio files into one MP3 file
    merged_audio = AudioSegment.empty()
    for filename in os.listdir('uploads'):
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext in ['.mp3', '.wav']:
            audio = AudioSegment.from_file(os.path.join('uploads', filename))
            merged_audio += audio

    # Export the merged audio to the "merged" directory as MP3
    output_path = os.path.join('merged', 'merged_audio.mp3')
    merged_audio.export(output_path, format='mp3')
    return output_path

# Function to extract vocals and remove silence
def process_audio(merged_audio_path):
    # Clear and create "vocals" directory
    clear_directory('vocals')

    # Use demucs to separate vocals
    demucs_model = "htdemucs"
    subprocess.run(f"python3 -m demucs.separate -n {demucs_model} -o vocals --two-stems=vocals {merged_audio_path}", shell=True)

    # Define paths for silence removal
    input_vocals_path = '/content/RVC_Dataset_Maker_GUI/vocals/htdemucs/merged_audio/vocals.wav'
    output_vocals_path = '/content/RVC_Dataset_Maker_GUI/vocals/vocals_cut.wav'
    silence_thresh = -40  # silence threshold (in dB)
    min_silence_len = 10  # minimum length of silence (in ms)

    # Load the vocals audio file
    vocals_audio = AudioSegment.from_wav(input_vocals_path)

    # Detect silence moments
    silence_ranges = detect_silence(vocals_audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)

    # Invert silence ranges to non-silence ranges
    non_silence_ranges = []
    start = 0
    for start_silence, end_silence in silence_ranges:
        if start < start_silence:
            non_silence_ranges.append((start, start_silence))
        start = end_silence
    if start < len(vocals_audio):
        non_silence_ranges.append((start, len(vocals_audio)))

    # Concatenate non-silence audio segments
    vocals_cut = AudioSegment.empty()
    for start, end in non_silence_ranges:
        vocals_cut += vocals_audio[start:end]

    # Export the result
    vocals_cut.export(output_vocals_path, format='wav')

    # Convert WAV to MP3
    audio = AudioSegment.from_wav(output_vocals_path)
    dataset_path = '/content/RVC_Dataset_Maker_GUI/dataset.mp3'
    audio.export(dataset_path, format='mp3')

    return dataset_path


import gradio as gr

# Gradio UI function without progress bar
def gradio_interface(uploaded_files):
    # Step 1: Merge uploaded audio files
    merged_audio_path = merge_audio_files(uploaded_files)

    # Step 2: Process audio to extract vocals and remove silence
    dataset_path = process_audio(merged_audio_path)

    # Return the path to the processed dataset and an audio preview
    return dataset_path, dataset_path

# Define Gradio inputs and outputs
inputs = gr.File(file_count="multiple", label="Upload Audio Files Or Songs")
outputs = [
    gr.File(label="Dataset File"),
    gr.Audio(label="Preview Dataset File")
]

# Custom HTML header
html_header = """
<div style="text-align: center; padding: 20px; background-color: #f0f0f0; border-radius: 10px;">
    <h1 style="color: #333; font-family: Arial, sans-serif;">Bahaa Ai - Dataset Maker For RVC</h1>
    <p style="color: #666; font-family: Arial, sans-serif;">
        This code cleans up your uploaded audio files from noise and music, removes silence and compiles it all into a single audio file that you can use for training directly.
    </p>
</div>
"""

# Create Gradio interface
interface = gr.Interface(
    fn=gradio_interface,
    inputs=inputs,
    outputs=outputs,
    title="",  # Remove the default title
    description="",  # Remove the default description
    flagging_mode="never"  # Disable the flagging feature
)

# Add the HTML header to the interface
interface = gr.Blocks()
with interface:
    gr.HTML(html_header)  # Add the custom HTML header
    with gr.Row():
        with gr.Column():
            gr.Interface(
                fn=gradio_interface,
                inputs=inputs,
                outputs=outputs,
                flagging_mode="never"
            )

# Launch the interface
interface.launch(share=True, inline=False)
