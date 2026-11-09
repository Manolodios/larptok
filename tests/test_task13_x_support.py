import unittest

JAVA_PATH = "android/app/src/main/java/com/descargador/videos/MainActivity.java"
STRINGS_PATH = "android/app/src/main/res/values/strings.xml"
PYTHON_PATH = "android/app/src/main/python/main.py"


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_main():
    namespace = {"__name__": "larptok_main", "__file__": PYTHON_PATH}
    with open(PYTHON_PATH, "r", encoding="utf-8") as f:
        exec(compile(f.read(), PYTHON_PATH, "exec"), namespace)
    return namespace


class TestTask13XSupport(unittest.TestCase):
    """X/Twitter publico: yt-dlp resuelve el link, sin login."""

    def test_supported_hosts_include_x_and_twitter(self):
        java = read(JAVA_PATH)
        self.assertIn('"x.com"', java, "Falta x.com en los dominios soportados")
        self.assertIn('"twitter.com"', java, "Falta twitter.com")

    def test_invalid_url_message_lists_x(self):
        java = read(JAVA_PATH)
        self.assertIn("x.com", java[java.index("URL no válida"):][:200],
                      "El mensaje de error debe nombrar x.com")

    def test_network_capture_includes_x_media_hosts(self):
        java = read(JAVA_PATH)
        block = java[java.index("shouldInterceptRequest"):java.index("setDownloadListener")]
        self.assertIn("twimg.com", block,
                      "X sirve los videos desde twimg.com")

    def test_home_subtitle_lists_x(self):
        strings = read(STRINGS_PATH)
        line = [l for l in strings.splitlines() if 'name="home_subtitle"' in l][0]
        self.assertIn("X", line, "El subtitulo de Inicio debe mencionar X")

    def test_python_has_format_picker(self):
        python = read(PYTHON_PATH)
        self.assertIn("def _pick_best_format", python,
                      "Hace falta elegir el mejor formato progresivo")
        body = python[python.index("def get_media_url"):]
        self.assertIn("_pick_best_format(", body,
                      "get_media_url debe usar el selector de formatos")

    def test_picker_prefers_progressive_mp4_over_hls(self):
        main = load_main()
        formats = [
            {"url": "https://video.twimg.com/pl/avc1/720/x.m3u8",
             "vcodec": "avc1.64001F", "height": 720, "tbr": 893},
            {"url": "https://video.twimg.com/vid/avc1/720x720/best.mp4",
             "vcodec": None, "height": 720, "tbr": 1280},
            {"url": "https://video.twimg.com/vid/avc1/320x320/low.mp4",
             "vcodec": None, "height": 320, "tbr": 432},
            {"url": "https://video.twimg.com/pl/mp4a/32000/audio.m3u8",
             "vcodec": "none", "height": None, "tbr": 32},
        ]
        url = main["_pick_best_format"](formats)
        self.assertTrue(url.endswith("best.mp4"),
                        "Debe elegir el MP4 progresivo de mayor calidad, devolvio: %r" % url)

    def test_picker_returns_empty_when_only_hls(self):
        main = load_main()
        formats = [
            {"url": "https://video.twimg.com/pl/avc1/720/x.m3u8",
             "vcodec": "avc1", "height": 720, "tbr": 893},
        ]
        self.assertEqual("", main["_pick_best_format"](formats),
                         "DownloadManager no puede bajar un m3u8")

    def test_x_link_is_not_treated_as_instagram_embed(self):
        main = load_main()
        self.assertEqual("", main["build_embed_url"](
            "https://x.com/usuario/status/1234567890"))

    def test_version_bumped_for_x_support(self):
        gradle = read("android/app/build.gradle")
        self.assertIn("versionCode 3", gradle,
                      "larptok 2.0 debe tener versionCode 3")
        self.assertIn('versionName "2.0"', gradle,
                      "La version debe llamarse 2.0")
        strings = read(STRINGS_PATH)
        self.assertIn("Versión 2.0", strings,
                      "Ajustes debe mostrar larptok 2.0")


if __name__ == "__main__":
    unittest.main()
