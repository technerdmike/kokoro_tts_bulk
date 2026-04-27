from kokoro import KPipeline
import torch
import pandas as pd
from pydub import AudioSegment
import numpy as np
import os
import re

# Initialize pipeline
pipeline = KPipeline(lang_code='a')

# Load voice tensor
voice_tensor = torch.load('af_heart.pt', weights_only=True)
# voice_tensor = torch.load('ff_siwis.pt', weights_only=True) # France French

# Ensure output directory exists
output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)

# Regex to detect pause markers like [[s=500]]
pause_pattern = re.compile(r"\[\[s=(\d+)\]\]")

# Load CSV file
csv_file = "inputs_math_with_pauses.csv"
df = pd.read_csv(csv_file, header=None)

# Loop through each row
for index, row in df.iterrows():
    filename = str(row[0]).strip()
    text = str(row[1]).strip()

    print(f"Processing: {filename}")

    # Split text into segments (text + pauses)
    parts = pause_pattern.split(text)
    # Example result:
    # ["Hello", "500", "world"] → text, pause(ms), text...

    full_audio = []

    for i, part in enumerate(parts):
        if i % 2 == 0:
            # TEXT segment
            segment_text = part.strip()
            if not segment_text:
                continue

            generator = pipeline(
                segment_text,
                voice=voice_tensor,
                speed=0.9,
                split_pattern=r'\n+'
            )

            for _, _, audio in generator:
                full_audio.append(audio)

        else:
            # PAUSE segment (milliseconds)
            pause_ms = int(part)

            # Convert ms to number of samples
            sample_rate = 24000
            num_samples = int(sample_rate * (pause_ms / 1000.0))

            silence = np.zeros(num_samples, dtype=np.float32)
            full_audio.append(silence)

    if not full_audio:
        print(f"Skipping empty output for {filename}")
        continue

    # Concatenate everything
    full_audio = np.concatenate(full_audio)

    # Convert to int16
    audio_int16 = np.int16(full_audio * 32767)

    # Create AudioSegment
    audio_segment = AudioSegment(
        audio_int16.tobytes(),
        frame_rate=24000,
        sample_width=2,
        channels=1
    )

    # Save to outputs3 folder
    output_path = os.path.join(output_dir, f"{filename}.mp3")
    audio_segment.export(output_path, format="mp3")

    print(f"Saved: {output_path}")