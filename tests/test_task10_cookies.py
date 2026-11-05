import os
import unittest

LAYOUT_PATH = "android/app/src/main/res/layout/activity_main.xml"
ACTIVITY_PATH = "android/app/src/main/java/com/descargador/videos/MainActivity.java"
STRINGS_PATH = "android/app/src/main/res/values/strings.xml"
PYTHON_PATH = "android/app/src/main/python/main.py"


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class TestTask10Cookies(unittest.TestCase):
    def test_settings_has_cookies_card(self):
        layout = read(LAYOUT_PATH)
        for widget in ["cookiesCard", "actionPickCookies", "tvCookiesHint"]:
            self.assertIn('android:id="@+id/%s"' % widget, layout,
                          "Falta %s en activity_main.xml" % widget)

    def test_settings_has_remove_cookies_action(self):
        layout = read(LAYOUT_PATH)
        self.assertIn('android:id="@+id/actionRemoveCookies"', layout,
                      "Falta la accion para quitar las cookies")

    def test_activity_has_cookies_picker(self):
        activity = read(ACTIVITY_PATH)
        self.assertIn("ActivityResultContracts.OpenDocument", activity,
                      "Falta el selector de archivos para cookies")
        self.assertIn("cookiePicker", activity,
                      "Falta registrar el selector de cookies")
        self.assertIn("cookiePicker.launch", activity,
                      "Falta abrir el selector de cookies")

    def test_activity_copies_cookies_to_private_storage(self):
        activity = read(ACTIVITY_PATH)
        self.assertIn("getFilesDir", activity,
                      "Las cookies deben copiarse al almacenamiento privado")
        self.assertIn("COOKIES_FILE_NAME", activity,
                      "Falta el nombre del archivo de cookies local")
        self.assertIn("openFileOutput", activity,
                      "Falta escribir el archivo en el almacenamiento privado")
        self.assertIn("output.write", activity,
                      "Falta volcar el contenido del archivo de cookies")

    def test_activity_persists_cookies_choice(self):
        activity = read(ACTIVITY_PATH)
        self.assertIn("PREF_COOKIES_URI", activity,
                      "Falta recordar la URI de cookies elegida")
        self.assertIn("takePersistableUriPermission", activity,
                      "Falta conservar el permiso de lectura del archivo")

    def test_activity_passes_cookies_to_python(self):
        activity = read(ACTIVITY_PATH)
        self.assertIn('callAttr("get_media_url", url', activity,
                      "getBestQualityUrl debe pasar la URL y las cookies a Python")
        self.assertIn("getCookiesLocalPath", activity,
                      "Falta resolver la ruta local de cookies")

    def test_activity_removes_cookies(self):
        activity = read(ACTIVITY_PATH)
        self.assertIn("removeCookies", activity,
                      "Falta poder quitar las cookies")

    def test_python_accepts_cookie_path(self):
        python = read(PYTHON_PATH)
        self.assertIn("cookie_path", python,
                      "main.py debe aceptar la ruta de cookies")
        self.assertIn('opts["cookiefile"]', python,
                      "main.py debe pasar cookiefile a yt-dlp")

    def test_cookies_strings_exist(self):
        strings = read(STRINGS_PATH)
        for name in ["cookies_title", "cookies_hint", "cookies_hint_active",
                     "cookies_pick", "cookies_remove", "cookies_error"]:
            self.assertIn('name="%s"' % name, strings,
                          "Falta el string %s" % name)


if __name__ == "__main__":
    unittest.main()
