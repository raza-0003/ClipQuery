# ClipQuery

ClipQuery is an AI-powered video assistant built with Python, Streamlit, LangChain, Mistral AI, Whisper, and ChromaDB. It extracts audio from YouTube videos or local media files, transcribes speech, generates summaries, identifies action items, decisions, open questions, and enables follow-up chat through a RAG pipeline.

## What it does

- Accepts a YouTube URL or a local video/audio file path
- Downloads and converts audio into WAV format
- Splits audio into manageable chunks
- Transcribes speech using Whisper for English and Sarvam for Hinglish
- Generates a session title from the transcript
- Produces a detailed meeting summary
- Extracts action items, key decisions, and unresolved questions
- Builds a RAG chat chain with ChromaDB and HuggingFace embeddings
- Provides a Streamlit UI for analysis and conversational follow-up

## Key features

- `YouTube URL` audio extraction via `yt-dlp`
- `Local file path` support for `.mp4` and other media files
- `Whisper` transcription for English content
- `Sarvam` transcription/translation for Hinglish content
- `LangChain` prompt chains for summarization and extraction
- `ChromaDB` vector storage for semantic retrieval
- `RAG` chat interface for transcript-based question answering
- Highly stylized Streamlit UI with author branding

## Architecture

- `app.py` — Streamlit user interface and pipeline orchestration
- `main.py` — CLI pipeline entrypoint for local execution
- `core/transcriber.py` — transcription orchestration for local Whisper and Sarvam
- `core/summarizer.py` — title generation and summarization chains
- `core/extractor.py` — action items, decisions, and questions extraction
- `core/rag_engine.py` — RAG chain builder and retrieval QA
- `core/vector_store.py` — embedding and Chroma vector store management
- `utils/audio_processor.py` — YouTube download, file conversion, and chunking

## Requirements

- Python 3.11+ recommended
- `ffmpeg` installed on the machine and available on PATH
- A compatible Python environment with dependencies from `requirements.txt`

## Environment variables

The project uses the following variables in `.env`:

```env
MISTRAL_API_KEY=
SARVAM_API_KEY=
WHISPER_MODEL=base
SARVAM_STT_MODEL=saaras:v2.5
```

### Required values

- `MISTRAL_API_KEY` — API key for Mistral AI
- `SARVAM_API_KEY` — API key for Sarvam transcription/translation

### Optional model settings

- `WHISPER_MODEL` — local Whisper model name, defaults to `base`
- `SARVAM_STT_MODEL` — Sarvam STT model name, defaults to `saaras:v2.5`

## Installation

1. Clone the repository or copy the project files.
2. Create and activate a Python virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Install `ffmpeg` separately if it is not already installed.
   - On Windows, add the `ffmpeg` binary to your PATH.

5. Create a `.env` file in the project root with the required API keys.

## Usage

### Run with Streamlit

```bash
streamlit run app.py
```

Then open the local Streamlit address in your browser.

### Run from command line

```bash
python main.py
```

Enter a YouTube URL or local file path when prompted.

## Local video support

The app currently supports direct local video processing via a file path. If the input is not a URL, the same audio pipeline is used:

- local media conversion to WAV
- audio chunking
- transcription
- summarization
- extraction
- RAG chat

This means local `.mp4` files will go through the same analysis flow as YouTube URLs.

## Notes and troubleshooting

- If you see `FP16 is not supported on CPU; using FP32 instead`, that is expected on CPU-only environments.
- If you encounter missing `torchvision`, install it with:

```bash
pip install torchvision
```

- Ensure `ffmpeg` is installed and available in your PATH so `pydub` conversion works.

## Author

Built with ❤️ by Faizan Raza

## Future improvements

- add a browser `st.file_uploader(...)` for direct file uploads
- improve progress feedback and error handling for large videos
- support more transcription languages and model choices
- add output export options for PDF, TXT, or JSON
