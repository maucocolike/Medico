from flask import Flask, request, jsonify, render_template, redirect, url_for, session, g
import mysql.connector

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'  # Necesaria para manejar sesiones

# Conexión a la base de datos MySQL
def obtener_conexion_db():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Ganstar12',
        database='Medico',
        auth_plugin='mysql_native_password'  # Especifica el plugin de autenticación aquí
    )
    return conn

# Ruta para el inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        rfc = request.form['RFC']
        contrasena = request.form['Contrasena']
        
        # Verificar las credenciales
        conn = obtener_conexion_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT Medicos.*, Roles.Tipo_rol 
            FROM Medicos 
            JOIN Roles ON Medicos.RolID = Roles.RolID 
            WHERE RFC = %s AND Contrasena = %s
        """, (rfc, contrasena))
        medico = cursor.fetchone()

        if medico:
            session['medico_id'] = medico['MedicoID']  # Guardar el ID en la sesión
            session['tipo_rol'] = medico['Tipo_rol']  # Guardar el rol en la sesión
            return redirect(url_for('inicio'))
        else:
            return render_template('login.html', error='Credenciales incorrectas')

    return render_template('login.html')

# Middleware para autenticar al usuario
@app.before_request
def autenticar_usuario():
    if 'medico_id' not in session and request.endpoint not in ('login', 'static'):
        return redirect(url_for('login'))
    if 'medico_id' in session:
        conn = obtener_conexion_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT Medicos.*, Roles.Tipo_rol, Genero.Tipo_genero 
            FROM Medicos 
            JOIN Roles ON Medicos.RolID = Roles.RolID 
            LEFT JOIN Genero ON Medicos.GeneroID = Genero.GeneroID
            WHERE MedicoID = %s
        """, (session['medico_id'],))
        medico = cursor.fetchone()
        if medico:
            g.medico = medico
        else:
            # Si no se encuentra el médico, limpiar la sesión y redirigir al login
            session.clear()
            return redirect(url_for('login'))


@app.route('/')
def inicio():
    if 'medico_id' in session:
        nombre_medico = g.medico['Nombre']
        tipo_genero = g.medico.get('Tipo_genero', 'Desconocido')  # Obtener el género del médico
        
        if tipo_genero.lower() == 'masculino':
            saludo = "Bienvenido"
            titulo = "Dr."
        elif tipo_genero.lower() == 'femenino':
            saludo = "Bienvenida"
            titulo = "Dra."
        else:
            saludo = "Bienvenid@"
            titulo = "Dr./Dra."  # En caso de que el género no esté definido claramente
        
        nombre_completo = f"{titulo} {nombre_medico}"
        return render_template('index.html', saludo=saludo, nombre_medico=nombre_completo)
    else:
        return redirect(url_for('login'))


# CRUD para Médicos
@app.route('/medicos', methods=['GET', 'POST'])
def gestionar_medicos():
    if g.medico['Tipo_rol'] != 'administrador':
        return jsonify({"error": "Acceso denegado"}), 403
    
    conn = obtener_conexion_db()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        # Crear un nuevo médico
        datos = request.form  # Usar request.form si envías datos desde un formulario HTML
        cursor.execute(
            "INSERT INTO Medicos (RFC, Nombre, Cedula, Correo, Contrasena, RolID, EspecialidadID) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (datos['RFC'], datos['Nombre'], datos['Cedula'], datos['Correo'], datos['Contrasena'], datos['RolID'], datos['EspecialidadID'])
        )
        conn.commit()
        return redirect(url_for('gestionar_medicos'))
    
    elif request.method == 'GET':
        # Leer todos los médicos (solo accesible para administradores)
        cursor.execute("SELECT * FROM Medicos")
    
        medicos = cursor.fetchall()
        return render_template('medicos.html', medicos=medicos)

@app.route('/medicos/<int:MedicoID>', methods=['GET', 'PUT', 'DELETE'])
def gestionar_medico(MedicoID):
    if g.medico['Tipo_rol'] != 'administrador':
        return jsonify({"error": "Acceso denegado"}), 403

    conn = obtener_conexion_db()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'GET':
        # Obtener un médico específico
        cursor.execute("SELECT * FROM Medicos WHERE MedicoID = %s", (MedicoID,))
        medico = cursor.fetchone()
        if medico:
            return jsonify(medico)
        else:
            return jsonify({"error": "Médico no encontrado"}), 404
    
    elif request.method == 'PUT':
        # Actualizar la información de un médico
        datos = request.json
        cursor.execute(
            "UPDATE Medicos SET RFC = %s, Nombre = %s, Cedula = %s, Correo = %s, Contrasena = %s, RolID = %s, EspecialidadID = %s "
            "WHERE MedicoID = %s",
            (datos['RFC'], datos['Nombre'], datos['Cedula'], datos['Correo'], datos['Contrasena'], datos['RolID'], datos['EspecialidadID'], MedicoID)
        )
        conn.commit()
        return jsonify({"mensaje": "Médico actualizado exitosamente"})
    
    elif request.method == 'DELETE':
        # Eliminar un médico
        cursor.execute("DELETE FROM Medicos WHERE MedicoID = %s", (MedicoID,))
        conn.commit()
        return jsonify({"mensaje": "Médico eliminado exitosamente"})

