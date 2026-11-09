import importlib.util
import unittest

ICON_PATH = "android/app/src/main/res/drawable/ic_launcher.png"


@unittest.skipUnless(importlib.util.find_spec("PIL"), "Pillow no esta instalado")
class TestTask14Icon(unittest.TestCase):
    """El icono debe ser solo el rayo, sin el texto larptok."""

    def test_icon_has_no_dark_text(self):
        from PIL import Image

        img = Image.open(ICON_PATH).convert("RGBA")
        self.assertEqual((512, 512), img.size,
                         "El icono debe seguir siendo 512x512")
        px = img.load()
        dark = []
        for y in range(400, 475):
            for x in range(140, 375):
                r, g, b, a = px[x, y]
                if a >= 10 and r < 120 and g < 120 and b < 140:
                    dark.append((x, y))
        self.assertEqual([], dark,
                         "El icono todavia tiene el texto larptok")

    def test_icon_keeps_the_bolt_tip(self):
        from PIL import Image

        img = Image.open(ICON_PATH).convert("RGBA")
        px = img.load()
        whites = 0
        for y in range(400, 480):
            for x in range(180, 280):
                r, g, b, a = px[x, y]
                if a >= 10 and r > 225 and g > 225 and b > 225:
                    whites += 1
        self.assertGreater(whites, 50,
                           "El rayo debe conservar su punta blanca")


if __name__ == "__main__":
    unittest.main()
