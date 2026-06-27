import unittest
import app


class TestPersonas(unittest.TestCase):

    def setUp(self):
        self.client = app.app.test_client()
        app.personas.clear()
        app.id_actual = 1

    def test_agregar_persona(self):
        respuesta = self.client.post(
            "/personas",
            json={
                "nombre": "Benjamin",
                "rut": "12345678-9",
                "fechaNacimiento": "2001-10-15",
                "ciudad": "Coquimbo"
            }
        )

        self.assertEqual(respuesta.status_code, 201)

    def test_obtener_personas(self):
        self.client.post(
            "/personas",
            json={
                "nombre": "Benjamin",
                "rut": "12345678-9",
                "fechaNacimiento": "2001-10-15",
                "ciudad": "Coquimbo"
            }
        )

        respuesta = self.client.get("/personas")

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.get_json()), 1)

    def test_eliminar_persona(self):
        self.client.post(
            "/personas",
            json={
                "nombre": "Benjamin",
                "rut": "12345678-9",
                "fechaNacimiento": "2001-10-15",
                "ciudad": "Coquimbo"
            }
        )

        respuesta = self.client.delete("/personas/1")

        self.assertEqual(respuesta.status_code, 200)


if __name__ == "__main__":
    unittest.main()