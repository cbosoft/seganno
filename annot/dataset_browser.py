import os
from typing import List, Optional, Dict
import json
from datetime import datetime

from tqdm import tqdm

from PySide6.QtWidgets import QWidget, QGroupBox, QTableWidget, QTableWidgetItem, QScrollArea, QFileDialog, QPushButton, QHBoxLayout, QVBoxLayout, QHeaderView
from PySide6.QtGui import QImage
from PySide6.QtCore import Qt

from .coco import COCO_Category, COCO_Info, COCO_Image, COCO_License
from .annotation import Annotation
from .class_labels import CLASSES


class DatasetBrowser(QGroupBox):

    IMAGE_EXTENSIONS = {'.bmp', '.jpg', '.jpeg', '.tif', '.tiff', '.png'}

    def __init__(self, app):
        super().__init__('Dataset')
        self.app = app
        self.info = COCO_Info(
            year=datetime.now().strftime('%Y'),
            description=f'Created with MDPC App <> Annnotation Tool',
            date_created=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        self.licenses: List[COCO_License] = []
        self.images: List[COCO_Image] = []
        self.image_annotations: Dict[int, List[Annotation]] = []
        self.categories: List[COCO_Category] = [
            COCO_Category(id=i, name=name)
            for i, name in enumerate(CLASSES, start=1)
        ]
        self.dname: Optional[str] = None

        self.layout = QVBoxLayout(self)
        button_box = QWidget()
        self.layout.addWidget(button_box)
        self.btn_open = QPushButton('Open')
        self.btn_open.clicked.connect(self.open_dataset)
        self.btn_save = QPushButton('Save')
        self.btn_save.clicked.connect(self.save)
        button_box.layout = QHBoxLayout(button_box)
        button_box.layout.addWidget(self.btn_open)
        button_box.layout.addWidget(self.btn_save)

        scroll = QScrollArea()
        self.layout.addWidget(scroll)
        scroll.layout = QVBoxLayout(scroll)
        self.dataset_table = QTableWidget()
        cols = ['Mark', '#Ann', 'Filename']
        self.dataset_table.setColumnCount(len(cols))
        self.dataset_table.setHorizontalHeaderLabels(cols)
        header = self.dataset_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        scroll.layout.addWidget(self.dataset_table)
        self.dataset_table.itemSelectionChanged.connect(self.selected_image_changed)

    def open_dataset(self):
        dn = QFileDialog.getExistingDirectory(
            self, 'Open a directory of images',
            '.'
        )
        if dn:
            self.open_folder(dn)

    def open_folder(self, dn: str):
        self.dname = dn
        self.droot = os.path.dirname(dn)
        if os.path.exists(dn+'.json'):
            self.load_from_coco_json(dn+'.json')
        else:
            self.images = []
            self.image_annotations = {}
            image_fns = []
            for root, _, files in os.walk(dn):
                print(root)
                for file in files:
                    _, ext = os.path.splitext(file)
                    if ext.lower() in self.IMAGE_EXTENSIONS:
                        image_fn = os.path.join(root, file)
                        image_fns.append(image_fn)

            for image_fn in tqdm(image_fns):
                image = QImage(image_fn)
                if image.isNull():
                    continue
                image_fn = os.path.relpath(image_fn, self.droot)
                coco_image = COCO_Image(len(self.images), image_fn, width=image.width(), height=image.height())
                self.images.append(coco_image)
                self.image_annotations[coco_image.id] = []
        self.refresh_list()

    def load_from_coco_json(self, path: str):
        with open(path) as f:
            data = json.load(f)
        self.info = COCO_Info(**data['info'])
        self.licenses = [COCO_License(**lkw) for lkw in data['licenses']]
        self.images = [COCO_Image(**imkw) for imkw in data['images']]
        images_by_id = {im.id: im for im in self.images}
        self.image_annotations = {im.id: list() for im in self.images}
        annots = [Annotation.from_coco(images_by_id, **ankw) for ankw in data['annotations']]
        for annot in annots:
            im = images_by_id[annot.im_id]
            self.image_annotations[im.id].append(annot)
        self.categories = [COCO_Category(**ckw) for ckw in data['categories']]

        print(f'Loaded DS with {len(self.images)} images and {len(annots)} annotations.')

    def as_coco_dict(self):
        images = []
        annots = []
        for im in self.images:
            images.append(im.__dict__)
            for annot in self.image_annotations[im.id]:
                adict = annot.as_coco_annot()
                adict['id'] = len(annots)
                adict['image_id'] = im.id
                annots.append(adict)
        print(f'saved ds of {len(images)} images and {len(annots)} annotations.')
        return dict(
            info=self.info.__dict__,
            images=images,
            annotations=annots,
            licenses=[lic.__dict__ for lic in self.licenses],
            categories=[cat.__dict__ for cat in self.categories]
        )

    def save(self):
        output_path = self.dname + '.json'
        data = self.as_coco_dict()
        self.save_dataset(output_path, data)

    @staticmethod
    def save_dataset(filename, dataset):
        with open(filename, 'w') as f:
            json.dump(dataset, f, indent=2)

    def refresh_list(self):
        self.dataset_table.setRowCount(len(self.images))
        for r, image in enumerate(self.images):
            twi = QTableWidgetItem()
            twi.setCheckState(Qt.CheckState.Unchecked)
            self.dataset_table.setItem(r, 0, twi)
            n_annots = len(self.image_annotations[image.id])
            self.dataset_table.setItem(r, 1, QTableWidgetItem(f'{n_annots}'))
            self.dataset_table.setItem(r, 2, QTableWidgetItem(image.file_name))

    def selected_image_changed(self):
        index = self.dataset_table.selectedRanges()[0].topRow()
        imname = os.path.join(self.droot, self.images[index].file_name)
        im_id = self.images[index].id
        self.app.set_image(imname, self.images[index].id, self.image_annotations[im_id])
        self.app.particle_browser.refresh_table()
