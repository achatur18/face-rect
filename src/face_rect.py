from src.extras import facerect_get_image, get_default_provider_options, get_any_model, ArcFaceONNX, Face
from src.model_zoo import PickableInferenceSession
import os
from src.config import load_config
from loguru import logger


current_dir = os.path.dirname(os.path.realpath(__file__))
logger.info(f"current_dir: {current_dir}")
config = load_config(current_dir)
model_loc = os.path.join(current_dir, config["model"]["folder_name"])


class FaceRec:
    def __init__(self) -> None:
        kwargs={
            "provider_options" : get_default_provider_options()
        }

        self.retinaface_onnx_file=os.path.join(model_loc, config["model"]["face_detection_model_name"])
        self.session = PickableInferenceSession(self.retinaface_onnx_file, **kwargs)
        self.retinaface=get_any_model(self.retinaface_onnx_file)

        self.arcface_onnx_file=os.path.join(model_loc, config["model"]["face_recognition_model_name"])
        self.arcface_session = PickableInferenceSession(self.arcface_onnx_file, **kwargs)
        self.arcface=ArcFaceONNX(model_file=self.arcface_onnx_file, session=self.arcface_session)

    def get_faces(self, image_loc):
        img = facerect_get_image(image_loc)
        bboxes, kpss = self.retinaface.detect(img,input_size=( 640, 640), max_num=0,metric='default')
        return bboxes, kpss

    def get_embeddings(self, image_loc):
        img = facerect_get_image(image_loc)
        bboxes, kpss = self.get_faces(image_loc)

        ret = []
        for i in range(bboxes.shape[0]):
            bbox = bboxes[i, 0:4]
            det_score = bboxes[i, 4]
            kps = None
            if kpss is not None:
                kps = kpss[i]
            face = Face(bbox=bbox, kps=kps, det_score=det_score)
            self.arcface.get(img, face)
            ret.append(face)
        return ret

    def yield_embeddings(self, image_loc):
        img = facerect_get_image(image_loc)
        bboxes, kpss = self.get_faces(image_loc)

        for i in range(bboxes.shape[0]):
            bbox = bboxes[i, 0:4]
            det_score = bboxes[i, 4]
            kps = None
            if kpss is not None:
                kps = kpss[i]
            face = Face(bbox=bbox, kps=kps, det_score=det_score)
            self.arcface.get(img, face)
            yield face
            