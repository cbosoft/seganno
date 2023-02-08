from typing import List

from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QScrollArea, QTableWidget, QTableWidgetItem, QComboBox, QPushButton

from .annotation import Annotation
from .class_labels import CLASSES


class ParticleBrowser(QGroupBox):

    def __init__(self, app):
        super().__init__('Particles')
        self.app = app
        self.annotations: List[Annotation] = []
        self.current = None
        self.im_id = -1

        self.layout = QVBoxLayout(self)
        scroll = QScrollArea()
        self.layout.addWidget(scroll)
        scroll.layout = QVBoxLayout(scroll)
        self.table_particles = QTableWidget()
        scroll.layout.addWidget(self.table_particles)

        self.table_particles.setColumnCount(4)
        self.table_particles.setHorizontalHeaderLabels(['ID', 'Class', '', ''])

        self.setMinimumHeight(300)

    def refresh_table(self):
        self.table_particles.setRowCount(len(self.annotations))
        for r, annot in enumerate(self.annotations):
            self.table_particles.setItem(r, 0, QTableWidgetItem(f'{self.im_id}/{r+1}'))
            # self.table_particles.setItem(r, 1, QTableWidgetItem(CLASSES[annot.class_label-1]))
            class_sel = QComboBox()
            class_sel.addItems(CLASSES)
            class_sel.setCurrentIndex(annot.class_label - 1)
            class_sel.currentIndexChanged.connect(lambda i, a=annot: self.update_annot_label(i, a))
            self.table_particles.setCellWidget(r, 1, class_sel)

            edit_button = QPushButton('Edit')
            edit_button.clicked.connect(lambda checked=False, a=annot: self.edit_annot(a))
            self.table_particles.setCellWidget(r, 2, edit_button)

            del_button = QPushButton('Delete')
            del_button.clicked.connect(lambda checked=False, a=annot: self.delete_annot(a))
            self.table_particles.setCellWidget(r, 3, del_button)

    def update_annot_label(self, i, a):
        a.set_label(i+1)
        self.app.canvas.repaint()

    def edit_annot(self, a):
        self.current = a
        self.refresh_table()

    def delete_annot(self, a):
        self.annotations.remove(a)
        self.refresh_table()
        self.app.canvas.repaint()

    def set_annotations(self, annotations: List[Annotation], im_id: int):
        self.annotations = annotations
        self.current = None
        self.im_id = im_id

    def get_current_annotation(self, x, y) -> Annotation:
        """
        return current selected annotation, or none if no annot is selected.
        """
        if self.current is not None:
            return self.current
        #  TODO: fix broken
        # elif self.annotations:
        #     for ann in self.annotations:
        #         if (x, y) in ann:
        #             self.current = ann
        #             break
        #     print('in get current', self.current)
        return self.current

    def add_annotation(self, annotation: Annotation, is_current=True):
        self.annotations.append(annotation)
        if is_current:
            self.current = annotation
        annotation.im_id = self.im_id

    def finish_with_current(self):
        if not self.current:
            return

        self.current = None
        self.refresh_table()
