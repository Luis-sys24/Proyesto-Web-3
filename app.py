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


# ======================================
# CRUD PROFESORES
# ======================================
@app.route('/profesores')
def profesores():
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM profesor")
    data = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template("profesores.html", profesores=data)

@app.route('/profesores/agregar', methods=['POST'])
def agregar_profesor():
    nombre = request.form['nombre']
    materia = request.form['materia']

    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO profesor (nombre, materia) VALUES (%s, %s)", (nombre, materia))
    conexion.commit()
    cursor.close()
    conexion.close()

    flash("Profesor agregado correctamente")
    return redirect(url_for('profesores'))

@app.route('/profesores/eliminar/<int:id>')
def eliminar_profesor(id):
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM profesor WHERE id = %s", (id,))
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
        SELECT c.id, c.nombre AS clase,
               p.nombre AS profesor 
        FROM clase c
        LEFT JOIN profesor p ON c.profesor_id = p.id
    """)
    data = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template("clases.html", clases=data)

@app.route('/clases/agregar', methods=['POST'])
def agregar_clase():
    nombre = request.form['nombre']
    profesor = request.form['profesor_id']

    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO clase (nombre, profesor_id) VALUES (%s, %s)", (nombre, profesor))
    conexion.commit()
    cursor.close()
    conexion.close()

    flash("Clase agregada correctamente")
    return redirect(url_for('clases'))

@app.route('/clases/eliminar/<int:id>')
def eliminar_clase(id):
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM clase WHERE id = %s", (id,))
    conexion.commit()
    cursor.close()
    conexion.close()

    flash("Clase eliminada")
    return redirect(url_for('clases'))

# ======================================
# CRUD ASISTENCIAS
# ======================================
@app.route('/asistencia')
def asistencia():
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT a.id, al.nombre AS alumno, cl.nombre AS clase, a.fecha, a.estado
        FROM asistencia a
        INNER JOIN alumno al ON a.alumno_id = al.id
        INNER JOIN clase cl ON a.clase_id = cl.id
    """)
    data = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template("asistencia.html", asistencias=data)

@app.route('/asistencia/marcar', methods=['POST'])
def marcar_asistencia():
    alumno_id = request.form['alumno_id']
    clase_id = request.form['clase_id']
    estado = request.form['estado']

    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO asistencia (alumno_id, clase_id, fecha, estado)
        VALUES (%s, %s, CURDATE(), %s)
    """, (alumno_id, clase_id, estado))
    conexion.commit()
    cursor.close()
    conexion.close()

    flash("Asistencia registrada")
    return redirect(url_for('asistencia'))

@app.route('/asistencia/eliminar/<int:id>')
def eliminar_asistencia(id):
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM asistencia WHERE id = %s", (id,))
    conexion.commit()
    cursor.close()
    conexion.close()

    flash("Asistencia eliminada")
    return redirect(url_for('asistencia'))

# ======================================
# INICIO DE LA APP
# ======================================
if __name__ == '__main__':
    app.run(debug=True)
