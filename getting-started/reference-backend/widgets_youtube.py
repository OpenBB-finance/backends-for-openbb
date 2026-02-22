from typing import List
from fastapi import APIRouter, Query
from fastapi.responses import PlainTextResponse

from core import register_widget, WIDGETS, FileOption

router = APIRouter()

SAMPLE_VIDEOS = [
    {
        "name": "OpenBB Workspace Demo",
        "url": "https://www.youtube.com/watch?v=uYyhswnZkSw",
        "transcript": "# OpenBB Workspace Demo\n\nTranscript handled by the backend..."
    },
    {
        "name": "Open Data Platform Demo",
        "url": "https://www.youtube.com/watch?v=MSlhOFxEdxg",
        "transcript": "# Open Data Platform Demo\n\nTranscript handled by the backend..."
    }
]

@router.get("/get_video_options")
async def get_video_options() -> List[FileOption]:
    """Get list of available videos for dropdown selection"""
    return [
        FileOption(label=video["name"], value=video["name"])
        for video in SAMPLE_VIDEOS
    ]


@register_widget({
    "name": "Video Library",
    "description": "View YouTube videos",
    "type": "youtube",
    "endpoint": "/get_video",
    "gridData": {"w": 20, "h": 12},
    "params": [{
        "paramName": "video_name",
        "description": "Video to display",
        "type": "endpoint",
        "label": "Video",
        "optionsEndpoint": "/get_video_options",
        "value": "OpenBB Workspace Demo",
    }]
})
@router.get("/get_video")
async def get_video(
    video_name: str = Query("", description="Selected video"),
):
    """
    Get YouTube video URL.

    This endpoint returns the video URL for the player.
    """
    video = next((v for v in SAMPLE_VIDEOS if v["name"] == video_name), None)

    if not video:
        return PlainTextResponse(content="")

    return PlainTextResponse(content=video["url"])

@register_widget({
    "name": "Video Library with Transcript",
    "description": "View YouTube videos with transcript support for AI",
    "type": "youtube",
    "endpoint": "/get_video_with_transcript",
    "raw": True,
    "gridData": {"w": 20, "h": 12},
    "params": [{
        "paramName": "video_name",
        "description": "Video to display",
        "type": "endpoint",
        "label": "Video",
        "optionsEndpoint": "/get_video_options",
        "value": "OpenBB Workspace Demo",
    }]
})
@router.get("/get_video_with_transcript")
async def get_video_with_transcript(
    video_name: str = Query("", description="Selected video"),
    raw: bool = Query(False, description="Return transcript instead of URL"),
):
    """
    Get YouTube video URL or transcript.

    When raw=True is set in the widget config, the frontend will request
    ?raw=true to get the transcript for AI context.
    """
    video = next((v for v in SAMPLE_VIDEOS if v["name"] == video_name), None)

    if not video:
        return PlainTextResponse(content="*No video selected*" if raw else "")

    if raw:
        return PlainTextResponse(content=video["transcript"], media_type="text/markdown")

    return PlainTextResponse(content=video["url"])
