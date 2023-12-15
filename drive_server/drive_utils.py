import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

FOLDER_NAME = "IOT_Monitor"

class DriveUtils:
    def __init__(self, drive_folder_name, local_dir=None):
        gauth = GoogleAuth()
        self.drive = GoogleDrive(gauth)

        self.drive_folder_name = drive_folder_name
        self.local_dir = local_dir
        self.drive_folder_id = self.get_folder_id(drive_folder_name)
        assert self.drive_folder_id is not None

    def get_folder_id(self, folder_name):
        file_list = self.drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
        for file in file_list:
            if file["title"] == FOLDER_NAME:
                folder_id = file["id"]
                return folder_id
        return None

    def upload_image_to_drive(self, img_path):
        filename = img_path.split("/")[-1]
        metadata = {
            "parents": [{"id": self.drive_folder_id}],
            "title": filename,
            "mimeType": "image/png",
        }
        file = self.drive.CreateFile(metadata)
        if self.local_dir is not None:
            img_path = os.path.join(self.local_dir, filename)
        file.SetContentFile(img_path)
        file.Upload()
        print(f"Uploaded {img_path} to drive")

    def upload_images_in_folder(self, imgs_dir):
        dir_list = os.listdir(imgs_dir)
        for img in dir_list:
            if not img.endswith("png"):
                continue
            img_path = os.path.join(imgs_dir, img)
            self.upload_image_to_drive(img_path)

if __name__ == "__main__":
    drive_utils = DriveUtils(FOLDER_NAME)
    drive_utils.upload_images_in_folder("/Users/wanlin/Desktop/camera_images")

