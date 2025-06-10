import os
import tempfile
import base64
import requests
import logging
from django.http import FileResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

DENSEPOSE_URL = os.getenv("DENSEPOSE_URL")
BASE_URL      = os.getenv("BASE_URL")
INFERENCE_URL = os.getenv("INFERENCE_URL")

@csrf_exempt
def virtual_tryon(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    human = request.FILES.get("human")
    cloth = request.FILES.get("cloth")
    print("Received files: %s", list(request.FILES.keys()))
    if not human or not cloth:
        return JsonResponse({"error": "Missing required files: human, cloth"}, status=400)

    tmpdir = tempfile.mkdtemp()
    print("tmpdir = %s", tmpdir)

    def save_uploaded(f, name):
        path = os.path.join(tmpdir, name)
        with open(path, "wb") as out:
            for chunk in f.chunks():
                out.write(chunk)
        return path

    human_path = save_uploaded(human, "human.png")
    cloth_path = save_uploaded(cloth, "cloth.png")
    print("Saved human -> %s, cloth -> %s", human_path, cloth_path)

    densepose_path     = request.FILES.get("densepose")     and save_uploaded(request.FILES["densepose"], "densepose.jpg")
    agnostic_path      = request.FILES.get("agnostic")      and save_uploaded(request.FILES["agnostic"], "agnostic.png")
    agnostic_mask_path = request.FILES.get("agnostic_mask") and save_uploaded(request.FILES["agnostic_mask"], "agnostic_mask.png")
    cloth_mask_path    = request.FILES.get("cloth_mask")    and save_uploaded(request.FILES["cloth_mask"], "cloth_mask.png")

    f = request.FILES['agnostic_mask']
    if f.content_type != 'image/png':
        print("Unexpected mime for agnostic_mask: %s", f.content_type)

    print("Initial optional paths: densepose=%s, agnostic=%s, agnostic_mask=%s, cloth_mask=%s",
                densepose_path, agnostic_path, agnostic_mask_path, cloth_mask_path)

    # Tự sinh nếu thiếu
    if not densepose_path:
        r = requests.post(DENSEPOSE_URL, files={"image": open(human_path, "rb")})
        r.raise_for_status()
        densepose_path = os.path.join(tmpdir, "densepose.jpg")
        with open(densepose_path, "wb") as f:
            f.write(r.content)
        print("Generated densepose -> %s", densepose_path)

    human_nobg = ""
    if not agnostic_path or not agnostic_mask_path:
        # Remove background
        r = requests.post(f"{BASE_URL}/remove_bg", files={"image": open(human_path, "rb")})
        r.raise_for_status()
        human_nobg = os.path.join(tmpdir, "human_nobg.png")
        with open(human_nobg, "wb") as f:
            f.write(r.content)
        print("Generated human without bg -> %s", human_nobg)

        # Tạo agnostic + mask
        r2 = requests.post(f"{BASE_URL}/agnostic_shirt", files={"image": open(human_nobg, "rb")})
        r2.raise_for_status()
        data2 = r2.json()

        # Xử lý agnostic image
        agn_b64 = data2.get("agnostic")
        if not agn_b64 or "," not in agn_b64:
            logger.error("Invalid agnostic data")
            return JsonResponse({"error": "Invalid agnostic data"}, status=502)
        b1 = base64.b64decode(agn_b64.split(",", 1)[1])
        agnostic_path = os.path.join(tmpdir, "agnostic.png")
        with BytesIO(b1) as bio:
            img = Image.open(bio)
            if img.size == (0, 0):
                raise ValueError("Agnostic image has zero size")
            img.save(agnostic_path, format="PNG")

        # Xử lý mask image
        mask_b64 = data2.get("mask")
        if not mask_b64 or "," not in mask_b64:
            logger.error("Invalid mask data")
            return JsonResponse({"error": "Invalid mask data"}, status=502)
        b2 = base64.b64decode(mask_b64.split(",", 1)[1])
        agnostic_mask_path = os.path.join(tmpdir, "agnostic_mask.png")
        with BytesIO(b2) as bio:
            img2 = Image.open(bio)
            if img2.size == (0, 0):
                raise ValueError("Agnostic mask image has zero size")
            img2.save(agnostic_mask_path, format="PNG")

        print("Generated agnostic=%s, agnostic_mask=%s", agnostic_path, agnostic_mask_path)

    if not cloth_mask_path:
        r = requests.post(f"{BASE_URL}/shirt_mask", files={"image": open(cloth_path, "rb")})
        r.raise_for_status()
        cloth_mask_path = os.path.join(tmpdir, "cloth_mask.png")
        with open(cloth_mask_path, "wb") as f:
            f.write(r.content)
        print("Generated cloth_mask -> %s", cloth_mask_path)

    files = {
        "agn_src":        open(agnostic_path, "rb"),
        "agn_mask_src":   open(agnostic_mask_path, "rb"),
        "cloth_src":      open(cloth_path, "rb"),
        "cloth_mask_src": open(cloth_mask_path, "rb"),
        "image_src":      open(human_nobg if human_nobg else human_path, "rb"),
        "densepose_src":  open(densepose_path, "rb"),
    }
    data = {"repaint": "true"}

    # Log thông tin kích thước file
    for key, fp in files.items():
        try:
            size = os.path.getsize(fp.name)
        except Exception:
            size = 'N/A'
        print("File %s = %s bytes (%s)", key, fp.name, size)

    try:
        r = requests.post(INFERENCE_URL, files=files, data=data, timeout=60)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        detail = None
        try:
            detail = r.json()
        except:
            detail = r.text
        logger.error("Inference server error %s: %s", e, detail)
        return JsonResponse({
            "error": "Inference server error",
            "detail": detail
        }, status=502)

    # Trả về
    out_path = os.path.join(tmpdir, "output.jpg")
    with open(out_path, "wb") as f:
        f.write(r.content)
    print("Wrote output to %s", out_path)

    return FileResponse(open(out_path, "rb"), content_type="image/jpeg")
