from typing import List

from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QScrollArea, QTableWidget, QTableWidgetItem, QComboBox, QPushButton, QHeaderView

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
        self.table_particles.itemSelectionChanged.connect(self.selection_changed)
        scroll.layout.addWidget(self.table_particles)

        self.table_particles.setColumnCount(4)
        self.table_particles.setHorizontalHeaderLabels(['ID', 'Class', '', ''])
        header = self.table_particles.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        self.setMinimumHeight(300)
    
    def selection_changed(self, *args):
        try:
            selected_index = self.table_particles.selectedIndexes()[0].row()
        except IndexError:
            selected_index = None
        for i, a in enumerate(self.annotations):
            a.is_selected = i == selected_index
        self.app.canvas.repaint()
            

    def refresh_table(self):
        self.table_particles.setRowCount(len(self.annotations))
        for r, annot in enumerate(self.annotations):
            self.table_particles.setItem(r, 0, QTableWidgetItem(f'{self.im_id}-{r+1}'))
            # self.table_particles.setItem(r, 1, QTableWidgetItem(CLASSES[annot.class_label-1]))
            class_sel = QComboBox()
            class_sel.addItems(CLASSES)
            class_sel.setCurrentIndex(annot.class_label - 1)
            class_sel.currentIndexChanged.connect(lambda i, a=annot: self.update_annot_label(i, a))
            self.table_particles.setCellWidget(r, 1, class_sel)

            edit_button = QPushButton('Edit')
            edit_button.clicked.connect(lambda checked=False, a=annot: self.toggle_editing(a))
            self.table_particles.setCellWidget(r, 2, edit_button)

            del_button = QPushButton('Delete')
            del_button.clicked.connect(lambda checked=False, a=annot: self.delete_annot(a))
            self.table_particles.setCellWidget(r, 3, del_button)

    def update_annot_label(self, i, a):
        a.set_label(i+1)
        self.app.canvas.repaint()
    
    def toggle_editing(self, a: Annotation):
        if self.current == a:
            self.stop_editing()
        else:
            self.edit_annot(a)
    
    def stop_editing(self):
        if self.current is not None:
            self.current.is_editing = False
            self.current = None
            self.app.canvas.repaint()
        self.app.toolbox.stop_editing_button.setEnabled(False)

    def edit_annot(self, a: Annotation):
        if self.current is not None:
            self.current.is_editing = False
        self.current = a
        a.is_editing = True
        self.refresh_table()
        self.app.canvas.repaint()
        self.app.toolbox.stop_editing_button.setEnabled(True)

    def delete_annot(self, a):
        self.annotations.remove(a)
        self.refresh_table()
        self.app.canvas.repaint()

    def set_annotations(self, annotations: List[Annotation], im_id: int):
        self.annotations = annotations
        if self.current is not None:
            self.current.is_editing = False
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
        annotation.im_id = self.im_id
        self.edit_annot(annotation)

    def finish_with_current(self):
        self.stop_editing()
