import os
import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
load_dotenv()

# Lấy URL ngrok từ biến môi trường
NGROK_CHAT_URL = os.getenv(
    "NGROK_CHAT_URL",
    "https://e1ce-2402-800-629c-6da3-da6-3fbe-4543-91f2.ngrok-free.app/chat"
)

@csrf_exempt
def chat_proxy(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        payload = json.loads(request.body)
        session_id = payload.get("session_id")
        query = payload.get("query")
        if not session_id or not query:
            return JsonResponse(
                {"error": "Missing 'session_id' or 'query'"},
                status=400
            )

        # Gọi tới chatbot API qua ngrok
        upstream = requests.post(
            NGROK_CHAT_URL,
            json={"session_id": session_id, "query": query},
            timeout=100
        )
        upstream.raise_for_status()

        # Trả lại JSON từ upstream
        return JsonResponse(upstream.json(), status=upstream.status_code)

    except requests.RequestException as e:
        return JsonResponse(
            {"error": "Upstream API error", "details": str(e)},
            status=502
        )
    except Exception as e:
        return JsonResponse(
            {"error": "Internal server error", "details": str(e)},
            status=500
        )
