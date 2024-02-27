
import os
import os.path as osp
import glob
import onnxruntime
from .arcface_onnx import *
from .retinaface import *
from .landmark import *

__all__ = ['get_model']


class PickableInferenceSession(onnxruntime.InferenceSession): 
    # This is a wrapper to make the current InferenceSession class pickable.
    def __init__(self, model_path, **kwargs):
        super().__init__(model_path, **kwargs)
        self.model_path = model_path

    def __getstate__(self):
        return {'model_path': self.model_path}

    def __setstate__(self, values):
        model_path = values['model_path']
        self.__init__(model_path)

class ModelRouter:
    def __init__(self, onnx_file):
        self.onnx_file = onnx_file

    def get_model(self, **kwargs):
        session = PickableInferenceSession(self.onnx_file, **kwargs)
        print('Applied providers: {session._providers}, with options: {session._provider_options}')
        inputs = session.get_inputs()
        input_cfg = inputs[0]
        input_shape = input_cfg.shape
        outputs = session.get_outputs()

        if len(outputs)>=5:
            return RetinaFace(model_file=self.onnx_file, session=session)
        elif input_shape[2]==192 and input_shape[3]==192:
            return Landmark(model_file=self.onnx_file, session=session)
        # elif input_shape[2]==96 and input_shape[3]==96:
        #     return Attribute(model_file=self.onnx_file, session=session)
        # elif len(inputs)==2 and input_shape[2]==128 and input_shape[3]==128:
        #     return INSwapper(model_file=self.onnx_file, session=session)
        elif input_shape[2]==input_shape[3] and input_shape[2]>=112 and input_shape[2]%16==0:
            return ArcFaceONNX(model_file=self.onnx_file, session=session)
        else:
            #raise RuntimeError('error on model routing')
            return None
