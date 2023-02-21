import numpy as np
import torch
from torchvision.models import resnet18, ResNet18_Weights
import cv2

from PySide6.QtWidgets import QComboBox

from ..base import Augmentation


class ResNetFeatDet(Augmentation):

    def __init__(self):
        super().__init__('ResNet (ImageNet)')
        self.model = resnet18(weights=ResNet18_Weights.DEFAULT)
        self.model.eval()
        self.w = None

    def apply_to_image(self, image: np.ndarray):
        image[:] = self.inference(image, self.w.currentIndex())

    def inference(self, image: np.ndarray, level: int):

        if not level:
            return image

        h, w = image.shape
        if len(image.shape) < 3:
            image = np.stack([image, image, image], -1)

        x = torch.tensor(image.astype(float) / 255.).permute(2, 0, 1).float().unsqueeze(0)
        with torch.no_grad():
            x = self.model.conv1(x)
            x = self.model.bn1(x)
            x = self.model.relu(x)
            x = self.model.maxpool(x)

            x = self.model.layer1(x)

            if level >= 2:
                x = self.model.layer2(x)

                if level >= 3:
                    x = self.model.layer3(x)

                    if level >= 4:
                        x = self.model.layer4(x)

            x = torch.mean(x, 1)
            x = (np.array(x[0]) * 255.).astype(np.uint8)
        return cv2.resize(x, (w, h))

    def widget(self, update_f):
        self.w = QComboBox()
        self.w.addItems([str(i) for i in range(5)])
        self.w.setCurrentIndex(0)
        self.w.currentIndexChanged.connect(update_f)
        return self.w

    def reset(self):
        self.w.setCurrentIndex(0)