#registro de actividades realizadas en el crud de medicos
#se usa la tabla log_actividades que ya actualice en medico.sql
def get_logs():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM log_actividades ORDER BY Fecha DESC")
    logs = cursor.fetchall()
    cursor.close()
    connection.close()
    return logs
#se crea la ruta actividades (no se como aplicarla a la pagina) 
#pero yo siento que poniendo un boton que se vaya a esta ruta
@app.route('/actividades')
def actividades():
    logs = get_logs()
    return render_template('actividades.html', logs=logs)

# CRUD para Pacientes
@app.route('/pacientes', methods=['GET', 'POST'])
def gestionar_pacientes():
    conn = obtener_conexion_db()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        # Crear un nuevo paciente (solo accesible para administradores)
        if g.medico['Tipo_rol'] != 'administrador':
            return jsonify({"error": "Acceso denegado"}), 403

        datos = request.form  # Usar request.form si envías datos desde un formulario HTML
        cursor.execute(
            "INSERT INTO Pacientes (Nombre, Resultado_exploracion) "
            "VALUES (%s, %s)",
            (datos['Nombre'], datos['Resultado_exploracion'])
        )
        conn.commit()
        return redirect(url_for('gestionar_pacientes'))
    
    elif request.method == 'GET':
        # Leer todos los pacientes (accesible para ambos roles)
        if g.medico['Tipo_rol'] == 'administrador':
            cursor.execute("SELECT * FROM Pacientes")
        else:
            # Médico normal solo ve sus pacientes
            cursor.execute("""
                SELECT * FROM Pacientes
                WHERE PacienteID IN (
                    SELECT PacienteID FROM Citas WHERE MedicoID = %s
                )
            """, (g.medico['MedicoID'],))
        
        pacientes = cursor.fetchall()
        return render_template('pacientes.html', pacientes=pacientes)

@app.route('/pacientes/<int:PacienteID>', methods=['GET', 'PUT', 'DELETE'])
def gestionar_paciente(PacienteID):
    conn = obtener_conexion_db()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'GET':
        # Obtener un paciente específico (accesible para ambos roles)
        cursor.execute("SELECT * FROM Pacientes WHERE PacienteID = %s", (PacienteID,))
        paciente = cursor.fetchone()
        if paciente:
            return jsonify(paciente)
        else:
            return jsonify({"error": "Paciente no encontrado"}), 404
    
    elif request.method == 'PUT':
        # Actualizar la información de un paciente (solo accesible para administradores)
        if g.medico['Tipo_rol'] != 'administrador':
            return jsonify({"error": "Acceso denegado"}), 403

        datos = request.json
        cursor.execute(
            "UPDATE Pacientes SET Nombre = %s, Resultado_exploracion = %s WHERE PacienteID = %s",
            (datos['Nombre'], datos['Resultado_exploracion'], PacienteID)
        )
        conn.commit()
        return jsonify({"mensaje": "Paciente actualizado exitosamente"})
    
    elif request.method == 'DELETE':
        # Eliminar un paciente (solo accesible para administradores)
        if g.medico['Tipo_rol'] != 'administrador':
            return jsonify({"error": "Acceso denegado"}), 403

        cursor.execute("DELETE FROM Pacientes WHERE PacienteID = %s", (PacienteID,))
        conn.commit()
        return jsonify({"mensaje": "Paciente eliminado exitosamente"})
    
# Rutas adicionales para las funcionalidades de la aplicación
@app.route('/menu')
def menu():
    return render_template('menu.html')  # Aquí iría la plantilla HTML para el menú

@app.route('/cuenta')
def cuenta():
    return render_template('cuenta.html')  # Aquí iría la plantilla HTML para la cuenta

@app.route('/consulta')
def consulta():
    return render_template('consulta.html')  # Aquí iría la plantilla HTML para la consulta

@app.route('/citas')
def citas():
    return render_template('citas.html')  # Aquí iría la plantilla HTML para las citas

@app.route('/nueva_cita', methods=['GET', 'POST'])
def nueva_cita():
    if request.method == 'POST':
        nombre_paciente = request.form['nombre_paciente']
        apellido1_paciente = request.form['apellido1_paciente']
        apellido2_paciente = request.form.get('apellido2_paciente')
        rfc_medico = request.form['rfc_medico']
        dia = request.form['dia']
        mes = request.form['mes']
        ano = request.form['ano']
        hora = request.form['hora']
        
        # Aquí realizarías la lógica para crear la cita, incluyendo la inserción en la base de datos
        # Ejemplo:
        fecha_cita = f"{ano}-{mes}-{dia} {hora}"
        conn = obtener_conexion_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Citas (nombre_paciente, apellido1_paciente, apellido2_paciente, rfc_medico, fecha_cita)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre_paciente, apellido1_paciente, apellido2_paciente, rfc_medico, fecha_cita))
        conn.commit()
        return redirect(url_for('citas'))  # Redirige a la lista de citas u otra página apropiada

    return render_template('nueva_cita.html')
  # Aquí iría la plantilla HTML para agendar una nueva cita

@app.route('/expediente')
def expediente():
    return render_template('expediente.html')  # Aquí iría la plantilla HTML para el expediente

if __name__ == '__main__':
    app.run(debug=True)
