from flask import Flask, request, render_template, redirect, url_for, abort
import sqlite3
import os
import base64
import joblib
import numpy as np
import cv2
import shutil
from cnn import validate_image
from correo import enviar_correo

base_dir = os.path.abspath(os.path.dirname(__file__))
database_path = os.path.join(base_dir, "database", "my_database.db")

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

model_filename = "svm_model.joblib"
svm_model = joblib.load(model_filename)
disease_folders = ["PSORIASIS", "ROSACEA", "SARPULLIDO", "VITILIGO"]

carpeta_imagenes = "app/static/record"
id_imagen = len(
    [
        nombre
        for nombre in os.listdir(carpeta_imagenes)
        if os.path.isfile(os.path.join(carpeta_imagenes, nombre))
    ]
)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["POST", "GET"])
def index():
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        if request.method == "POST":
            documento = request.form["documento"]
            contrasena = request.form["contrasena"]

            cursor.execute(
                "SELECT * FROM Patients WHERE document=? AND password=?",
                (documento, contrasena),
            )
            paciente = cursor.fetchone()

            cursor.execute(
                "SELECT * FROM Doctors WHERE document=? AND password=?",
                (documento, contrasena),
            )
            doctor = cursor.fetchone()

            cursor.execute(
                "SELECT * FROM Admin WHERE document=? AND password=?",
                (documento, contrasena),
            )
            admin = cursor.fetchone()

            if paciente:
                return redirect(url_for("interface_patient", paciente_id=paciente[0]))

            if doctor:
                return redirect(url_for("interface_doctor", doctor_id=doctor[0]))

            if admin:
                return redirect(url_for("interface_admin"))

    except Exception as e:
        print("Error al conectar a la base de datos:", e)
    finally:
        if conn:
            conn.close()

    return render_template("index.html")


@app.route("/interface_patient/<int:paciente_id>", methods=["POST", "GET"])
def interface_patient(paciente_id):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, lastName FROM Patients WHERE id = ?", (paciente_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        paciente_name = result[0]
        paciente_lastname = result[1]
        full_name_pacient = paciente_name + " " + paciente_lastname
        return render_template(
            "interface_patient.html",
            paciente_id=paciente_id,
            paciente_name=full_name_pacient,
        )
    else:
        abort(404)


@app.route("/interface_doctor/<int:doctor_id>", methods=["POST", "GET"])
def interface_doctor(doctor_id):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, lastName FROM Doctors WHERE id = ?", (doctor_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        doctor_name = result[0]
        doctor_lastname = result[1]
        full_name_doctor = doctor_name + " " + doctor_lastname
        return render_template(
            "interface_doctor.html", doctor_id=doctor_id, doctor_name=full_name_doctor
        )
    else:
        abort(404)


@app.route("/interface_admin", methods=["POST", "GET"])
def interface_admin():
    return render_template("interface_admin.html")


@app.route("/show_patients_admin")
def show_patients_admin():
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Patients")
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("show_patients_admin.html", pacientes=resultados)


@app.route("/show_doctors_admin")
def show_doctors_admin():
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Doctors")
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("show_doctors_admin.html", doctores=resultados)


@app.route("/add_patient", methods=["POST", "GET"])
def add_patient():
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        documento = request.form["documento"]
        telefono = request.form["telefono"]
        date = request.form["fecha_nacimiento"]
        correo = request.form["correo"]
        contrasena = request.form["contrasena"]
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Patients (name, lastName,document,telf,date,email,password) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (nombre, apellido, documento, telefono, date, correo, contrasena),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("successful_registration"))
    return render_template("add_patient.html")


@app.route("/successful_registration", methods=["GET"])
def successful_registration():
    return render_template("successful_registration.html")


@app.route("/add_doctor", methods=["POST", "GET"])
def add_doctor():
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        descripcion = request.form["descripcion"]
        dni = request.form["documento"]
        contrasena = request.form["contrasena"]
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Doctors (name, lastName, description, document, password) VALUES ( ?, ?, ?, ?, ?)",
            (nombre, apellido, descripcion, dni, contrasena),
        )
        conn.commit()
        conn.close()
        return redirect("/show_doctors_admin")
    return render_template("add_doctor.html")


