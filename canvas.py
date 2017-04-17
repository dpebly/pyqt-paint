from PyQt4 import QtGui, QtCore
from layers import Layer, Folder


class PaintScene(QtGui.QGraphicsScene):
    """
    This module deals with all stroke information for PyQtPaint.
    Creates and stores strokes, toggles visibility, communicates with PaintView
    and LayerPanel. Makes calls to QUndoFramework.

    Attributes:
        brushChanged (SIGNAL): emitted when brush settings change
        height (int): Height of scene
        next_stroke (int): Stores index of next stroke
        pen_blur (int): Controls brush hardness
        pen_color (QColor): Color of brush
        pen_size (int): Controls brush size
        strokeAdded (SIGNAL): emitted when new stroke added
        strokeRemoved (SIGNAL): emitted when stroked deleted
        undo_stack (QUndoStack): contains histroy of paint scene
        undo_view (QUndoView): history panel; currently hidden from users
        width (int): width of scene
    """

    strokeAdded = QtCore.pyqtSignal(int, str)
    strokeRemoved = QtCore.pyqtSignal(int)
    brushChanged = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(PaintScene, self).__init__(*args, **kwargs)

        # scene properties
        self.width = self.sceneRect().width()
        self.height = self.sceneRect().height()

        # stroke info
        self._strokes = {}
        self.next_stroke = 0
        self._current_path = None
        self._path_preview = None
        self._paint_layer = None
        self._is_painting = False

        # undo framework
        self.undo_stack = QtGui.QUndoStack(self)
        self.undo_view = QtGui.QUndoView(self.undo_stack)
        self.undo_view.setEmptyLabel(QtCore.QString('New'))

        # brush properites
        self.pen_size = 30
        self.pen_color = QtGui.QColor(255, 0, 0, 255)
        self.pen_blur = 0

        # scene ui styling
        border = QtGui.QPen()
        border.setWidthF(0.01)
        border.setColor(QtGui.QColor(128, 128, 128, 255))
        self.addRect(0, 0, self.width, self.height, border, QtGui.QBrush(
            QtGui.QColor(255, 255, 255, 255), QtCore.Qt.SolidPattern))

        # cursor preview
        pen = QtGui.QPen(QtGui.QColor(0, 0, 0, 255), .5,
                         QtCore.Qt.SolidLine, QtCore.Qt.RoundCap,
                         QtCore.Qt.RoundJoin)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0), QtCore.Qt.SolidPattern)
        self._cursor_outline = self.addEllipse(-15, -15, 30, 30, pen, brush)

        pen = QtGui.QPen(QtGui.QColor(255, 255, 255, 0), 1,
                         QtCore.Qt.SolidLine, QtCore.Qt.RoundCap,
                         QtCore.Qt.RoundJoin)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0, 255),
                             QtCore.Qt.SolidPattern)
        self._cursor_fill = self.addEllipse(-15, -15, 30, 30, pen, brush)
        self._cursor_fill.setOpacity(.5)

        effect = QtGui.QGraphicsBlurEffect()
        effect.setBlurRadius(self.pen_blur)
        self._cursor_fill.setGraphicsEffect(effect)
        self._cursor_fill.setZValue(1000)
        self._cursor_outline.setZValue(1001)

    @property
    def is_painting(self):
        """
        Determines whether paint scene is currently creating new stroke

        Returns:
            bool: painting state
        """
        if self._current_path is None:
            return self._current_path

    @property
    def strokes(self):
        """
        Contains dictionary of all strokes in paint scene

        Returns:
            dict: strokes in paint scene
        """
        return self._strokes

    def push_stroke(self, stroke):
        """
        creates AddStroke object & adds it to history

        Args:
            stroke (QPath): path of stroke, also contains pen/color information
        """
        command = AddStroke(self, stroke)
        self.undo_stack.push(command)

    def removeStroke(self, stroke_id):
        """
        removes stroke from paint scene

        Args:
            stroke_id (int): index of stroke
        """
        try:
            self.removeItem(self.strokes[stroke_id]['stroke'])
            # del self.strokes[stroke_id]
        except KeyError:
            pass

    def start_paintstroke(self, position, layer=None):
        """
        creates new QPath with appropriate brush settings

        Args:
            position (QPoint): start position of stroke
            layer (None, optional): index of target layer
        """
        if self.is_painting:
            if self.paintLayer == layer:
                self.update_paintstroke(position)
                return
            else:
                self.complete_paintstroke()

        self._current_path = QtGui.QGraphicsPathItem(QtGui.QPainterPath())
        pen = QtGui.QPen(self.pen_color, self.pen_size, QtCore.Qt.SolidLine,
                         QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
        self._current_path.setPen(pen)
        path = QtGui.QPainterPath(position)
        self._current_path.setPath(path)

        # brush hardness
        effect = QtGui.QGraphicsBlurEffect()
        effect.setBlurRadius(self.pen_blur)
        self._current_path.setGraphicsEffect(effect)

        # draw preview
        # preview is temp version of stroke to display while drawing
        # preview is deleted when stroke is finalized
        pen = QtGui.QPen(self.pen_color, self.pen_size,
                         QtCore.Qt.SolidLine, QtCore.Qt.RoundCap,
                         QtCore.Qt.RoundJoin)
        self._path_preview = self.addPath(QtGui.QPainterPath(), pen)
        self._path_preview.setPath(path)
        preview_effect = QtGui.QGraphicsBlurEffect()
        preview_effect.setBlurRadius(self.pen_blur)
        self._path_preview.setGraphicsEffect(preview_effect)
        self._path_preview.setZValue(self.next_stroke + 1)

    def update_paintstroke(self, position):
        """
        Update stroke on mouse move

        Args:
            position (QPoint): new position of mouse, draw to this point
        """
        try:
            path = self._current_path.path()
            path.lineTo(position)
            self._current_path.setPath(path)
            self._path_preview.setPath(path)
        except AttributeError:
            pass

    def complete_paintstroke(self, position=None):
        """
        finish paint stroke, call push_stroke to add stroke to scene.
        Delete preview stroke used for stroke visualization while drawing.

        Args:
            position (None, optional): End position
        """
        if position:
            position.setX(position.x() + .0001)
            self.update_paintstroke(position)

        # add stroke
        stroke = self._current_path
        self.push_stroke(stroke)

        # delete preview stroke
        self._current_path = None
        self.removeItem(self._path_preview)
        self._path_preview = None

    def toggle_layer_visibility(self, stroke_id, toggle):
        """
        control stroke visibilty in paint scene
        Args:
            stroke_id (int): index of stroke
            toggle (bool): visibility toggle
        """
        self.strokes[stroke_id]['stroke'].setVisible(toggle)

    def update_layer_name(self, stroke_id, name):
        """
        updates information stored in stroke, coresponds to name in layers

        Args:
            stroke_id (int): stroke index
            name (str): layer name
        """
        self.strokes[stroke_id]['name'] = name

    def set_stroke_zindex(self, stroke_id, index):
        """
        sets stoke stacking order

        Args:
            stroke_id (int): stroke index
            index (int): stacking position
        """
        self.strokes[stroke_id]['stroke'].setZValue(index)

    def move_cursor_preview(self, position):
        """
        Updates position of preview cursor

        Args:
            position (QPoint): position of cursor
        """
        self._cursor_outline.setPos(position)
        self._cursor_fill.setPos(position)

    def set_pen_size(self, size):
        """
        sets size of pen

        Args:
            size (int): diameter of brush size
        """
        self.pen_size = size
        self._cursor_outline.setRect(-size/2, -size/2, size, size)
        self._cursor_fill.setRect(-size/2, -size/2, size, size)

    def increment_pen_size(self, inc):
        """
        increment size of pen

        Args:
            inc (int): number to increment by

        """
        size = max(1, min(self.pen_size + inc, 400))
        self.set_pen_size(size)
        self.brushChanged.emit()

    def set_pen_blur(self, blur):
        """
        sets softness of pen

        Args:
            blur (int): amount to blur pen by

        """
        self.pen_blur = blur
        self._cursor_fill.graphicsEffect().setBlurRadius(blur)

    def increment_pen_blur(self, inc):
        """
        increment softness of pen

        Args:
            inc (int): number to increment by

        """
        size = max(0, min(self.pen_blur + inc, 40))
        self.set_pen_blur(size)
        self.brushChanged.emit()

    def set_pen_color(self, color):
        """
        set pen color

        Args:
            color (QColor): new pen color

        """
        self.pen_color = color
        self._cursor_fill.setBrush(QtGui.QBrush(color, QtCore.Qt.SolidPattern))


class PaintView(QtGui.QGraphicsView):
    """
    Display/input for Paint Scene
    """
    def __init__(self, *args, **kwargs):
        super(PaintView, self).__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.setFrameStyle(QtGui.QFrame.NoFrame)
        self.setBackgroundBrush(
            QtGui.QBrush(QtGui.QColor(128, 128, 128, 128),
                         QtCore.Qt.SolidPattern))
        self._current_layer = None

    @property
    def current_layer(self):
        """
        current active layer/stroke

        Returns:
            int: layer index
        """
        return self._current_layer

    @current_layer.setter
    def current_layer(self, value):
        self._current_layer = value

    def mousePressEvent(self, event):
        """
        Starts paint stroke on user's initial click
        """
        if event.button() == QtCore.Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            # self.scene().start_paintstroke(scene_pos)
            self.scene().start_paintstroke(scene_pos, layer=self.current_layer)
        super(PaintView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        updates cursor preview, updates stroke if drawing
        """
        # use event modifiers (?)
        scene_pos = self.mapToScene(event.pos())
        if event.buttons() & QtCore.Qt.LeftButton:
            self.scene().update_paintstroke(scene_pos)
        self.scene().move_cursor_preview(scene_pos)

    def mouseReleaseEvent(self, event):
        """
        comeplete paint stroke on mouse release
        """
        if event.button() == QtCore.Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            self.scene().complete_paintstroke(scene_pos)

    def wheelEvent(self, event):
        """
        change brush properties based off of keypress & user scroll
        """
        if event.modifiers() & QtCore.Qt.ControlModifier:
            self.scene().increment_pen_blur(event.delta()/abs(event.delta()))
        elif event.modifiers() & QtCore.Qt.ShiftModifier:
            self.scene().increment_pen_size(
                event.delta() / abs(event.delta()) * 2)

    def resizeEvent(self, event):
        """
        scale paint viewer so canvas is in view, maintain aspect ratip
        """
        self.fitInView(0, 0, self.scene().width, self.scene().height,
                       QtCore.Qt.KeepAspectRatio)


class AddStroke(QtGui.QUndoCommand):
    """
    Adds stroke to paint_scene
    """
    def __init__(self, parent, stroke):
        """
        Args:
            parent (QGraphicsScene): paint_scene stroke belongs to
            stroke (QPath): Stroke information
        """
        super(AddStroke, self).__init__()
        self._stroke_path = stroke
        self._parent = parent
        self._parent.next_stroke += 1
        self._stroke_id = self._parent.next_stroke

        self._layer_name = 'Stroke {:02}'.format(self._stroke_id)

        self._stroke_properties = {'stroke': None, 'name': self._layer_name,
                                   'color': stroke.pen().color(),
                                   'size': stroke.pen().width(),
                                   'blur': stroke.graphicsEffect().blurRadius()}

        self.setText(self._layer_name)
        self._stroke_properties['stroke'] = self._stroke_path

    def redo(self):
        """
        Adds stroke to scene
        """
        self._parent.addItem(self._stroke_path)
        self._parent.strokes[self._stroke_id] = self._stroke_properties
        temp_name = self._parent.strokes[self._stroke_id]['name']
        self._parent.strokeAdded.emit(self._stroke_id, temp_name)

    def undo(self):
        """
        Removes stroke from scene
        """
        self._parent.removeItem(self._stroke_path)
        self._parent.strokeRemoved.emit(self._stroke_id)


class DeleteStroke(QtGui.QUndoCommand):
    """
    Removes stroke from paint scene
    """
    def __init__(self, parent, stroke, group=None):
        """
        Args:
            parent (QGraphicsScene): paint_scene stroke belongs to
            stroke (QPath): Stroke information
            group (None, optional): if layer is grouped, pass Folder info
        """
        super(DeleteStroke, self).__init__()
        self._parent = parent
        self._stroke = stroke
        self._stroke_id = stroke.stroke_index
        self._group = None

        if group:
            self._group = group
            self._index = stroke.parent().indexOfChild(stroke)
        else:
            self._index = self._parent.layers_tree.indexOfTopLevelItem(stroke)

        self._stroke_inf = self._parent.paint_scene._strokes[stroke.stroke_index]
        self.setText(self._stroke_inf['name'])

    def redo(self):
        """
        removes stroke from scene
        """
        self._parent.paint_scene.removeStroke(self._stroke_id)
        self._parent.paint_scene.strokeRemoved.emit(self._stroke_id)

    def undo(self):
        """
        adds stroke back to scene
        """
        self._parent.paint_scene.addItem(self._stroke_inf['stroke'])

        if self._group:
            self._group.insertChild(self._index, self._stroke)

            layer_data = self._stroke.data(1,
                                           QtCore.Qt.UserRole).toPyObject()[0]
            layer_data['layerType'] = 2
            varient = QtCore.QVariant((layer_data,))
            self._stroke.setData(1, QtCore.Qt.UserRole, varient)

        else:
            self._parent.layers_tree.insertTopLevelItem(self._index,
                                                       self._stroke)


class DeleteGroup(QtGui.QUndoCommand):
    """
    delete group of strokes
    """
    def __init__(self, parent, group):
        """
        Args:
            parent (QGraphicsScene): paint scene
            group (QTreeWidgetItem): folder of group
        """
        super(DeleteGroup, self).__init__()
        self._parent = parent
        self._group = group

        self._group_index = self._parent.layers_tree.indexOfTopLevelItem(self._group)
        self.setText('Deleted Group')

    def redo(self):
        """
        deletes group & children
        """
        self._parent.paint_scene.strokeRemoved.emit(self._group.group_index)
        for i in range(self._group.childCount()):
            stroke_id = self._group.child(i).stroke_index
            self._parent.paint_scene.removeStroke(stroke_id)

    def undo(self):
        """
        re adds group & children
        """
        self._parent.layers_tree.insertTopLevelItem(
            self._group_index, self._group)

        for i in range(self._group.childCount()):
            stroke_id = self._group.child(i).stroke_index
            stroke_data = self._parent.paint_scene._strokes[stroke_id]

            self._parent.paint_scene.addItem(stroke_data['stroke'])
            self._group.setExpanded(True)


class GroupStrokes(QtGui.QUndoCommand):
    """
    group selected strokes, create folder in layers
    """
    def __init__(self, parent, strokes):
        """Summary

        Args:
            parent (QGraphicsScene): paint scene
            strokes (list): list of selected Layers
        """
        super(GroupStrokes, self).__init__()
        self._strokes = strokes
        self._parent = parent

        self._parent.paint_scene.next_stroke += 1
        self._group_index = self._parent.paint_scene.next_stroke

        column_text = ['', 'Group']

        self._group_item = Folder(None, column_text,
                                  group_index=self._group_index)

        self.setText('Group Layers')

    def redo(self):
        """
        groups strokes
        """
        iterator = QtGui.QTreeWidgetItemIterator(self._parent.layers_tree)
        while iterator.value():
            layer = iterator.value()

            remove_these = []
            if isinstance(layer, Layer):
                if layer.stroke_index in self._strokes:
                    remove_these.append(layer)
            iterator += 1

            first_index = -1
            for layer in remove_these:
                parent = layer.parent()
                if parent:
                    idx = parent.indexOfChild(layer)
                    # item = parent.takeChild(item)
                else:
                    idx = self._parent.layers_tree.indexOfTopLevelItem(layer)
                    item = self._parent.layers_tree.takeTopLevelItem(idx)

                if first_index == -1:
                    first_index = idx
                elif idx < first_index:
                    first_index = idx

                self._group_item.addChild(item)

                layer_data = layer.data(1, QtCore.Qt.UserRole).toPyObject()[0]
                layer_data['layerType'] = 2
                varient = QtCore.QVariant((layer_data,))
                layer.setData(1, QtCore.Qt.UserRole, varient)

                if parent:
                    parent.insertChild(first_index, self._group_item)
                else:
                    self._parent.layers_tree.insertTopLevelItem(first_index, self._group_item)

        self._group_item.setExpanded(True)

    def undo(self):
        """
        ungroups strokes
        """
        move_these = []
        iterator = QtGui.QTreeWidgetItemIterator(self._group_item)
        while iterator.value():
            layer = iterator.value()

            if isinstance(layer, Layer):
                if layer.stroke_index in self._strokes:
                    move_these.append(layer)
            iterator += 1

        for layer in move_these:
            parent = layer.parent()

            idx = parent.indexOfChild(layer)
            item = parent.takeChild(idx)

            parent_index = self._parent.layers_tree.indexOfTopLevelItem(self._group_item)
            self._parent.layers_tree.insertTopLevelItem(parent_index, item)

            layer_data = item.data(1, QtCore.Qt.UserRole).toPyObject()[0]
            layer_data['layerType'] = 0
            varient = QtCore.QVariant((layer_data,))
            item.setData(1, QtCore.Qt.UserRole, varient)
            item.setFlags(QtCore.Qt.ItemIsSelectable |
                          QtCore.Qt.ItemIsEditable |
                          QtCore.Qt.ItemIsEnabled |
                          QtCore.Qt.ItemIsDragEnabled)

        self._parent.paint_scene.strokeRemoved.emit(self._group_index)
