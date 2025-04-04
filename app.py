from flask import Flask, render_template, request, jsonify, send_file
import random
from datetime import datetime
from fpdf import FPDF
import os
import tempfile

app = Flask(__name__)

# Configuración de las loterías
loterias = {
    'boyaca': {'nombre': 'Boyacá', 'premio_base': 150000000},
    'valle': {'nombre': 'Valle', 'premio_base': 150000000},
    'huila': {'nombre': 'Huila', 'premio_base': 150000000},
    'tolima': {'nombre': 'Tolima', 'premio_base': 150000000},
    'bogota': {'nombre': 'Bogotá', 'premio_base': 150000000},
    'quindio': {'nombre': 'Quindío', 'premio_base': 150000000}
}

# Historial de números ganadores
historial_ganadores = []

# Configuración de valores por modalidad
valores_modalidad = {
    '1': {'min': 1000, 'max': 10000},
    '2': {'min': 1000, 'max': 10000},
    '3': {'min': 1000, 'max': 10000},
    '4': {'min': 1000, 'max': 10000}
}

@app.route('/')
def index():
    return render_template('index.html')

def generar_pdf_apuesta(numero, modalidad, valor_apuesta, loteria):
    pdf = FPDF()
    pdf.add_page()
    
    # Título en azul menta
    pdf.set_font('Arial', 'B', 24)
    pdf.set_text_color(0, 255, 170)  # Color azul menta
    pdf.cell(0, 20, 'Apuesta & Gana - Comprobante', 0, 1, 'C')
    
    # Datos en azul oscuro
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(0, 0, 139)  # Azul oscuro
    pdf.cell(0, 10, f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', 0, 1)
    pdf.cell(0, 10, f'Lotería: {loterias[loteria]["nombre"]}', 0, 1)
    pdf.cell(0, 10, f'Modalidad: {modalidad} cifra(s)', 0, 1)
    pdf.cell(0, 10, f'Número apostado: {numero}', 0, 1)
    pdf.cell(0, 10, f'Valor apostado: ${valor_apuesta:,}', 0, 1)
    
    try:
        temp_dir = tempfile.gettempdir()
        temp_pdf = os.path.join(temp_dir, f'apuesta_{datetime.now().strftime("%Y%m%d%H%M%S")}.pdf')
        pdf.output(temp_pdf)
        if not os.path.exists(temp_pdf):
            raise Exception('Error al generar el archivo PDF')
        return temp_pdf
    except Exception as e:
        if 'temp_pdf' in locals() and os.path.exists(temp_pdf):
            try:
                os.remove(temp_pdf)
            except:
                pass
        raise Exception('Error al generar el PDF de la apuesta')

def generar_pdf_historico():
    pdf = FPDF()
    pdf.add_page()
    
    # Título en azul menta
    pdf.set_font('Arial', 'B', 24)
    pdf.set_text_color(0, 255, 170)  # Color azul menta
    pdf.cell(0, 20, 'Historial de Números Ganadores', 0, 1, 'C')
    
    # Datos en azul oscuro
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(0, 0, 139)  # Azul oscuro
    
    for registro in historial_ganadores:
        pdf.cell(0, 10, f'Fecha: {registro["fecha"]}', 0, 1)
        pdf.cell(0, 10, f'Lotería: {registro["loteria"]}', 0, 1)
        pdf.cell(0, 10, f'Número Ganador: {registro["numero"]}', 0, 1)
        pdf.cell(0, 10, '-------------------', 0, 1)
    
    temp_dir = tempfile.gettempdir()
    temp_pdf = os.path.join(temp_dir, 'historico.pdf')
    pdf.output(temp_pdf)
    return temp_pdf

@app.route('/generar_pdf', methods=['POST'])
def generar_pdf_route():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos no válidos'}), 400
            
        tipo = data.get('tipo', 'apuesta')
        pdf_path = None
        
        try:
            if tipo == 'apuesta':
                # Validar que todos los campos necesarios estén presentes
                required_fields = ['numero', 'modalidad', 'valor_apuesta', 'loteria']
                if not all(field in data for field in required_fields):
                    return jsonify({'error': 'Faltan campos requeridos'}), 400
                    
                pdf_path = generar_pdf_apuesta(
                    data['numero'],
                    data['modalidad'],
                    data['valor_apuesta'],
                    data['loteria']
                )
                download_name = 'apuesta.pdf'
            else:
                pdf_path = generar_pdf_historico()
                download_name = 'historico.pdf'
            
            response = send_file(pdf_path, as_attachment=True, download_name=download_name)
            
            # Agregar callback para eliminar el archivo temporal después de enviarlo
            @response.call_on_close
            def cleanup():
                try:
                    if pdf_path and os.path.exists(pdf_path):
                        os.remove(pdf_path)
                except Exception:
                    pass  # Ignorar errores al limpiar
                    
            return response
            
        except Exception as e:
            if pdf_path and os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                except:
                    pass
            raise  # Re-lanzar la excepción para el manejo global
            
    except Exception as e:
        return jsonify({'error': 'Error al generar el PDF'}), 500

@app.route('/jugar', methods=['POST'])
def jugar():
    try:
        numero_jugado = request.form.get('numero')
        modalidad = int(request.form.get('modalidad'))
        valor_apuesta = int(request.form.get('valor'))
        loteria = request.form.get('loteria')
        
        # Validar que todos los campos estén presentes
        if not all([numero_jugado, modalidad, valor_apuesta, loteria]):
            return jsonify({'error': 'Todos los campos son requeridos'}), 400
            
        # Validar que la lotería exista
        if loteria not in loterias:
            return jsonify({'error': 'Lotería no válida'}), 400
        
        # Validar modalidad
        if modalidad not in [1, 2, 3, 4]:
            return jsonify({'error': 'Modalidad no válida'}), 400
        
        # Validar valor de apuesta
        if valor_apuesta < 1000 or valor_apuesta > 10000 or valor_apuesta % 1000 != 0:
            return jsonify({
                'error': 'El valor de la apuesta debe ser múltiplo de $1000 y estar entre $1000 y $10000'
            }), 400
        
        # Validar número según modalidad
        try:
            if not numero_jugado.isdigit():
                return jsonify({'error': 'El número debe contener solo dígitos'}), 400
                
            numero_jugado = int(numero_jugado)
            rangos = {
                4: (1000, 9999, 'Para 4 cifras, el número debe estar entre 1000 y 9999'),
                3: (100, 999, 'Para 3 cifras, el número debe estar entre 100 y 999'),
                2: (10, 99, 'Para 2 cifras, el número debe estar entre 10 y 99'),
                1: (0, 9, 'Para 1 cifra, el número debe estar entre 0 y 9')
            }
            
            min_num, max_num, mensaje = rangos[modalidad]
            if not (min_num <= numero_jugado <= max_num):
                return jsonify({'error': mensaje}), 400
        except ValueError:
            return jsonify({'error': 'Número no válido'}), 400
        
        # Generar número ganador
        if modalidad == 4:
            min_num, max_num = 1000, 9999
        elif modalidad == 3:
            min_num, max_num = 100, 999
        elif modalidad == 2:
            min_num, max_num = 10, 99
        else:
            min_num, max_num = 0, 9
        
        numero_ganador = random.randint(min_num, max_num)
        
        # Guardar en historial
        historial_ganadores.append({
            'fecha': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'loteria': loterias[loteria]['nombre'],
            'numero': numero_ganador
        })
        
        # Verificar si ganó y calcular premio
        mensaje = ''
        if numero_jugado == numero_ganador:
            try:
                # Calcular premio según la modalidad
                multiplicadores = {
                    1: 300,  # Para 1 cifra: 300 por cada peso
                    2: 400,  # Para 2 cifras: 400 por cada peso
                    3: 1000,  # Para 3 cifras: 1000 por cada peso
                    4: 5000   # Para 4 cifras: 5000 por cada peso
                }
                multiplicador = multiplicadores[modalidad]
                premio = valor_apuesta * multiplicador
                mensaje = f'¡Felicitaciones! Has ganado ${premio:,.2f}'
            except Exception as e:
                return jsonify({'error': 'Error al calcular el premio'}), 500
        else:
            mensaje = 'Apuesta generada con éxito ✔️'
        
        return jsonify({
            'ganador': numero_ganador,
            'mensaje': mensaje
        })
        
    except Exception as e:
        return jsonify({'error': 'Error en el servidor'}), 500
    
if __name__ == '__main__':
    app.run(debug=True)