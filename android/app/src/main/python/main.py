import os

from yt_dlp import YoutubeDL


def get_media_url(link: str, cookie_path: str = "") -> str:
    """Devuelve la URL directa del archivo multimedia de un link publico.

    cookie_path: ruta local a un cookies.txt en formato Netscape. Con cookies
    de sesion yt-dlp puede alcanzar contenido que exige login (por ejemplo
    Instagram). Vacio = solo contenido publico.

    Retorna '' si no se pudo extraer (link privado, login requerido,
    formato no soportado o error de red).
    """
    if not link:
        return ""

    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "noplaylist": True,
    }

    if cookie_path and os.path.isfile(cookie_path):
        opts["cookiefile"] = cookie_path

    try:
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
