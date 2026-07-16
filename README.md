# Word-Math

## Project Description

**Try it out! [link](https://word-math.up.railway.app/)**

An interactive word embedding sandbox. It uses a local GloVe vector space where you can enter simple word equations like `king - man + woman`. The backend evaluates the expression, finds the nearest neighbors in embedding space, and projects the result onto an interactive 3D view.

## Features

- Preprocessing script that converts raw GloVe text into optimized `.npy` vectors and metadata
- FastAPI backend for word lookup, nearest-neighbor search, and analogy solving
- Interactive 3D visualization of input words, neighbors, and the computed result point
- Preset example equations for quick exploration
- Static frontend served directly by the backend

## Workflow

The project is built around a simple pipeline:

1. Download the [GloVe file](https://huggingface.co/stanfordnlp/glove/resolve/main/glove.840B.300d.zip) into `data/`.
2. Run `preprocess.py` to build `data/vectors.npy` and `data/metadata.pkl`.
3. Start the FastAPI server from `main.py`.
4. Enter an equation in the browser and explore the resulting vector cluster in 3D.

## Requirements

- Python 3.10+, `pip`
- A GloVe embedding file in `data/glove.840B.300d.txt`

## Installation

Install the dependencies with:

```bash
pip install -r requirements.txt
```

## Prepare the Dataset

If you have not generated the vector files yet, run the preprocessing script first:

```bash
python preprocess.py
```

This reads `data/glove.840B.300d.txt` and writes:

- `data/vectors.npy`
- `data/metadata.pkl`

By default the script keeps up to 200,000 unique tokens and stores 300-dimensional float vectors.

## Run the App

Start the API server with:

```bash
uvicorn main:app --reload
```

Then open the app in your browser at:

```text
http://localhost:8000
```

From the UI you can:

- enter an analogy equation such as `king - man + woman`
- use the built-in example presets
- change how many closest labels are shown
- inspect the 3D projection of the cluster

## API Endpoints

The backend exposes a small set of HTTP endpoints:

- `GET /` serves the frontend
- `GET /api/status` returns vocabulary size and embedding dimensions
- `GET /vector/{word}` returns the raw embedding for a word
- `GET /neighbors/{word}?k=25` returns nearest neighbors for a word
- `POST /api/analogy` evaluates an analogy equation and returns the projected cluster

Example request body for `POST /api/analogy`:

```json
{
  "equation": "king - man + woman",
  "k": 25
}
```
