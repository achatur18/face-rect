import unittest
import sys
import os
import cv2

# Add the parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
parent_dir = os.path.dirname(parent_dir)
sys.path.append(parent_dir)

# Now you can import face_rect
import src.face_rect as face_rect


class TestFaceRec(unittest.TestCase):
    fr = face_rect.FaceRec()
    face_img_path = os.path.join(current_dir, "test.jpeg")

    def test_get_faces(self):
        resp=self.fr.get_faces(self.face_img_path)
        self.assertEqual(len(resp[0]), 1)
        self.assertEqual(len(resp[1]), 1)

    def test_get_embeddings(self):
        emb = self.fr.get_embeddings(self.face_img_path)
        self.assertEqual(len(emb), 1)

    def test_get_embeddings_withcv2(self):
        img=cv2.imread(self.face_img_path)
        emb = self.fr.get_embeddings(img)
        self.assertEqual(len(emb), 1)
    
    def test_yield_embeddings(self):
        img=cv2.imread(self.face_img_path)
        for face_embedding in self.fr.yield_embeddings(img):
            self.assertEqual(len(face_embedding["embedding"]), 512)

    def test_load_config(self):
        from src.config import load_config
        config=load_config()
        self.assertNotEqual(len(config.keys()), 0)


if __name__ == '__main__':
    unittest.main()
