import os
import time
from datetime import datetime

from drive_utils import DriveUtils
from email_utils import send_alert_email
from flask import Flask, request, jsonify

TIMESTAMP_FORMAT = "%m_%d_%Y_%H_%M_%S_%f"
IMAGE_DUMP_DIR = "/Users/wanlin/Desktop/camera_images"

app = Flask(__name__)
drive_utils = DriveUtils("IOT_Monitor", IMAGE_DUMP_DIR)

@app.route("/upload", methods=["POST"])
def upload_file():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    datetime_str = data.get("datetime")
    if not datetime_str:
        return jsonify({'error': 'Missing required parameters'}), 400

    datetime_obj = datetime.strptime(datetime_str, TIMESTAMP_FORMAT)
    images = os.listdir(IMAGE_DUMP_DIR)

    images_to_upload = []
    for img in images:
        if not img.endswith("png"):
            continue
        t_str = img.split(".")[0]
        t_obj = datetime.strptime(t_str, TIMESTAMP_FORMAT)
        if t_obj >= datetime_obj:
            images_to_upload.append(img)

    uploaded_files = []
    for f in images_to_upload:
        drive_utils.upload_image_to_drive(f)
        uploaded_files.append(f)

    send_alert_email()

    result = {"message": f"Uploaded {','.join(uploaded_files)}"}
    return jsonify(result)

@app.route("/test", methods=["POST"])
def test():
    data = request.json
    print(data)
    time.sleep(3)
    result = {"message": "done"}
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
