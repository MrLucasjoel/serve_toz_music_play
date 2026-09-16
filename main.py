import asyncio
import base64
import glob
import os
import shutil
import tempfile
from pathlib import Path

import yt_dlp
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl
from starlette.background import BackgroundTask

app = FastAPI(title="TozMusic Downloader")


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "tozmusic-downloader",
        "status": "ok",
        "health": "/health",
    }


class DownloadRequest(BaseModel):
    url: HttpUrl


def encode_header(value: str) -> str:
    return base64.urlsafe_b64encode(value.encode("utf-8")).decode("ascii")


def download_video(url: str) -> tuple[str, dict[str, str], str]:
    folder = tempfile.mkdtemp(prefix="tozmusic-")
    options = {
        "format": "bestaudio[ext=m4a]/bestaudio",
        "outtmpl": os.path.join(folder, "%(id)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(options) as downloader:
            info = downloader.extract_info(url, download=True)

        files = [path for path in glob.glob(os.path.join(folder, "*")) if os.path.isfile(path)]
        if not files:
            raise RuntimeError("O yt-dlp não gerou nenhum arquivo de áudio.")

        path = files[0]
        headers = {
            "X-TozMusic-Id": str(info.get("id", "")),
            "X-TozMusic-Title": encode_header(info.get("title", "Música")),
            "X-TozMusic-Artist": encode_header(info.get("uploader", "YouTube")),
            "X-TozMusic-Thumbnail": info.get("thumbnail", ""),
            "X-TozMusic-Duration": str(int(info.get("duration") or 0)),
            "X-TozMusic-Extension": Path(path).suffix.lstrip(".") or "m4a",
        }
        return path, headers, folder
    except Exception:
        shutil.rmtree(folder, ignore_errors=True)
        raise


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/download")
async def download(request: DownloadRequest):
    try:
        path, headers, folder = await asyncio.to_thread(download_video, str(request.url))
    except Exception as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    filename = os.path.basename(path)
    media_type = "audio/mp4" if path.endswith(".m4a") else "audio/webm"
    return FileResponse(
        path,
        media_type=media_type,
        filename=filename,
        headers=headers,
        background=BackgroundTask(shutil.rmtree, folder, ignore_errors=True),
    )
