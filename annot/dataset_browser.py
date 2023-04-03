import os
from typing import List, Optional, Dict
import json
from datetime import datetime
import shutil

from tqdm import tqdm

from PySide6.QtWidgets import QWidget, QGroupBox, QTableWidget, QTableWidgetItem, QScrollArea, QFileDialog, QPushButton, QHBoxLayout, QVBoxLayout, QHeaderView, QMessageBox, QCheckBox
from PySide6.QtGui import QImage
from PySide6.QtCore import Qt

from .coco import COCO_Category, COCO_Info, COCO_Image, COCO_License
from .annotation import Annotation
from .class_labels import CLASSES


class DatasetBrowser(QGroupBox):

    IMAGE_EXTENSIONS = {'.bmp', '.jpg', '.jpeg', '.tif', '.tiff', '.png'}

    def __init__(self, app):
        super().__init__('Dataset')
        self.previous_dir = '.'
        self.app = app
        self.info = self.default_info()
        self.licenses: List[COCO_License] = []
        self.images: List[COCO_Image] = []
        self.image_annotations: Dict[int, List[Annotation]] = []
        self.categories: List[COCO_Category] = self.default_categories()
        self.dname: Optional[str] = None

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        open_button_box = QWidget()
        open_button_box.layout = QHBoxLayout(open_button_box)
        open_button_box.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(open_button_box)
        self.btn_open = QPushButton('Open')
        self.btn_open.setToolTip('Open a dataset, replacing current.')
        self.btn_open.clicked.connect(self.open_dataset)
        self.btn_open_and_merge = QPushButton('Open and Merge')
        self.btn_open_and_merge.setToolTip('Open a dataset, merging into current. Images not present in the current dataset are added. Annotations on each image are added, not replaced.')
        self.btn_open_and_merge.clicked.connect(self.merge_dataset)
        self.btn_open_and_merge.setEnabled(False)
        open_button_box.layout.addWidget(self.btn_open)
        open_button_box.layout.addWidget(self.btn_open_and_merge)

        save_button_box = QWidget()
        self.layout.addWidget(save_button_box)
        save_button_box.layout = QHBoxLayout(save_button_box)
        save_button_box.layout.setContentsMargins(0, 0, 0, 0)
        self.btn_save = QPushButton('Save')
        self.btn_save.setToolTip('Save current dataset.')
        self.btn_save.clicked.connect(self.save)

        self.btn_save_marked = QPushButton('Save Marked')
        self.btn_save_marked.setToolTip('Save selected images as new dataset.')
        self.btn_save_marked.clicked.connect(self.save_marked)
        self.btn_save_marked.setEnabled(False)
        save_button_box.layout.addWidget(self.btn_save)
        save_button_box.layout.addWidget(self.btn_save_marked)

        self.chk_review_mode = QCheckBox('Review mode?')
        self.chk_review_mode.setToolTip('Select to filter list of images down to those that have annotations already.')
        self.chk_review_mode.clicked.connect(self.refresh_list)
        self.layout.addWidget(self.chk_review_mode)

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
        self.dataset_table.cellClicked.connect(self.datatable_row_clicked)
        self.dataset_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

    def open_dataset(self):
        dn = QFileDialog.getExistingDirectory(
            self, 'Open a directory of images',
            self.previous_dir,
        )
        if dn:
            self.open_folder(dn)
    
    def merge_dataset(self):
        dn, _ = QFileDialog.getOpenFileName(
            self, 'Open and merge existing dataset into current dataset',
            self.previous_dir,
            '*.json'
        )
        if dn:
            self.merge_json(dn)

    def open_folder(self, dn: str):
        self.dname = dn
        self.droot = os.path.dirname(dn)
        self.previous_dir = self.droot
        if os.path.exists(dn+'.json'):
            self.info, self.licenses, self.images, annots, self.image_annotations, self.categories = \
                self.load_coco_json(dn+'.json')
            print(f'Loaded DS with {len(self.images)} images and {len(annots)} annotations.')
        else:
            self.info, self.licenses, self.images, self.image_annotations, self.categories = \
                self.load_dir(dn, self.droot)
            print(f'Created new DS from {len(self.images)} images.')
        self.refresh_list()
        self.app.set_info('dataset', os.path.basename(self.dname))
        self.btn_open_and_merge.setEnabled(True)

    def merge_json(self, json_path: str):
        self.previous_dir = self.droot
        _, _, images, annots, image_annotations, categories = \
            self.load_coco_json(json_path)
        n_new_annots = len(annots)
        
        # assert categories == self.categories, \
        #     f'Cannot merge datasets with disparate categories "{categories}" (new) vs "{self.categories}" (current)'
        
        current_images_by_fn = {im.file_name: im for im in self.images}

        images_by_id = {im.id: im for im in images}
        image_annotations_by_fn = {
            images_by_id[im_id].file_name: a
            for im_id, a in image_annotations.items()
        }
        new_images = []
        for im in images:
            if im.file_name in current_images_by_fn:
                cim = current_images_by_fn[im.file_name]
                im.id = cim.id
            else:
                im.id = len(self.images) + len(new_images)
                new_images.append(im)
        
        for image in new_images:
            self.images.append(image)
        
        images_by_fn = {im.file_name: im for im in self.images}
        image_annotations = {
            images_by_fn[fn].id: a
            for fn, a in image_annotations_by_fn.items()
        }
        
        for im_id, annots in image_annotations.items():
            if im_id not in self.image_annotations:
                self.image_annotations[im_id] = []
            self.image_annotations[im_id].extend(annots)
        
        total_annots_count = sum(len(a) for a in self.image_annotations.values())
        print(f'Merged DS with {len(images)} images and {n_new_annots} annotations.')
        print(f'DS now has {len(self.images)} images and {total_annots_count} annotations.')
        self.refresh_list()
        self.app.set_info('dataset', os.path.basename(self.dname))

    @staticmethod
    def load_coco_json(path: str):
        with open(path) as f:
            data = json.load(f)
        info = COCO_Info(**data['info'])
        licenses = [COCO_License(**lkw) for lkw in data['licenses']]
        images = [COCO_Image(**imkw) for imkw in data['images']]
        for coco_image in images:
            coco_image.file_name = coco_image.file_name.replace('\\', '/')
        images_by_id = {im.id: im for im in images}
        image_annotations = {im.id: list() for im in images}
        annots = [Annotation.from_coco(images_by_id, **ankw) for ankw in data['annotations']]
        for annot in annots:
            im = images_by_id[annot.im_id]
            image_annotations[im.id].append(annot)
        categories = [COCO_Category(**ckw) for ckw in data['categories']]
        return info, licenses, images, annots, image_annotations, categories
    
    @staticmethod
    def default_info():
        return COCO_Info(
            year=datetime.now().strftime('%Y'),
            description=f'Created with MDPC App <> Annnotation Tool',
            date_created=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
    
    @staticmethod
    def default_categories():
        return [
            COCO_Category(id=i, name=name)
            for i, name in enumerate(CLASSES, start=1)
        ]
    
    @classmethod
    def load_dir(cls, path: str, droot: str):
        images = []
        image_annotations = {}
        image_fns = []
        for root, _, files in os.walk(path):
            for file in sorted(files):
                _, ext = os.path.splitext(file)
                if ext.lower() in cls.IMAGE_EXTENSIONS:
                    image_fn = os.path.join(root, file)
                    image_fns.append(image_fn)

        for image_fn in tqdm(image_fns):
            image = QImage(image_fn)
            if image.isNull():
                continue
            image_fn = os.path.relpath(image_fn, droot)
            coco_image = COCO_Image(len(images), image_fn, width=image.width(), height=image.height())
            coco_image.file_name = coco_image.file_name.replace('\\', '/')
            images.append(coco_image)
            image_annotations[coco_image.id] = []
        
        return cls.default_info(), [], images, image_annotations, cls.default_categories()


    def as_coco_dict(self, include_unmarked=True):
        images = []
        annots = []
        for im in self.images:
            if include_unmarked or im.marked:
                im_dict = {k: v for k, v in im.__dict__.items() if k not in {'marked'}}
                images.append(im_dict)
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
        mb = QMessageBox(self)
        mb.setText(f'Dataset saved:<br/>"{output_path}"')
        mb.show()
    
    def save_marked(self):
        if not any(im.marked for im in self.images):
            mb = QMessageBox(self)
            mb.setText('No marked images!')
            mb.show()
        else:
            fn, _ = QFileDialog.getSaveFileName(
                self,
                'Choose path to save marked images as new dataset.',
                self.previous_dir,
                '*.json'
            )
            if fn:
                new_droot = os.path.dirname(fn)
                self.save_dataset(fn, self.as_coco_dict(False))
                marked_images = [im for im in self.images if im.marked]
                for image in marked_images:
                    old_path = os.path.join(self.droot, image.file_name)
                    new_path = os.path.join(new_droot, image.file_name)
                    os.makedirs(os.path.dirname(new_path), exist_ok=True)
                    shutil.copy(old_path, new_path)
                mb = QMessageBox(self)
                mb.setText(f'Marked images saved as dataset:<br/>"{fn}"')
                mb.show()

    @staticmethod
    def save_dataset(filename, dataset):
        with open(filename, 'w') as f:
            json.dump(dataset, f, indent=2)
    
    def datatable_row_clicked(self, r, c):
        if c != 0:
            return
        
        twi = self.dataset_table.item(r, c)
        im = self.images[r]
        im.marked = twi.checkState() == Qt.CheckState.Checked

        self.btn_save_marked.setEnabled(any(im.marked for im in self.images))


    def refresh_list(self):
        if self.chk_review_mode.isChecked():
            images = [
                im for im in self.images if self.image_annotations[im.id]
            ]
        else:
            images = self.images
        self.dataset_table.setRowCount(0)
        self.dataset_table.setRowCount(len(images))
        for r, image in enumerate(tqdm(images)):
            twi = QTableWidgetItem()
            twi.setCheckState(Qt.CheckState.Checked if image.marked else Qt.CheckState.Unchecked)
            self.dataset_table.setItem(r, 0, twi)
            n_annots = len(self.image_annotations[image.id])
            self.dataset_table.setItem(r, 1, QTableWidgetItem(f'{n_annots}'))
            self.dataset_table.setItem(r, 2, QTableWidgetItem(image.file_name))

    def selected_image_changed(self):
        if self.chk_review_mode.isChecked():
            images = [
                im for im in self.images if self.image_annotations[im.id]
            ]
        else:
            images = self.images

        index = self.dataset_table.selectedRanges()[0].topRow()
        self.dataset_table
        imname = os.path.join(self.droot, images[index].file_name)
        im_id = images[index].id
        self.app.set_image(imname, images[index].id, self.image_annotations[im_id])
        self.app.set_info('image ID', f'{im_id}')
        self.app.particle_browser.refresh_table()
