import os
import re
import urllib.request

# User-Agent de navegador movil: Instagram responde distinto segun el cliente
# y el embed publico necesita uno de navegador.
MOBILE_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
)


def build_embed_url(link: str) -> str:
    """Convierte el link de un post en la URL del embed publico.

    El endpoint /embed/ de Instagram devuelve el HTML del post sin exigir
    sesion para contenido publico. Devuelve '' si el link no es un post.
    """
    if not link:
        return ""
    match = re.search(r"instagram\.com/(?:p|reel|tv)/([A-Za-z0-9_-]+)", link)
    if not match:
        return ""
    return "https://www.instagram.com/p/%s/embed/" % match.group(1)


def _unescape(value: str) -> str:
    return value.replace("\\/", "/").replace("&amp;", "&")


def extract_media_url_from_embed(html: str) -> str:
    """Saca la URL directa del archivo multimedia del HTML del embed.

    Busca primero el video (mp4) y despues la imagen, porque un post puede
    tener ambos. Devuelve '' si no encuentra nada.
    """
    if not html:
        return ""

    # 1) video: meta og:video o "video_url" en el JSON incrustado.
    for pattern in (
        r'<meta[^>]+property="og:video"[^>]+content="([^"]+)"',
        r'"video_url"\s*:\s*"([^"]+)"',
    ):
        match = re.search(pattern, html)
        if match:
            url = _unescape(match.group(1))
            if url.startswith("http"):
                return url

    # 2) imagen: meta og:image o el <img> del embed.
    for pattern in (
        r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"',
        r'<img[^>]+class="[^"]*EmbeddedMedia[^"]*"[^>]+src="([^"]+)"',
        r'<img[^>]+src="(https://[^"]*cdninstagram\.com[^"]+)"',
    ):
        match = re.search(pattern, html)
        if match:
            url = _unescape(match.group(1))
            if url.startswith("http"):
                return url

    return ""


def fetch_embed_html(url: str) -> str:
    """Descarga el HTML del embed publico. Devuelve '' si falla."""
    if not url:
        return ""
    request = urllib.request.Request(
        url,
        headers={"User-Agent": MOBILE_UA, "Accept-Language": "es-AR,es;q=0.9,en;q=0.8"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read().decode("utf-8", "replace")
    except Exception:
        return ""


def get_media_url(link: str, cookie_path: str = "") -> str:
    """Devuelve la URL directa del archivo multimedia de un link publico.

    Estrategia:
      1. Embed publico de Instagram (sin login, sin cookies).
      2. yt-dlp, usando cookies de sesion si las configuraste.

    Retorna '' si no se pudo extraer.
    """
    if not link:
        return ""

    # 1) Embed publico: no pide sesion para posts publicos.
    embed_url = build_embed_url(link)
    if embed_url:
        html = fetch_embed_html(embed_url)
        extracted = extract_media_url_from_embed(html)
        if extracted:
            return extracted

    # 2) yt-dlp como respaldo (con o sin cookies).
    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "noplaylist": True,
    }

    if cookie_path and os.path.isfile(cookie_path):
        opts["cookiefile"] = cookie_path

    try:
        from yt_dlp import YoutubeDL

        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(link, download=False)
    except Exception:
        return ""

    if not info:
        return ""

    # extract_info puede devolver un playlist si el link lo es; tomamos la
    # primera entrada valida.
    if isinstance(info, dict) and info.get("_type") == "playlist":
        entries = info.get("entries") or []
        info = entries[0] if entries else None
        if not info:
            return ""

    if not isinstance(info, dict):
        return ""

    url = info.get("url")
    if url:
        return url

    # Fallback: ultimo formato de la lista (suele ser la mejor calidad).
    formats = info.get("formats") or []
    for fmt in reversed(formats):
        if isinstance(fmt, dict) and fmt.get("url"):
            return fmt["url"]

    return ""
