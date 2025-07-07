from fastapi import APIRouter, Request, Response
from fastapi.responses import FileResponse
import os

router = APIRouter(tags=["scripts"])

@router.get("/scripts/queue.js")
async def get_queue_script(
    request: Request,
    app_id: str = None,
    callback_url: str = None,
    lang: str = "en",
    theme: str = "light"
):
    """Serve the dynamic queue management JavaScript client"""
    script_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "queue.js")
    
    if not os.path.exists(script_path):
        return Response(
            content="console.error('Queue script not found');",
            media_type="application/javascript"
        )
    
    # Read the script content
    with open(script_path, 'r') as f:
        script_content = f.read()
    
    # Inject configuration
    config_script = f"""
    // Auto-configuration
    window.QueueConfig = {{
        appId: '{app_id or ""}',
        callbackUrl: '{callback_url or ""}',
        lang: '{lang}',
        theme: '{theme}',
        apiBaseUrl: '{request.base_url}'
    }};
    """
    
    return Response(
        content=config_script + script_content,
        media_type="application/javascript"
    ) 