@app.route("/create_date/<int:paciente_id>/<paciente_name>", methods=["POST", "GET"])
def create_date(paciente_id, paciente_name):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Doctors")
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    if request.method == "POST":
        id_paciente = paciente_id
        id_doctor = request.form["doctor_d"]
        date = request.form["fecha"]
        type = request.form["type_d"]
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Date (id_patient, id_doctor, date, type) VALUES ( ?, ?, ?, ?)",
            (id_paciente, id_doctor, date, type),
        )
        conn.commit()
        conn.close()
        return render_template(
            "date_ok.html", paciente_id=paciente_id, paciente_name=paciente_name
        )
    return render_template(
        "create_date.html",
        paciente_id=paciente_id,
        paciente_name=paciente_name,
        doctors=resultados,
    )


@app.route("/show_patients/<int:doctor_id>/<doctor_name>")
def show_patients(doctor_id, doctor_name):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Patients")
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template(
        "show_patients.html",
        pacientes=resultados,
        doctor_id=doctor_id,
        doctor_name=doctor_name,
    )


@app.route("/show_dates/<int:doctor_id>/<doctor_name>")
def show_dates(doctor_id, doctor_name):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * 
        FROM Date
        INNER JOIN Patients ON Date.id_patient = Patients.id
        WHERE Date.id_doctor=?;
    """,
        (doctor_id,),
    )
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template(
        "show_dates.html",
        doctor_id=doctor_id,
        doctor_name=doctor_name,
        dates=resultados,
    )


@app.route("/show_record/<int:doctor_id>/<doctor_name>")
def show_record(doctor_id, doctor_name):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """
    SELECT * 
    FROM Record
    INNER JOIN Patients ON Record.id_patient = Patients.id
    ORDER BY Record.id DESC;
    """
    )
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template(
        "show_record.html",
        doctor_id=doctor_id,
        doctor_name=doctor_name,
        record=resultados,
    )


@app.route("/show_record_image/<int:doctor_id>/<doctor_name>/<record_img>")
def show_record_image(doctor_id, doctor_name, record_img):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT image_url FROM RECORD WHERE id = ?", (record_img,))
    result = cursor.fetchone()
    conn.close()
    return render_template(
        "show_record_image.html",
        doctor_id=doctor_id,
        doctor_name=doctor_name,
        record_img=result[0],
    )


@app.route(
    "/predict_section/<int:paciente_id>/<paciente_name>", methods=["POST", "GET"]
)
def predict_section(paciente_id, paciente_name):
    return render_template(
        "predict_section.html", paciente_id=paciente_id, paciente_name=paciente_name
    )


@app.route("/mostrar_imagen/<int:paciente_id>/<paciente_name>", methods=["POST", "GET"])
def upload_image(paciente_id, paciente_name):
    global id_imagen
    if "file" not in request.files:
        return render_template("index.html")

    if "file" not in request.files:
        return render_template("index.html")

    file = request.files["file"]

    if file.filename == "":
        return render_template("index.html")

    if file and allowed_file(file.filename):
        uploaded_image = file.read()
        encoded_image = base64.b64encode(uploaded_image).decode("utf-8")

        image = cv2.imdecode(
            np.fromstring(uploaded_image, np.uint8), cv2.IMREAD_UNCHANGED
        )
        if image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

        # Guardar imagen
        if isinstance(image, np.ndarray):
            _, enc_img = cv2.imencode(".jpg", image)
        with open("app/imagen.jpg", "wb") as f:
            f.write(enc_img)

        # Validar image
        if not validate_image():
            return redirect(
                url_for(
                    "bad_image", paciente_id=paciente_id, paciente_name=paciente_name
                )
            )
        else:
            # -----------------------------------
            image_name = f"record/disease_{id_imagen}.jpg"
            image_rute = "app/static/" + image_name
            print(image_rute)
            shutil.copy("app/imagen.jpg", image_rute)
            id_imagen = id_imagen + 1
            # -----------------------------------
            resized_image = cv2.resize(image, (256, 256))
            flattened_image = resized_image.reshape(-1)
            predicted_label = svm_model.predict([flattened_image])
            predicted_class = disease_folders[int(predicted_label)]

            # -------------------------------------
            confidence_scores = svm_model.decision_function(
                flattened_image.reshape(1, -1)
            )
            confidence = np.max(confidence_scores)

            # Normalizar la confianza a un rango de 0 a 1
            normalized_confidence = 1 / (1 + np.exp(-confidence))
            print("NORMALIZED_CONFIDENCE:", normalized_confidence)
            # -------------------------------------

            if predicted_class == "PSORIASIS":
                conn = sqlite3.connect(database_path)
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE Patients SET disease = ? WHERE id = ?",
                    (predicted_class, paciente_id),
                )
                cursor.execute(
                    "SELECT email FROM Patients WHERE id = ?", (paciente_id,)
                )
                paciente_correo = cursor.fetchone()

                # ENVIAR CORREO
                enviar_correo(
                    paciente_correo[0],
                    "Psoriasis",
                    paciente_name,
                    normalized_confidence,
                )

                # AGREGAR A REGISTROS
                cursor.execute(
                    "INSERT INTO Record (id_patient, image_url,disease) VALUES ( ?, ?, ?)",
                    (paciente_id, image_name, "Psoriasis"),
                )

                conn.commit()
                conn.close()

                return render_template(
                    "case_psoriasis.html",
                    mensaje=predicted_class,
                    image=encoded_image,
                    paciente_id=paciente_id,
                    paciente_name=paciente_name,
                )
            if predicted_class == "ROSACEA":
                conn = sqlite3.connect(database_path)
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE Patients SET disease = ? WHERE id = ?",
                    (predicted_class, paciente_id),
                )
                cursor.execute(
                    "SELECT email FROM Patients WHERE id = ?", (paciente_id,)
                )
                paciente_correo = cursor.fetchone()
                # ENVIAR CORREO
                enviar_correo(
                    paciente_correo[0], "Rosacea", paciente_name, normalized_confidence
                )

                # AGREGAR A REGISTROS
                cursor.execute(
                    "INSERT INTO Record (id_patient, image_url,disease) VALUES ( ?, ?, ?)",
                    (paciente_id, image_name, "Rosacea"),
                )

                conn.commit()
                conn.close()

                return render_template(
                    "case_rosacea.html",
                    mensaje=predicted_class,
                    image=encoded_image,
                    paciente_id=paciente_id,
                    paciente_name=paciente_name,
                )
            if predicted_class == "SARPULLIDO":
                conn = sqlite3.connect(database_path)
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE Patients SET disease = ? WHERE id = ?",
                    (predicted_class, paciente_id),
                )
                cursor.execute(
                    "SELECT email FROM Patients WHERE id = ?", (paciente_id,)
                )
                paciente_correo = cursor.fetchone()
                # ENVIAR CORREO
                enviar_correo(
                    paciente_correo[0],
                    "Sarpullido",
                    paciente_name,
                    normalized_confidence,
                )

                # AGREGAR A REGISTROS
                cursor.execute(
                    "INSERT INTO Record (id_patient, image_url,disease) VALUES ( ?, ?, ?)",
                    (paciente_id, image_name, "Sarpullido"),
                )

                conn.commit()
                conn.close()

                return render_template(
                    "case_sarpullido.html",
                    mensaje=predicted_class,
                    image=encoded_image,
                    paciente_id=paciente_id,
                    paciente_name=paciente_name,
                )
            if predicted_class == "VITILIGO":
                conn = sqlite3.connect(database_path)
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE Patients SET disease = ? WHERE id = ?",
                    (predicted_class, paciente_id),
                )
                cursor.execute(
                    "SELECT email FROM Patients WHERE id = ?", (paciente_id,)
                )
                paciente_correo = cursor.fetchone()
                # ENVIAR CORREO
                enviar_correo(
                    paciente_correo[0], "Vitiligo", paciente_name, normalized_confidence
                )

                # AGREGAR A REGISTROS
                cursor.execute(
                    "INSERT INTO Record (id_patient, image_url,disease) VALUES ( ?, ?, ?)",
                    (paciente_id, image_name, "Vitiligo"),
                )

                conn.commit()
                conn.close()

                return render_template(
                    "case_vitiligio.html",
                    mensaje=predicted_class,
                    image=encoded_image,
                    paciente_id=paciente_id,
                    paciente_name=paciente_name,
                )


@app.route(
    "/mostrar_imagen/bad_image/<int:paciente_id>/<paciente_name>", methods=["GET"]
)
def bad_image(paciente_id, paciente_name):
    return render_template(
        "case_wrong_image.html", paciente_id=paciente_id, paciente_name=paciente_name
    )


if __name__ == "__main__":
    app.run(debug=True)
