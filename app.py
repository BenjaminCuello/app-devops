import os
import time
import psycopg
from flask import Flask, request, jsonify

app = Flask(__name__)

personas = []
id_actual = 1


def usar_base_datos():
    return os.getenv("DATABASE_URL") is not None


def obtener_conexion():
    return psycopg.connect(os.getenv("DATABASE_URL"))


def preparar_base_datos():
    if not usar_base_datos():
        return

    intentos = 10

    for _ in range(intentos):
        try:
            with obtener_conexion() as conexion:
                with conexion.cursor() as cursor:
                    cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS personas (
                            id SERIAL PRIMARY KEY,
                            nombre VARCHAR(120) NOT NULL,
                            rut VARCHAR(20) NOT NULL,
                            fecha_nacimiento VARCHAR(20) NOT NULL,
                            ciudad VARCHAR(120) NOT NULL,
                            gustos TEXT[] NOT NULL
                        )
                        """
                    )
                    conexion.commit()
            return
        except psycopg.OperationalError:
            time.sleep(2)


preparar_base_datos()


@app.route("/personas", methods=["POST"])
def agregar_persona():
    global id_actual

    datos = request.get_json()

    if usar_base_datos():
        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO personas (nombre, rut, fecha_nacimiento, ciudad, gustos)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        datos["nombre"],
                        datos["rut"],
                        datos["fechaNacimiento"],
                        datos["ciudad"],
                        datos["gustos"]
                    )
                )

                nuevo_id = cursor.fetchone()[0]
                conexion.commit()

        nueva_persona = {
            "id": nuevo_id,
            "nombre": datos["nombre"],
            "rut": datos["rut"],
            "fechaNacimiento": datos["fechaNacimiento"],
            "ciudad": datos["ciudad"],
            "gustos": datos["gustos"]
        }

        return jsonify(nueva_persona), 201

    nueva_persona = {
        "id": id_actual,
        "nombre": datos["nombre"],
        "rut": datos["rut"],
        "fechaNacimiento": datos["fechaNacimiento"],
        "ciudad": datos["ciudad"],
        "gustos": datos["gustos"]
    }

    personas.append(nueva_persona)
    id_actual += 1

    return jsonify(nueva_persona), 201


@app.route("/personas", methods=["GET"])
def obtener_personas():
    if usar_base_datos():
        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, nombre, rut, fecha_nacimiento, ciudad, gustos
                    FROM personas
                    ORDER BY id
                    """
                )
                registros = cursor.fetchall()

        resultado = []

        for registro in registros:
            resultado.append({
                "id": registro[0],
                "nombre": registro[1],
                "rut": registro[2],
                "fechaNacimiento": registro[3],
                "ciudad": registro[4],
                "gustos": registro[5]
            })

        return jsonify(resultado), 200

    return jsonify(personas), 200


@app.route("/personas/<int:id_persona>", methods=["DELETE"])
def eliminar_persona(id_persona):
    global personas

    if usar_base_datos():
        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM personas WHERE id = %s RETURNING id",
                    (id_persona,)
                )
                persona = cursor.fetchone()
                conexion.commit()

        if persona is None:
            return jsonify({
                "mensaje": "Persona no encontrada"
            }), 404

        return jsonify({
            "mensaje": "Persona eliminada correctamente"
        }), 200

    persona = next(
        (p for p in personas if p["id"] == id_persona),
        None
    )

    if persona is None:
        return jsonify({
            "mensaje": "Persona no encontrada"
        }), 404

    personas = [p for p in personas if p["id"] != id_persona]

    return jsonify({
        "mensaje": "Persona eliminada correctamente"
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)