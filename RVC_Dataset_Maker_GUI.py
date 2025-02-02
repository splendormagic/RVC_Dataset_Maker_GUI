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
    <h1 style="color: #333; font-family: Arial, sans-serif;">Bahaa Mahmoud TUT - Dataset Maker For RVC</h1>
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
