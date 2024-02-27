from time import time
import os
import boto3
from .storage_base import StorageBase
from botocore.exceptions import NoCredentialsError
from loguru import logger
from starlette.datastructures import UploadFile
import shutil

class S3Storage(StorageBase):
    def __init__(self, config) -> None:
        super().__init__(config)
        self.bucketName = os.getenv("BUCKET_NAME", "facerect")
        self.uploadFolderName = os.getenv("FOLDER_NAME", "uploaded_images")
        self.upload_img_path = os.path.join(self.bucketName, self.uploadFolderName)
        self.s3 = boto3.client('s3')

    async def upload_file_to_s3(self, upload_file: UploadFile, event_id: str):
        """
        Uploads a file to an AWS S3 bucket.

        :param upload_file: The file to upload, as a Starlette UploadFile object.
        :param bucket_name: The name of the bucket to upload to.
        :param object_name: The S3 object name. If not specified, the file's name will be used.
        :return: True if file was uploaded, else False.
        """
        try:
            object_name = os.path.join(self.upload_img_path, event_id, upload_file.filename.split("/")[-1])
            # Convert the UploadFile to bytes
            file_content = await upload_file.read()
            
            # Upload the file
            self.s3.put_object(Body=file_content, Bucket=self.bucketName, Key=object_name)
            logger.info(f"object_name, {object_name}")
            
            return object_name
        except NoCredentialsError:
            print("Credentials not available")
            return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    def folder_exists(self, folder_path, bucket_name=None):
        """
        Check if a folder exists in an S3 bucket.

        :param bucket_name: Name of the S3 bucket.
        :param folder_path: The path to the folder (should end with a slash).
        :return: True if the folder exists, False otherwise.
        """
        if not bucket_name:
            bucket_name = self.bucketName

        # Ensure the folder path ends with a slash
        if not folder_path.endswith('/'):
            folder_path += '/'
        
        s3_client = boto3.client('s3')
        
        # List objects within the specified folder path
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_path, Delimiter='/')
        
        # Check if any objects were returned
        return 'Contents' in response or 'CommonPrefixes' in response


    def create_folder(self, directory_path, bucket_name=None):
        if self.folder_exists(directory_path):
            return
        
        if not bucket_name:
            bucket_name = self.bucketName

        self.s3.put_object(Bucket=bucket_name, Key=directory_path)

    async def save_image_to_storage(self, config, files):
        uploaded_images = []
        for file in files:
            # file_path = os.path.join(DIRECTORY, f"{int(time()*10**7)}_{file.filename}")
            response = await self.upload_file_to_s3(file, config["event_id"])
            if response:
                uploaded_images.append(response)
                logger.info(f"file {file.filename} uploaded successfully.")
            else:
                logger.info(f"file {file.filename} did not uploaded.")
        return uploaded_images


    def upload_image(self, file_path, config: str, object_name=None):
        """Upload an image to an S3 bucket

        :param file_path: File path to the image to upload
        :param object_name: S3 object name. If not specified, file_path is used
        :return: True if file was uploaded, else False
        """
        if object_name is None:
            object_name = os.path.join(self.uploadFolderName, config["event_id"], file_path.split("/")[-1])

        try:
            self.s3.upload_file(file_path, self.bucketName, object_name)
            print(f"'{file_path}' has been uploaded to '{self.bucketName}/{object_name}'")
            return object_name
        except NoCredentialsError:
            print("Credentials not available")
            return False
        
    def save_image_to_local(self, config, files):
        DIRECTORY = os.path.join(self.upload_img_path, config["event_id"])
        os.makedirs(DIRECTORY, exist_ok=True)

        uploaded_images = []
        for file in files:
            file_path = os.path.join(DIRECTORY, f"{int(time()*10**7)}_{file.filename}")
            uploaded_images.append(file_path)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        return uploaded_images

    def delete_images_from_local(self, image_paths):
        """
        Deletes specified images from local storage.

        :param image_paths: List of full paths to the images to be deleted.
        :return: A list of statuses indicating whether each image was successfully deleted or not.
        """
        delete_statuses = []
        for image_path in image_paths:
            try:
                if os.path.isfile(image_path):
                    os.remove(image_path)
                    delete_statuses.append((image_path, True))
                else:
                    # If the path does not exist or is not a file, consider it a failed deletion.
                    delete_statuses.append((image_path, False))
            except Exception as e:
                # Catch any unexpected errors during deletion.
                print(f"Error deleting {image_path}: {e}")
                delete_statuses.append((image_path, False))
        
        return delete_statuses


    def download_image(self, object_name, file_path):
        """Download an image from an S3 bucket

        :param object_name: S3 object name
        :param file_path: File path where the image will be saved
        :return: True if file was downloaded, else False
        """
        try:
            self.s3.download_file(self.bucketName, object_name, file_path)
            print(f"'{self.bucketName}/{object_name}' has been downloaded to '{file_path}'")
            return True
        except NoCredentialsError:
            print("Credentials not available")
            return False
        
    def get_image_download_link(self, object_name, expiration=30):
        """Generate a presigned URL to download an image from an S3 bucket.

        :param object_name: S3 object name
        :param expiration: Time in seconds for the presigned URL to remain valid
        :return: Presigned URL as a string. If error, returns None.
        """
        try:
            response = self.s3.generate_presigned_url('get_object',
                                                      Params={'Bucket': self.bucketName,
                                                              'Key': object_name},
                                                      ExpiresIn=expiration)
            return response
        except NoCredentialsError:
            print("Credentials not available")
            return None
