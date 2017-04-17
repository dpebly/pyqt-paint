import sys
from PyQt4 import QtGui, QtCore, uic
from canvas import PaintScene, PaintView
from canvas import DeleteStroke, GroupStrokes, DeleteGroup
from layers import LayerPanel, Layer, Folder
from delegate import TreeDelegate


class PyQtPaint(QtGui.QWidget):
    """
    Canvas based painting ui w/ brush control, layers, undo functionality

    Attributes:
        color_dialog (QColorDialog): Color Picker
        file_dialog (QFileDialog): Filepath picker for saving img externally
        layers_tree (QTreeWidgetItem): Tree widget acting as a layers panel
        paint_scene (QGraphicsScene): graphics scene storing/maintaing stroke
                                      information
    Args:
        width (int): width of PyQtPaint
        height (int): height of PyQtPaint
    """
    def __init__(self, width, height, *args, **kwargs):
        super(PyQtPaint, self).__init__(*args, **kwargs)
        uic.loadUi('ui/pyqtpaint.ui', self)

        self._paint_view = PaintView()
        self._paint_view.setRenderHints(QtGui.QPainter.HighQualityAntialiasing)

        self.paint_scene = PaintScene(0, 0, width, height, None)
        self._paint_view.setScene(self.paint_scene)

        self._setup_ui()
        self._create_actions()
        self._make_connections()

    def _setup_ui(self):
        self.viewport_widget.layout().addWidget(self._paint_view)
        self.layers_tree = LayerPanel(dragToggleColumns=[0], columns=['', ''])
        self.layers_tree.setItemDelegate(TreeDelegate())
        self.layers_widget.layout().addWidget(self.layers_tree)

        self.file_dialog = QtGui.QFileDialog(self)
        self.color_dialog = QtGui.QColorDialog()

        self._update_brush_ui()

    def _create_actions(self):
        self.undo_action = QtGui.QAction('Undo', self)
        self.undo_action.setShortcut('Ctrl+Z')
        self.addAction(self.undo_action)

        self.redo_action = QtGui.QAction('Redo', self)
        self.redo_action.setShortcut('Shift+Ctrl+Z')
        self.addAction(self.redo_action)

        self.delete_action = QtGui.QAction('Delete', self)
        self.delete_action.setShortcut('Backspace')
        self.addAction(self.delete_action)

        self.group_action = QtGui.QAction('Group', self)
        self.group_action.setShortcut('Ctrl+G')
        self.addAction(self.group_action)

        self.save_action = QtGui.QAction('Save', self)
        self.save_action.setShortcut('Ctrl+S')
        self.addAction(self.save_action)

        self.increase_size_action = QtGui.QAction('Increase Size', self)
        self.increase_size_action.setShortcut(']')
        self.addAction(self.increase_size_action)

        self.decrease_size_action = QtGui.QAction('Decrease Size', self)
        self.decrease_size_action.setShortcut('[')
        self.addAction(self.decrease_size_action)

        self.brush_softer_action = QtGui.QAction('Brush Softer', self)
        self.brush_softer_action.setShortcut('{')
        self.addAction(self.brush_softer_action)

        self.brush_harder_action = QtGui.QAction('Brush Harder', self)
        self.brush_harder_action.setShortcut('}')
        self.addAction(self.brush_harder_action)

    def _make_connections(self):
        self.paint_scene.strokeAdded.connect(self.create_layer_item)
        self.paint_scene.strokeRemoved.connect(self.remove_layer_item)

        self.paint_scene.brushChanged.connect(self._update_brush_ui)
        self.size_SLD.valueChanged.connect(lambda: self.set_pen_size(self.size_SLD.value()))
        self.blur_SLD.valueChanged.connect(lambda: self.set_pen_blur(self.blur_SLD.value()))

        self.increase_size_action.triggered.connect(lambda: self.paint_scene.increment_pen_size(10))
        self.decrease_size_action.triggered.connect(lambda: self.paint_scene.increment_pen_size(-10))
        self.brush_softer_action.triggered.connect(lambda: self.paint_scene.increment_pen_blur(1))
        self.brush_harder_action.triggered.connect(lambda: self.paint_scene.increment_pen_blur(-1))

        self.redo_action.triggered.connect(self.paint_scene.undo_stack.redo)
        self.undo_action.triggered.connect(self.paint_scene.undo_stack.undo)

        self.delete_action.triggered.connect(self.delete_layer)
        self.group_action.triggered.connect(self.group_layers)

        self.save_action.triggered.connect(self.save_img)

        self.layers_tree.itemChanged.connect(self.layer_change)
        self.layers_tree.layerOrderChanged.connect(self.update_layer_index)

        self.color_BTN.clicked.connect(self.update_pen_color)

    def _update_brush_ui(self):
        self.size_SLD.setValue(self.paint_scene.pen_size)
        self.blur_SLD.setValue(self.paint_scene.pen_blur)

        style = QtCore.QString("QPushButton { border-style: none; \
                                              border-radius: 10px; \
                                              min-width: 3em; \
                                              height: 3em; \
                                              background-color: " +
                               self.paint_scene.pen_color.name() + "}")
        self.color_BTN.setStyleSheet(style)

    def create_layer_item(self, stroke_id, layer_name):
        """
        Creates layer item in layer panel using stroke data

        Args:
            stroke_id (int): unique index of stroke
            layer_name (str): name of stroke layer

        """
        stroke_info = ['', layer_name]
        layer = Layer(stroke_info, stroke_index=stroke_id)

        highest_group = None
        if self.layers_tree.selectedItems():
            iterator = QtGui.QTreeWidgetItemIterator(self.layers_tree)
            while iterator.value():
                item = iterator.value()
                if isinstance(item, Folder) and item in self.layers_tree.selectedItems():
                    highest_group = item
                    break
                iterator += 1
        if highest_group:
            highest_group.insertChild(0, layer)
        else:
            self.layers_tree.insertTopLevelItem(0, layer)
        self.update_layer_index()

    def remove_layer_item(self, stroke_id):
        """
        deletes layer item in layer panel

        Args:
            stroke_id (int): unique index of stroke to be removed

        """
        iterator = QtGui.QTreeWidgetItemIterator(self.layers_tree)

        while iterator.value():
            item = iterator.value()
            if isinstance(item, Layer):
                layer_data = item.data(1, QtCore.Qt.UserRole).toPyObject()[0]
                if layer_data['stroke_index'] == stroke_id:
                    parent = item.parent()
                    if parent:
                        idx = parent.indexOfChild(item)
                        parent.takeChild(idx)
                    else:
                        idx = self.layers_tree.indexOfTopLevelItem(item)
                        self.layers_tree.takeTopLevelItem(idx)
            if isinstance(item, Folder):
                layer_data = item.data(1, QtCore.Qt.UserRole).toPyObject()[0]

                if item.group_index == stroke_id:
                    parent = item.parent()
                    if parent:
                        idx = parent.indexOfChild(item)
                        parent.takeChild(idx)
                    else:
                        idx = self.layers_tree.indexOfTopLevelItem(item)
                        self.layers_tree.takeTopLevelItem(idx)
            iterator += 1

    def layer_change(self, item, column):
        """
        updates stroke information, used when updating visibility or layer name

        Args:
            item (QTreeWidgetItem): item associated with stroke
            column (int): column to change
        """
        if column == 0:
            if isinstance(item, Layer):
                self.paint_scene.toggle_layer_visibility(item.stroke_index,
                                                         item.visible)

            elif isinstance(item, Folder):
                for i in range(item.childCount()):
                    if item.visible is True:
                        item.child(i).setFlags(QtCore.Qt.ItemIsSelectable |
                                               QtCore.Qt.ItemIsEditable |
                                               QtCore.Qt.ItemIsEnabled |
                                               QtCore.Qt.ItemIsDragEnabled)
                    else:
                        item.child(i).setFlags(QtCore.Qt.NoItemFlags)
                    self.paint_scene.toggle_layer_visibility(item.child(i).stroke_index, item.visible)

        elif column == 1:
            if isinstance(item, Layer):
                self.paint_scene.update_layer_name(item.stroke_index,
                                                   item.text(1))

    def delete_layer(self):
        """
        Deletes selected layers
        """
        for item in self.layers_tree.selectedItems():
            # remove item.stroke_index
            if isinstance(item, Layer):
                if item.parent():
                    command = DeleteStroke(self, item, group=item.parent())
                    self.paint_scene.undo_stack.push(command)
                else:
                    command = DeleteStroke(self, item)
                    self.paint_scene.undo_stack.push(command)

            if isinstance(item, Folder):
                command = DeleteGroup(self, item)
                self.paint_scene.undo_stack.push(command)

    def group_layers(self):
        """
        groups seleted layers

        """
        if self.layers_tree.selectedItems():
            grab_items = []
            for item in self.layers_tree.selectedItems():
                if isinstance(item, Layer):
                    grab_items.append(item.stroke_index)

            command = GroupStrokes(self, grab_items)
            self.paint_scene.undo_stack.push(command)

    def update_layer_index(self):
        """
        iterates through layer panel & updates stacking order of strokes

        """
        iterator = QtGui.QTreeWidgetItemIterator(self.layers_tree)
        while iterator.value():
            item = iterator.value()
            target_index = self.layers_tree.indexFromItem(item).row()
            try:
                new_indx = len(self.paint_scene.strokes) - target_index
                self.paint_scene.set_stroke_zindex(item._stroke_index, new_indx)
            except AttributeError:
                pass

            if isinstance(item, Layer):
                layer_data = item.data(1, QtCore.Qt.UserRole).toPyObject()[0]
                parent = item.parent()
                if not parent:
                    layer_data['layerType'] = 0
                else:
                    layer_data['layerType'] = 2

                varient = QtCore.QVariant((layer_data,))
                item.setData(1, QtCore.Qt.UserRole, varient)

            elif isinstance(item, Folder):
                for i in range(item.childCount()):
                    if item.visible is True:
                        item.child(i).setFlags(QtCore.Qt.ItemIsSelectable |
                                               QtCore.Qt.ItemIsEditable |
                                               QtCore.Qt.ItemIsEnabled |
                                               QtCore.Qt.ItemIsDragEnabled)
                    else:
                        item.child(i).setFlags(QtCore.Qt.NoItemFlags)
                    self.paint_scene.toggle_layer_visibility(item.child(i).stroke_index, item.visible)
            iterator += 1

    def set_pen_size(self, size):
        """
        Sets pen size from slider input

        Args:
            size (int): diameter of pen
        """
        self.paint_scene.set_pen_size(size)
        self._update_brush_ui()

    def set_pen_blur(self, blur):
        """
        Sets pen blur

        Args:
            blur (int): level of blur
        """
        self.paint_scene.set_pen_blur(blur)
        self._update_brush_ui()

    def set_pen_color(self, color):
        """
        sets pen color

        Args:
            color (QColor): color to set
        """
        self.paint_scene.set_pen_color(color)
        self._update_brush_ui()

    def update_pen_color(self):
        """
        updates pen color from color picker
        """
        color = self.color_dialog.getColor(self.paint_scene.pen_color,
                                           self, QtCore.QString('Color'),
                                           QtGui.QColorDialog.ShowAlphaChannel)
        self.paint_scene.set_pen_color(color)

        style = QtCore.QString("QPushButton { border-style: none; \
                                              border-radius: 10px; \
                                              min-width: 3em; \
                                              height: 3em; \
                                              background-color: " +
                               color.name() + "}")
        self.color_BTN.setStyleSheet(style)

    def save_img(self):
        """
        saves image to file
        """
        filepath = self.file_dialog.getSaveFileName(self, "Save Canvas",
                                                    "Render",
                                                    "Images (*.png *.jpg)")
        if filepath:
            img = self.get_img()
            img.save(filepath)

    def get_img(self):
        """
        gets image from PyQtPaint

        Returns:
            img: returns QImage data from canvas
        """
        img = QtGui.QImage(self.paint_scene.width, self.paint_scene.height,
                           QtGui.QImage.Format_RGB32)
        paint = QtGui.QPainter(img)
        paint.setRenderHint(QtGui.QPainter.Antialiasing)
        self.paint_scene.render(paint)
        paint.end()
        return img
