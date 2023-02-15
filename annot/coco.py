from typing import Optional
from dataclasses import dataclass

# coco format info: https://medium.com/mlearning-ai/coco-dataset-what-is-it-and-how-can-we-use-it-e34a5b0c6ecd


@dataclass
class COCO_License:
    id: int
    url: str
    name: str


@dataclass
class COCO_Info:
    year: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    date_created: Optional[str] = None
    contributor: Optional[str] = None
    url: Optional[str] = None


@dataclass
class COCO_Category:
    id: int
    name: str
    supercategory: Optional[str] = None


@dataclass
class COCO_Image:
    id: int
    file_name: str
    height: int
    width: int
    date_created: Optional[str] = None
    license: Optional[str] = None
    flickr_url: Optional[str] = None
    coco_url: Optional[str] = None
    date_captured: Optional[str] = None
