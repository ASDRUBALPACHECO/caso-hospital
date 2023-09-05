import sqlite3

# Clase Paciente
class Paciente:
    def __init__(self, documento, nombre, sexo, fecha_nacimiento):
        self.documento = documento
        self.nombre = nombre
        self.sexo = sexo
        self.fecha_nacimiento = fecha_nacimiento
        self.signos_vitales = {}
        self.notas_evolucion = []
        self.imagenes_diagnosticas = []
        self.resultados_laboratorio = []
        self.medicamentos = []

    def agregar_signos_vitales(self, presion_arterial, temperatura, saturacion_o2, frecuencia_respiratoria):
        self.signos_vitales = {
            'Presión Arterial': presion_arterial,
            'Temperatura': temperatura,
            'Saturación O2': saturacion_o2,
            'Frecuencia Respiratoria': frecuencia_respiratoria
        }

    def agregar_nota_evolucion(self, nota):
        self.notas_evolucion.append(nota)

    def agregar_imagen_diagnostica(self, imagen):
        self.imagenes_diagnosticas.append(imagen)

    def agregar_resultado_laboratorio(self, resultado):
        self.resultados_laboratorio.append(resultado)

    def agregar_medicamento(self, medicamento):
        self.medicamentos.append(medicamento)

# Clase Hospital
class Hospital:
    def __init__(self, nombre, direccion):
        self.nombre = nombre
        self.direccion = direccion
        self.conexion_db = sqlite3.connect('hospital.db')
        self.crear_tablas()

    def crear_tablas(self):
        cursor = self.conexion_db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pacientes (
                documento TEXT PRIMARY KEY,
                nombre TEXT,
                sexo TEXT,
                fecha_nacimiento TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signos_vitales (
                documento_paciente TEXT PRIMARY KEY,
                presion_arterial TEXT,
                temperatura TEXT,
                saturacion_o2 TEXT,
                frecuencia_respiratoria TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notas_evolucion (
                documento_paciente TEXT,
                nota TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medicamentos (
                documento_paciente TEXT,
                medicamento TEXT
            )
        ''')
        
        self.conexion_db.commit()

    def ingresar_paciente(self, paciente):
        cursor = self.conexion_db.cursor()
        cursor.execute('''
            INSERT INTO pacientes (documento, nombre, sexo, fecha_nacimiento)
            VALUES (?, ?, ?, ?)
        ''', (paciente.documento, paciente.nombre, paciente.sexo, paciente.fecha_nacimiento))
        
        # Insertar signos vitales
        cursor.execute('''
            INSERT INTO signos_vitales (documento_paciente, presion_arterial, temperatura, saturacion_o2, frecuencia_respiratoria)
            VALUES (?, ?, ?, ?, ?)
        ''', (paciente.documento, paciente.signos_vitales.get('Presión Arterial', ''), paciente.signos_vitales.get('Temperatura', ''), paciente.signos_vitales.get('Saturación O2', ''), paciente.signos_vitales.get('Frecuencia Respiratoria', '')))
        
        # Insertar notas de evolución
        for nota in paciente.notas_evolucion:
            cursor.execute('''
                INSERT INTO notas_evolucion (documento_paciente, nota)
                VALUES (?, ?)
            ''', (paciente.documento, nota))
        
        # Insertar medicamentos
        for medicamento in paciente.medicamentos:
            cursor.execute('''
                INSERT INTO medicamentos (documento_paciente, medicamento)
                VALUES (?, ?)
            ''', (paciente.documento, medicamento))
        
        self.conexion_db.commit()
        print(f'Paciente {paciente.nombre} ingresado con éxito.')

    def buscar_paciente(self, documento):
        cursor = self.conexion_db.cursor()
        cursor.execute('SELECT * FROM pacientes WHERE documento = ?', (documento,))
        paciente_data = cursor.fetchone()
        if paciente_data:
            paciente = Paciente(paciente_data[0], paciente_data[1], paciente_data[2], paciente_data[3])
            
            # Recuperar información adicional
            cursor.execute('SELECT * FROM signos_vitales WHERE documento_paciente = ?', (documento,))
            signos_vitales_data = cursor.fetchone()
            if signos_vitales_data:
                paciente.agregar_signos_vitales(*signos_vitales_data[1:])
            
            cursor.execute('SELECT nota FROM notas_evolucion WHERE documento_paciente = ?', (documento,))
            notas_data = cursor.fetchall()
            for nota in notas_data:
                paciente.agregar_nota_evolucion(nota[0])
            
            cursor.execute('SELECT medicamento FROM medicamentos WHERE documento_paciente = ?', (documento,))
            medicamentos_data = cursor.fetchall()
            for medicamento in medicamentos_data:
                paciente.agregar_medicamento(medicamento[0])
            
            return paciente
        else:
            return None

# Función para ingresar datos de un paciente
def ingresar_datos_paciente():
    documento = input("Documento del paciente: ")
    nombre = input("Nombre del paciente: ")
    sexo = input("Sexo del paciente: ")
    fecha_nacimiento = input("Fecha de nacimiento del paciente (dd/mm/yyyy): ")

    paciente = Paciente(documento, nombre, sexo, fecha_nacimiento)

    presion_arterial = input("Presión Arterial: ")
    temperatura = input("Temperatura: ")
    saturacion_o2 = input("Saturación O2: ")
    frecuencia_respiratoria = input("Frecuencia Respiratoria: ")

    paciente.agregar_signos_vitales(presion_arterial, temperatura, saturacion_o2, frecuencia_respiratoria)

    notas = input("Notas de evolución (separadas por coma): ").split(',')
    for nota in notas:
        paciente.agregar_nota_evolucion(nota.strip())

    medicamentos = input("Medicamentos formulados (separados por coma): ").split(',')
    for medicamento in medicamentos:
        paciente.agregar_medicamento(medicamento.strip())

    return paciente

if __name__ == "__main__":
    hospital = Hospital("Hospital XYZ", "123 Calle Principal")

    while True:
        # Ingresar un nuevo paciente
        paciente = ingresar_datos_paciente()
        hospital.ingresar_paciente(paciente)

        continuar = input("¿Desea ingresar otro paciente? (S/N): ").strip().lower()
        if continuar != 's':
            break

    while True:
        documento_buscar = input("Ingrese el documento del paciente que desea buscar (o 'salir' para terminar): ").strip()
        
        if documento_buscar.lower() == 'salir':
            break

        paciente_buscado = hospital.buscar_paciente(documento_buscar)
        if paciente_buscado:
            print(f'Datos del paciente encontrado:')
            print(f'Documento: {paciente_buscado.documento}')
            print(f'Nombre: {paciente_buscado.nombre}')
            print(f'Sexo: {paciente_buscado.sexo}')
            print(f'Fecha de nacimiento: {paciente_buscado.fecha_nacimiento}')
            print(f'Signos vitales: {paciente_buscado.signos_vitales}')
            print(f'Notas de evolución: {", ".join(paciente_buscado.notas_evolucion)}')
            print(f'Medicamentos: {", ".join(paciente_buscado.medicamentos)}')
        else:
            print('Paciente no encontrado.')

    hospital.conexion_db.close()
