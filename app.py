from flask import Flask, request, jsonify

app = Flask(__name__)

personas = []
id_actual = 1


@app.route("/personas", methods=["POST"])
def agregar_persona():
    global id_actual

    datos = request.get_json()

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
    return jsonify(personas), 200


@app.route("/personas/<int:id_persona>", methods=["DELETE"])
def eliminar_persona(id_persona):
    global personas

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
    app.run(debug=True)