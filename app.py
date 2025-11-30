from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql

# ======================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ======================================
app = Flask(__name__)
app.secret_key = 'secreto123'   # Necesario para mensajes flash

# ======================================
# FUNCIÓN PARA CONECTAR A MYSQL
# ======================================
def get_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='registro_de_asistencia_escolar',
        cursorclass=pymysql.cursors.DictCursor
    )

# ======================================
# RUTA PRINCIPAL
# ======================================
@app.route('/')
def index():
    return render_template("index.html")

# ======================================
# CRUD ALUMNOS
# ======================================
@app.route('/alumnos')
def alumnos():
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM alumno")
    data = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template("alumnos.html", alumnos=data)

@app.route('/alumnos/agregar', methods=['POST'])
def agregar_alumno():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    curso = request.form['curso']

    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO alumno (nombre, apellido, curso) VALUES (%s, %s, %s)", (nombre, apellido, curso))
    conexion.commit()
    cursor.close()
    conexion.close()

    flash("Alumno agregado correctamente")
    return redirect(url_for('alumnos'))

@app.route('/alumnos/eliminar/<int:id>')
def eliminar_alumno(id):
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM alumno WHERE id = %s", (id,))
    conexion.commit()
    cursor.close()
    conexion.close()

    flash("Alumno eliminado")
    return redirect(url_for('alumnos'))

# ======================================
# EDITAR ALUMNO (FORMULARIO)
# ======================================
@app.route('/alumnos/editar/<int:id>')
def editar_alumno(id):
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM alumno WHERE id = %s", (id,))
    alumno = cursor.fetchone()
    cursor.close()
    conexion.close()

    return render_template("alumno_form.html", alumno=alumno, accion="Editar")


# ======================================
# GUARDAR CAMBIOS EN ALUMNO
# ======================================
@app.route('/alumnos/actualizar/<int:id>', methods=['POST'])
def actualizar_alumno(id):
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    curso = request.form['curso']

    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE alumno 
        SET nombre=%s, apellido=%s, curso=%s
        WHERE id=%s
    """, (nombre, apellido, curso, id))
    conexion.commit()
    cursor.close()
    conexion.close()

    flash("Alumno actualizado correctamente")
    return redirect(url_for('alumnos'))


# =========================
#  PROFESORES
# =========================

@app.route('/profesores')
def profesores():
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("SELECT id_profesor, nombre, email, materia FROM profesor")
    profesores = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template('profesores.html', profesores=profesores)


@app.route('/profesores/agregar', methods=['POST'])
def agregar_profesor():
    nombre = request.form['nombre']
    email = request.form['email']
    materia = request.form['materia']

    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO profesor (nombre, email, materia) VALUES (%s, %s, %s)",
        (nombre, email, materia)
    )
    conexion.commit()
    cursor.close()
    conexion.close()

    flash("Profesor agregado correctamente")
    return redirect(url_for('profesores'))


@app.route('/profesores/eliminar/<int:id_profesor>')
def eliminar_profesor(id_profesor):
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM profesor WHERE id_profesor=%s", (id_profesor,))
    conexion.commit()
    cursor.close()
    conexion.close()

    flash("Profesor eliminado")
    return redirect(url_for('profesores'))

# ======================================
# CRUD CLASES
# ======================================
@app.route('/clases')
def clases():
    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT c.id_clase, c.nombre_clase, p.nombre AS profesor
        FROM clase c
        LEFT JOIN profesor p ON c.id_profesor = p.id_profesor
    """)
    clases = cursor.fetchall()

    cursor.execute("SELECT id_profesor, nombre FROM profesor")
    profesores = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template('clases.html', clases=clases, profesores=profesores)

# ======================================
# AGREGAR CLASES
# ======================================
@app.route('/clases/agregar', methods=['POST'])
def agregar_clase():
    nombre_clase = request.form['nombre_clase']
    id_profesor = request.form['id_profesor']

    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO clase (nombre_clase, id_profesor) VALUES (%s, %s)",
        (nombre_clase, id_profesor)
    )
    conexion.commit()
    cursor.close()
    conexion.close()

    flash("Clase agregada correctamente")
    return redirect(url_for('clases'))
# ======================================
# ELIMINAR CLASE
# ======================================
@app.route('/clases/eliminar/<int:id_clase>')
def eliminar_clase(id_clase):
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM clase WHERE id_clase = %s", (id_clase,))
    conexion.commit()
    cursor.close()
    conexion.close()

    flash("Clase eliminada")
    return redirect(url_for('clases'))

# ======================================
# CRUD ASISTENCIAS
# ======================================

@app.route("/asistencia")
def asistencia():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT a.id_asistencia, al.nombre AS alumno, c.nombre_clase AS clase,
               a.fecha, a.presente
        FROM asistencia a
        INNER JOIN alumno al ON a.id_alumno = al.id_alumno
        INNER JOIN clase c ON a.id_clase = c.id_clase
        ORDER BY a.fecha DESC
    """)
    asistencias = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("asistencia.html", asistencias=asistencias)
# ======================================
# FORMULARIO PARA AGREGAR ASISTENCIA
# ======================================
@app.route("/asistencia/nueva")
def asistencia_nueva():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id_alumno, nombre FROM alumno")
    alumnos = cursor.fetchall()

    cursor.execute("SELECT id_clase, nombre_clase FROM clase")
    clases = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("asistencia_nueva.html", alumnos=alumnos, clases=clases)

# ======================================
# REGISTRAR ASISTENCIA (POST)
# ======================================
@app.route("/asistencia/agregar", methods=["POST"])
def asistencia_agregar():
    id_alumno = request.form["id_alumno"]
    id_clase = request.form["id_clase"]
    fecha = request.form["fecha"]
    presente = 1 if "presente" in request.form else 0

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO asistencia (id_alumno, id_clase, fecha, presente)
        VALUES (%s, %s, %s, %s)
    """, (id_alumno, id_clase, fecha, presente))

    conn.commit()
    cursor.close()
    conn.close()

    flash("Asistencia registrada correctamente")
    return redirect(url_for("asistencia"))
# ======================================
# INICIO DE LA APP
# ======================================
if __name__ == '__main__':
    app.run(debug=True)
