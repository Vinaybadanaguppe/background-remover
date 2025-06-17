# Background Remover API

A Flask-based API service that removes backgrounds from images using the rembg library.

## Features

- Remove backgrounds from images via API endpoint
- Supports various image formats
- Returns transparent PNG

## API Usage

POST to `/remove-background` with a multipart form containing an 'image' file.

## Development

1. Install dependencies:
```bash
poetry install
```

2. Run the server:
```bash
poetry run python app.py
```

## Production

The service is configured to run on Render.com using Poetry for dependency management.
