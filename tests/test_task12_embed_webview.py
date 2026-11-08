import unittest

JAVA_PATH = "android/app/src/main/java/com/descargador/videos/MainActivity.java"


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class TestTask12EmbedWebView(unittest.TestCase):
    """El embed publico se renderiza en el WebView y se captura el archivo."""

    def test_builds_embed_url_for_posts(self):
        java = read(JAVA_PATH)
        self.assertIn("buildInstagramEmbedUrl", java,
                      "Falta convertir el link de Instagram a su embed publico")
        self.assertIn("/embed/", java,
                      "La URL del embed debe terminar en /embed/")

    def test_uses_embed_url_when_extraction_fails(self):
        java = read(JAVA_PATH)
        button = java[java.index("btnProcesar.setOnClickListener"):]
        self.assertIn("buildInstagramEmbedUrl", button,
                      "Al fallar yt-dlp, Instagram debe abrirse en modo embed")

    def test_does_not_stop_at_instagram_limit_message(self):
        java = read(JAVA_PATH)
        button = java[java.index("btnProcesar.setOnClickListener"):]
        self.assertNotIn("status_instagram_limit", button,
                         "No debe rendirse antes de intentar el embed en el WebView")

    def test_captures_media_from_rendered_page(self):
        java = read(JAVA_PATH)
        self.assertIn("captureMediaFromPage", java,
                      "Falta leer el DOM del embed ya renderizado")
        self.assertIn("evaluateJavascript", java,
                      "Falta evaluar JavaScript para obtener el archivo")
        self.assertIn("video", java,
                      "La busqueda debe incluir el elemento video")
        self.assertIn("cdninstagram", java,
                      "La busqueda debe incluir imagenes del CDN de Instagram")

    def test_retries_capture_while_embed_loads(self):
        java = read(JAVA_PATH)
        self.assertIn("EMBED_CAPTURE_ATTEMPTS", java,
                      "El embed carga despues de onPageFinished: hay que reintentar")
        self.assertIn("postDelayed", java,
                      "Falta esperar entre intentos de captura")

    def test_webview_uses_mobile_chrome_user_agent(self):
        java = read(JAVA_PATH)
        self.assertIn("setUserAgentString", java,
                      "Instagram sirve distinto segun el User-Agent")
        self.assertIn("Mobile Safari", java,
                      "Falta un User-Agent de navegador movil")

    def test_allows_media_playback_without_tap(self):
        java = read(JAVA_PATH)
        self.assertIn("setMediaPlaybackRequiresUserGesture(false)", java,
                      "El video del embed debe poder cargar sin tocar play")

    def test_extraction_runs_off_main_thread(self):
        java = read(JAVA_PATH)
        button = java[java.index("btnProcesar.setOnClickListener"):]
        self.assertIn("new Thread", button,
                      "yt-dlp no debe bloquear el hilo principal")
        self.assertIn("runOnUiThread", button,
                      "El resultado debe volver al hilo de la interfaz")

    def test_disables_button_while_extracting(self):
        java = read(JAVA_PATH)
        button = java[java.index("btnProcesar.setOnClickListener"):]
        self.assertIn("btnProcesar.setEnabled(false)", button,
                      "Hay que evitar extracciones simultaneas")
        self.assertIn("btnProcesar.setEnabled(true)", button,
                      "El boton debe reactivarse al terminar")


if __name__ == "__main__":
    unittest.main()
