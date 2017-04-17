from PyQt4 import QtGui, QtCore


class LayerPanel(QtGui.QTreeWidget):
    """
    QTreeWidget acting as a layers panel similar to photoshop/illustrator

    Attributes:
        layerOrderChanged (SIGNAL): Emitted when layers change
    """
    layerOrderChanged = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        self._drag_toggle_col = kwargs.pop('dragToggleColumns', [])
        self._columns = kwargs.pop('columns', None)
        self._drag_toggle = -1
        self._drag_toggle_state = None
        super(LayerPanel, self).__init__(*args, **kwargs)
        self.setIndentation(0)
        self._setup_panel()

    def _setup_panel(self):
        """
        intial setup of panel

        sets selection mode/drag & drop mode/columns
        """
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)
        self.viewport().setAcceptDrops(True)
        self.setDragDropMode(QtGui.QAbstractItemView.InternalMove)

        if not self._columns:
            return
        # self.setColumnCount(self._columns.count())
        self.setColumnCount(2)
        self.setHeaderLabels([n for n in self._columns])
        for i in range(2):
            self.resizeColumnToContents(i)

        self.header().resizeSection(0, 30)
        self.header().setResizeMode(QtGui.QHeaderView.Fixed)

    def mousePressEvent(self, event):
        """
        Toggles visibility, expands/contracts folders
        """
        pos = event.pos()
        col = self.columnAt(pos.x())
        item = self.itemAt(pos)
        if col in self._drag_toggle_col:
            self._drag_toggle = col
            item = self.itemAt(pos)
            if item:
                parent = item.parent()
                if parent and not parent.visible:
                    pass
                else:
                    self._drag_toggle_state = not item.get_toggle_state(col)
                    item.set_toggle_state(col, self._drag_toggle_state)

            if isinstance(item, Folder):
                if item.visible:
                    for i in range(item.childCount()):
                        item.child(i).set_toggle_state(col, True)
                else:
                    for i in range(item.childCount()):
                        item.child(i).set_toggle_state(col, False)
            return
        if isinstance(item, Folder) and pos.x() < 60:
            if item.isExpanded():
                item.setExpanded(False)
            else:
                item.setExpanded(True)

        super(LayerPanel, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        updates ui on mouse move, responsible for drag-toggle-visibility effect
        """
        if self._drag_toggle != -1:
            pos = event.pos()
            col = self.columnAt(pos.x())
            # double check it's over an item
            # so iterator doesnt error over header
            if col == self._drag_toggle:
                item = self.itemAt(pos)
                if item:
                    parent = item.parent()
                    if parent and not parent.visible:
                        pass
                    else:
                        item.set_toggle_state(col, self._drag_toggle_state)
                if isinstance(item, Folder):
                    if item.visible:
                        for i in range(item.childCount()):
                            item.child(i).set_toggle_state(col, True)
                    else:
                        for i in range(item.childCount()):
                            item.child(i).set_toggle_state(col, False)
            return
        super(LayerPanel, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """
        releases drag-toggle
        """
        self._drag_toggle = -1
        super(LayerPanel, self).mouseReleaseEvent(event)

    def dropEvent(self, event):
        """
        checks positon of item being moved & reorders layers accordingly
        """
        item = self.itemAt(event.pos())
        if item is not None and (isinstance(item, Folder)):
            super(LayerPanel, self).dropEvent(event)
            self.layerOrderChanged.emit()
        if self.dropIndicatorPosition() in (QtGui.QAbstractItemView.AboveItem,
                                            QtGui.QAbstractItemView.BelowItem):
            super(LayerPanel, self).dropEvent(event)
            self.layerOrderChanged.emit()
        else:
            event.setDropAction(QtCore.Qt.IgnoreAction)


class Layer(QtGui.QTreeWidgetItem):
    """
    Layer item visible in Layers pannel, stores information about
    individual strokes

    Attributes:
        visible (bool): layer visibility
    """
    def __init__(self, parent, *args, **kwargs):
        self._stroke_index = kwargs.pop('stroke_index', '')
        vis = kwargs.pop('visibility', True)
        super(Layer, self).__init__(parent, *args, **kwargs)
        self._visible = True
        self.visible = vis
        self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable |
                      QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDragEnabled)
        self.setSizeHint(0, QtCore.QSize(0, 25))

        layer_info = {}
        layer_info['layerType'] = 0
        layer_info['stroke_index'] = self._stroke_index
        varient = QtCore.QVariant((layer_info,))
        self.setData(1, QtCore.Qt.UserRole, varient)

    @property
    def stroke_index(self):
        """
        unique index number for each stroke

        Returns:
            int: stroke index
        """
        return self._stroke_index

    @stroke_index.setter
    def stroke_index(self, value):
        self._stroke_index = value

    def get_toggle_state(self, column):
        """
        check toggle state for given column (used to check visibility of layer)

        Args:
            column (int): column to check toggle state

        Returns:
            bool: layer visibility
        """
        if column == 0:
            return self.visible

    def set_toggle_state(self, column, state):
        """
        set toggle state of column

        Args:
            column (int): column to get toggle state
            state (bool): state to assign
        """
        if column == 0:
            self.visible = state

    @property
    def visible(self):
        """
        layer visibility status
        """
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value
        self.setData(0, QtCore.Qt.UserRole, value)

    def toggle_visibility(self, visible=None):
        """
        changes visibility of item

        Args:
            visible (None, optional): current visibility status
        """
        if visible is None:
            self.visible = not self.visible
        else:
            self.visible = bool(visible)


class Folder(QtGui.QTreeWidgetItem):
    """
    Folder item visible in Layers pannel, stores information about
    groups of strokes

    Attributes:
        visible (bool): group visibility
    """
    def __init__(self, parent, *args, **kwargs):
        vis = kwargs.pop('visibility', True)
        self._group_index = kwargs.pop('group_index', '')
        super(Folder, self).__init__(parent, *args, **kwargs)
        self._visible = True
        self.visible = vis
        self.setSizeHint(0, QtCore.QSize(0, 25))
        self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable |
                      QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDragEnabled)
        folder_info = {}
        folder_info['layerType'] = 1

        varient = QtCore.QVariant((folder_info,))
        self.setData(1, QtCore.Qt.UserRole, varient)

    def get_toggle_state(self, column):
        """
        check toggle state for given column (used to check visibility of layer)

        Args:
            column (int): column to check toggle state

        Returns:
            bool: layer visibility
        """
        if column == 0:
            return self.visible

    def set_toggle_state(self, column, state):
        """
        set toggle state of column

        Args:
            column (int): column to get toggle state
            state (bool): state to assign
        """
        if column == 0:
            self.visible = state

    @property
    def group_index(self):
        """
        unique index number for group of strokes

        Returns:
            int: group index
        """
        return self._group_index

    @property
    def visible(self):
        """
        layer visibility status

        Returns:
            bool: layer visibility
        """
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value
        self.setData(0, QtCore.Qt.UserRole, value)

    def toggle_visibility(self, visible=None):
        """
        changes visibility of group

        Args:
            visible (None, optional): current visibility status
        """
        if visible is None:
            self.visible = not self.visible
        else:
            self.visible = bool(visible)
