from qr import *
from io import BytesIO
import base64
import os
from flask import Flask, request, render_template, flash, url_for

app = Flask("QR Generator")
app.config.update(
    SECRET_KEY=os.urandom(1239),
    SERVER_NAME="qr.hadiobeid.tr",
    SESSION_COOKIE_NAME="qr.hadiobeid.tr",
    SESSION_COOKIE_SAMESITE="None",
    SESSION_COOKIE_SECURE=True
)

QR_MODULE_WIDTH = 5
QR_QUIET_ZONE = 5
QR_IMG_WIDTH = lambda version: QR_MODULE_WIDTH * ((17 + (QR_QUIET_ZONE * 2)) + (version * 4))

@app.route('/', methods= ["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template('index.html')
    if request.method == "POST":
        msg, version, ecc, = (request.form["message"], request.form["version"], request.form["ecc"])
        if version == '-1':
            for i in range(1, 41):
                if len(msg) <= char_capacity[(i, ecc, QREncoding.BYTE)]:
                    break
            version = i
        else:
            version = int(version)
        
        try:
            qr = QRCode(QREncoding.BYTE, ecc, int(version), msg)
            qr_img = Image.new("L", (QR_IMG_WIDTH(int(version)), QR_IMG_WIDTH(int(version))), color = 255)
            img_writer = ImageDraw.Draw(qr_img)
            code = qr.qr_code
            for y, row in enumerate(code):
                for x, bit in enumerate(row):
                    y_pos = (y + QR_QUIET_ZONE) * QR_MODULE_WIDTH
                    x_pos = (x + QR_QUIET_ZONE) * QR_MODULE_WIDTH
                    color = 255 if bit == "0" else 0
                    img_writer.rectangle([(x_pos, y_pos), (x_pos + QR_MODULE_WIDTH, y_pos + QR_MODULE_WIDTH)], fill = color)
            img_file = BytesIO()
            qr_img.save(img_file, format="PNG")
            qr_bytes = img_file.getvalue()
            qr_encoded = f"data:image/png;base64,{base64.b64encode(qr_bytes).decode('utf-8')}"
            #qr_img.show()
            #img_code = Reader(bytes=img)

            return render_template('gen_qr.html', img = qr_encoded)
        except ValueError:
            flash("Message exceeds code capacity!")
        except KeyError:
            flash("Invalid symbols in message!")
        return render_template('index.html')


        #print(char_capacity[(version, "L", QREncoding.BYTE)])

if __name__ == '__main__':
    app.run()
