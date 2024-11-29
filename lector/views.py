'''from django.shortcuts import render
from pyzbar.pyzbar import decode
from PIL import Image
from .forms import BarcodeForm

def barcode_reader(request):
    result = None
    if request.method == 'POST':
        form = BarcodeForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            # Procesar la imagen
            pil_image = Image.open(image)
            decoded_objects = decode(pil_image)
            if decoded_objects:
                result = decoded_objects[0].data.decode('utf-8')
            else:
                result = "No se pudo leer el código de barras."
    else:
        form = BarcodeForm()

    return render(request, 'lector/barcode_reader.html', {'form': form, 'result': result})'''

from django.shortcuts import render
from django.http import JsonResponse
from pyzbar.pyzbar import decode
from PIL import Image
import base64
from io import BytesIO
import threading
import psycopg2
import datetime

def camera_reader(request):
    if request.method == 'POST':
        # Obtener la imagen en base64 desde la solicitud POST
        image_data = request.POST.get('image')
        if image_data:
            # Decodificar la imagen
            image_data = base64.b64decode(image_data.split(',')[1])  # Eliminar la cabecera del base64
            image = Image.open(BytesIO(image_data))
            decoded_objects = decode(image)
            if decoded_objects:
                result = decoded_objects[0].data.decode('utf-8')
                guardar_codigo(result)
                return JsonResponse({'success': True, 'barcode': result})
            else:
                return JsonResponse({'success': False, 'message': 'No se pudo leer el código de barras.'})
    return render(request, 'lector/camera_reader.html')

def get_db_connection():
    conn = psycopg2.connect(**{
    "host": "localhost",
    "port": 5432,
    "database": "darksus",
    "user": "darksus",
    "password": ""
})
    return conn

def guardar_codigo(*codigo):
    thread = threading.Thread(target=insertar_codigo, args=codigo)
    thread.start()

def insertar_codigo(*codigo):   
    print(codigo) 
    conn = get_db_connection()
    cursor = conn.cursor()

    queryIfExist = "SELECT EXISTS (SELECT 1 FROM barcodes WHERE barcode = %s)"
    cursor.execute(queryIfExist, (codigo)) 
    #print( bool(cursor.fetchone()[0]) )

    if bool(cursor.fetchone()[0]):
        print(f"Código {codigo} existente.")
        cursor.close()
        conn.close()
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO barcodes (barcode, registered_at) VALUES (%s, %s)"
        
        try:
            cursor.execute(query, (codigo, datetime.datetime.now()))
            conn.commit()
            print(f"Código {codigo} guardado correctamente.")
        except Exception as e:
            print(f"Error al guardar el código: {e}")
        finally:
            cursor.close()
            conn.close()
