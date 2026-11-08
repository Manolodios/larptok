import os
import subprocess
import unittest

MAIN_PY = "android/app/src/main/python/main.py"
WORKER_PY = "tests/python_main_loader.py"

# HTML de ejemplo con la forma que devuelve Instagram en su endpoint publico
# /p/<shortcode>/embed/ para un post con imagen.
EMBED_IMAGE_HTML = '''
<html><body>
<meta property="og:image" content="https://scontent.cdninstagram.com/v/t51.28853-15/img123.jpg">
<div class="Embed">
  <img class="EmbeddedMedia" src="https://scontent.cdninstagram.com/v/t51.28853-15/img123.jpg?nc=cat">
</div>
</body></html>
'''

EMBED_VIDEO_HTML = '''
<html><body>
<meta property="og:video" content="https://scontent.cdninstagram.com/v/t50.28853-16/video456.mp4">
<script type="text/javascript">
  window.__additionalData = {"video_url":"https:\\/\\/scontent.cdninstagram.com\\/v\\/t50.28853-16\\/video456.mp4"};
</script>
</body></html>
'''


class TestInstagramEmbedExtractor(unittest.TestCase):
    """Prueba el parseo del embed publico de Instagram sin login."""

    @classmethod
    def setUpClass(cls):
        # Carga main.py sin depender de que yt-dlp este instalado.
        namespace = {"__name__": "larptok_main", "__file__": MAIN_PY}
        with open(MAIN_PY, "r", encoding="utf-8") as f:
            source = f.read()
        exec(compile(source, MAIN_PY, "exec"), namespace)
        cls.main = namespace

    def test_extracts_image_url_from_embed_html(self):
        url = self.main["extract_media_url_from_embed"](EMBED_IMAGE_HTML)
        self.assertTrue(url.startswith("https://scontent.cdninstagram.com/"),
                        "Debe extraer la URL de imagen del CDN, devolvio: %r" % url)
        self.assertTrue(url.endswith(".jpg"), "La URL debe ser una imagen .jpg")

    def test_extracts_video_url_from_embed_html(self):
        url = self.main["extract_media_url_from_embed"](EMBED_VIDEO_HTML)
        self.assertTrue(url.startswith("https://scontent.cdninstagram.com/"),
                        "Debe extraer la URL de video del CDN, devolvio: %r" % url)
        self.assertTrue(url.endswith(".mp4"), "La URL debe ser un video .mp4")

    def test_returns_empty_string_when_no_media(self):
        self.assertEqual("", self.main["extract_media_url_from_embed"]("<html></html>"))
        self.assertEqual("", self.main["extract_media_url_from_embed"](""))
        self.assertEqual("", self.main["extract_media_url_from_embed"](None))

    def test_unescapes_json_backslashes(self):
        html = '{"video_url":"https:\\/\\/scontent.cdninstagram.com\\/clip.mp4"}'
        url = self.main["extract_media_url_from_embed"](html)
        self.assertEqual("https://scontent.cdninstagram.com/clip.mp4", url)

    def test_get_media_url_tries_embed_before_ytdlp(self):
        with open(MAIN_PY, "r", encoding="utf-8") as f:
            source = f.read()
        body = source[source.index("def get_media_url"):]
        self.assertIn("build_embed_url(", body,
                      "get_media_url debe intentar el embed publico")
        self.assertLess(body.index("build_embed_url("), body.index("YoutubeDL("),
                        "El embed publico debe intentarse antes de yt-dlp")


class TestMediaHelpers(unittest.TestCase):
    """Verifica que las constantes y el flujo existen."""

    def test_embed_url_helper_exists(self):
        with open(MAIN_PY, "r", encoding="utf-8") as f:
            source = f.read()
        self.assertIn("def build_embed_url", source,
                      "Falta construir la URL del embed publico")

    def test_embed_url_format(self):
        namespace = {"__name__": "larptok_main", "__file__": MAIN_PY}
        with open(MAIN_PY, "r", encoding="utf-8") as f:
            exec(compile(f.read(), MAIN_PY, "exec"), namespace)
        url = namespace["build_embed_url"]("https://www.instagram.com/p/ABC123xyz/")
        self.assertEqual("https://www.instagram.com/p/ABC123xyz/embed/", url)

    def test_embed_url_returns_empty_for_non_post(self):
        namespace = {"__name__": "larptok_main", "__file__": MAIN_PY}
        with open(MAIN_PY, "r", encoding="utf-8") as f:
            exec(compile(f.read(), MAIN_PY, "exec"), namespace)
        self.assertEqual("", namespace["build_embed_url"](
            "https://www.instagram.com/natgeo/"))

    def test_ytdlp_has_socket_timeout(self):
        with open(MAIN_PY, "r", encoding="utf-8") as f:
            source = f.read()
        self.assertIn('"socket_timeout"', source,
                      "yt-dlp no debe quedar colgado sin limite de tiempo")


if __name__ == "__main__":
    unittest.main()
