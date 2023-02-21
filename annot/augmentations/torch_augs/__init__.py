try:
    import torch
    import torchvision

    from .resnet_featdet import ResNetFeatDet

except ImportError:

    ResNetFeatDet = None
