from flask import Flask, request, render_template, jsonify
import cv2
import numpy as np
import os

app = Flask(__name__)

# Fungsi untuk mengompres gambar
def compress_image(image, max_size=(800, 800)):
    h, w = image.shape[:2]
    ratio = min(max_size[0]/w, max_size[1]/h)
    new_size = (int(w*ratio), int(h*ratio))
    return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)

# Fungsi transformasi gambar
def transform_image(image, transform_type, **kwargs):
    if transform_type == 'translasi':
        dx, dy = kwargs.get('dx', 0), kwargs.get('dy', 0)
        matriks_translasi = np.float32([[1, 0, dx], [0, 1, dy]])
        return cv2.warpAffine(image, matriks_translasi, (image.shape[1], image.shape[0]))
    
    elif transform_type == 'rotasi':
        sudut = kwargs.get('sudut', 0)
        tengah = (image.shape[1] // 2, image.shape[0] // 2)
        matriks_rotasi = cv2.getRotationMatrix2D(tengah, sudut, 1.0)
        return cv2.warpAffine(image, matriks_rotasi, (image.shape[1], image.shape[0]))
    
    elif transform_type == 'skala':
        skala_x, skala_y = kwargs.get('skala_x', 1.0), kwargs.get('skala_y', 1.0)
        return cv2.resize(image, None, fx=skala_x, fy=skala_y, interpolation=cv2.INTER_LINEAR)
    
    elif transform_type == 'distorsi':
        h, w = image.shape[:2]
        skew_x, skew_y = kwargs.get('skew_x', 0), kwargs.get('skew_y', 0)
        pts1 = np.float32([[0,0], [w-1,0], [0,h-1], [w-1,h-1]])
        pts2 = np.float32([[0,0], 
                           [w-1,0], 
                           [skew_x*w,h-1], 
                           [(1+skew_y)*w-1,h-1]])
        matriks_distorsi = cv2.getPerspectiveTransform(pts1, pts2)
        return cv2.warpPerspective(image, matriks_distorsi, (w, h))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    transform_type = request.form['transform_type']
    
    # Baca dan kompres gambar
    file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
    gambar_asli = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    gambar_asli = compress_image(gambar_asli)

    # Transformasi gambar
    if transform_type == 'translasi':
        dx = int(request.form['dx'])
        dy = int(request.form['dy'])
        gambar_transformasi = transform_image(gambar_asli, 'translasi', dx=dx, dy=dy)
    elif transform_type == 'rotasi':
        sudut = int(request.form['sudut'])
        gambar_transformasi = transform_image(gambar_asli, 'rotasi', sudut=sudut)
    elif transform_type == 'skala':
        skala_x = float(request.form['skala_x'])
        skala_y = float(request.form['skala_y'])
        gambar_transformasi = transform_image(gambar_asli, 'skala', skala_x=skala_x, skala_y=skala_y)
    elif transform_type == 'distorsi':
        skew_x = float(request.form['skew_x'])
        skew_y = float(request.form['skew_y'])
        gambar_transformasi = transform_image(gambar_asli, 'distorsi', skew_x=skew_x, skew_y=skew_y)

    # Simpan gambar hasil transformasi ke dalam buffer
    _, buffer = cv2.imencode('.png', gambar_transformasi)
    img_str = base64.b64encode(buffer).decode('utf-8')

    return jsonify({"transformed_image": img_str})

if __name__ == '__main__':
    app.run(debug=True)