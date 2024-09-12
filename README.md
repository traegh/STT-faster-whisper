# Transcribe.py

Transcribe.py is a real-time audio transcription tool based on the Faster Whisper 1.0.3 model. It continuously listens for audio input, transcribes it, and outputs the text to both the console and a file.

## ⚠️ Security Warning

**IMPORTANT:** Always exercise caution when downloading and running scripts from the internet, especially those containing `.bat` files or other executable scripts. 

- **Always review the contents** of any `.bat` files or scripts before running them.
- Malicious actors may attempt to include harmful code in these files.
- If you're unsure about the contents of a file, **do not run it**.
- Consider using a trusted antivirus program to scan downloaded files.
- When in doubt, seek advice from a knowledgeable source or the project maintainers.

Your system's security is your responsibility. Stay vigilant!

## Features

- Real-time audio transcription
- Customizable microphone selection
- Noise threshold for speech detection
- GPU acceleration support
- Ignore phrases to filter out common misinterpretations
- Console output with color-coding and timing information
- Transcription saving to a text file

## Requirements

- Python 3.7+
- CUDA-compatible GPU (recommended for optimal performance)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/transcribe-project.git
   cd transcribe-project
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install numpy pyaudio psutil gputil fuzzywuzzy pystyle faster-whisper
   ```

4. Download the Faster Whisper model:
   ```
   # The model will be downloaded automatically when first running the script
   # Alternatively, you can manually download it from the Hugging Face model hub
   ```

## Usage

1. Adjust the configuration in the `CONFIG` dictionary at the top of `transcribe.py` if needed.

2. Run the script:
   ```
   python transcribe.py
   ```

3. Start speaking, and the transcriptions will appear in the console and be saved to `transcriptions.txt`.

4. To stop the program, press `Ctrl+C`.

## Configuration

You can modify the following parameters in the `CONFIG` dictionary:

- `MICROPHONE_NAME`: Name of your input device
- `THRESHOLD_DB`: Noise threshold for speech detection
- `MODEL_SIZE`: Size of the Whisper model to use (e.g., "large-v3")
- `DEVICE`: Computation device ("cuda" for GPU, "cpu" for CPU)
- `COMPUTE_TYPE`: Precision for GPU computations ("float16" recommended)

## System Requirements

- **CPU**: Modern multi-core processor (Intel i5/i7 or AMD Ryzen 5/7)
- **RAM**: 8GB minimum, 16GB or more recommended
- **GPU**: NVIDIA GPU with CUDA support
  - Recommended: RTX 2060 or better for optimal performance
  - Minimum: GTX 1060 6GB
- **Storage**: At least 10GB of free space for the model and dependencies

## Troubleshooting

- If you encounter issues with PyAudio installation on Windows, you may need to install the appropriate PyAudio wheel for your Python version from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio).

- Make sure your CUDA drivers are up to date if using GPU acceleration.

- If the transcription quality is poor, try adjusting the `THRESHOLD_DB` value or using a different microphone.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).
