from PyQt4 import QtGui, QtCore


class TreeDelegate(QtGui.QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        col_num = index.column()
        if col_num == 0:
            return
        return super(TreeDelegate, self).createEditor(parent, option, index)

    def setModelData(self, editor, model, index):
        return super(TreeDelegate, self).setModelData(editor, model, index)

    def paint(self, painter, option, index):
        icon_dim = 14
        col_num = index.column()
        background = QtGui.QColor(0, 0, 0, 10)
        line_color = QtGui.QColor(0, 0, 0, 10)

        if col_num == 0:
            if option.state & QtGui.QStyle.State_Enabled:
                if index.data(QtCore.Qt.UserRole).toPyObject():
                    painter.save()
                    # Set painter bassed on selection state.
                    if option.state & QtGui.QStyle.State_Selected:
                        painter.setPen(QtCore.Qt.white)
                        style = option.widget.style() if option.widget else QtGui.QApplication.style()
                        style.drawPrimitive(QtGui.QStyle.PE_PanelItemViewItem,
                                            option, painter, None)
                        opt = QtGui.QStyleOptionViewItemV4()
                        self.initStyleOption(opt, index)
                        style.drawControl(QtGui.QStyle.CE_ItemViewItem,
                                          option, painter, option.widget)
                        painter.setPen(QtCore.Qt.black)

                    img = QtGui.QPixmap('img/eye.png')
                    icon_rect = QtCore.QRect(option.rect)
                    painter.drawPixmap(icon_rect.center().x() - icon_dim / 2,
                                       icon_rect.center().y() - icon_dim / 2,
                                       icon_dim, icon_dim, img)
                    painter.setPen(QtGui.QPen(line_color, 0,
                                              QtCore.Qt.SolidLine,
                                              QtCore.Qt.SquareCap))
                    painter.pen().setWidthF(0)
                    painter.drawLine(option.rect.x(), option.rect.y() +
                                     option.rect.height(), option.rect.x() +
                                     option.rect.width(), option.rect.y() +
                                     option.rect.height())
                    painter.drawLine(option.rect.x(), option.rect.y(),
                                     option.rect.x() + option.rect.width(),
                                     option.rect.y())
                    painter.restore()
                    return

                else:
                    if option.state & QtGui.QStyle.State_Selected:
                        painter.setPen(QtCore.Qt.white)
                        style = option.widget.style() if option.widget else QtGui.QApplication.style()
                        style.drawPrimitive(QtGui.QStyle.PE_PanelItemViewItem,
                                            option, painter, None)
                        opt = QtGui.QStyleOptionViewItemV4()
                        self.initStyleOption(opt, index)
                        style.drawControl(QtGui.QStyle.CE_ItemViewItem,
                                          option, painter, option.widget)
                        painter.setPen(QtCore.Qt.black)

                    painter.save()
                    painter.setPen(QtGui.QPen(line_color, 0,
                                              QtCore.Qt.SolidLine,
                                              QtCore.Qt.SquareCap))
                    painter.pen().setWidthF(0)
                    painter.drawLine(option.rect.x(), option.rect.y() +
                                     option.rect.height(), option.rect.x() +
                                     option.rect.width(), option.rect.y() +
                                     option.rect.height())
                    painter.drawLine(option.rect.x(), option.rect.y(),
                                     option.rect.x() + option.rect.width(),
                                     option.rect.y())
                    painter.restore()
                    return
            else:
                painter.save()
                icon_rect = QtCore.QRect(option.rect)

                br = option.rect.adjusted(icon_dim * 3, 0, 0, 0)
                flags = QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
                fm = painter.fontMetrics()
                text = index.data(QtCore.Qt.DisplayRole).toPyObject()
                # this takes care of adding the ellipses as necessary
                text = fm.elidedText(text, QtCore.Qt.ElideRight, br.width())
                br = painter.boundingRect(br, int(flags), text)
                painter.fillRect(option.rect, background)
                painter.setPen(QtGui.QColor(0, 0, 0, 180))
                painter.drawText(br, 0, text)
                painter.setPen(QtGui.QPen(line_color, 0, QtCore.Qt.SolidLine,
                                          QtCore.Qt.SquareCap))
                painter.pen().setWidthF(0)
                painter.drawLine(option.rect.x(), option.rect.y() +
                                 option.rect.height(), option.rect.x() +
                                 option.rect.width(), option.rect.y() +
                                 option.rect.height())
                painter.drawLine(option.rect.x(), option.rect.y(),
                                 option.rect.x() + option.rect.width(),
                                 option.rect.y())
                painter.restore()

                return

        elif col_num == 1:
            # layerType = index.data(QtCore.Qt.UserRole).toPyObject()
            layer_data = index.data(QtCore.Qt.UserRole).toPyObject()[0]
            #   group
            if layer_data and layer_data['layerType'] == 1:

                painter.save()
                if option.state & QtGui.QStyle.State_Selected:
                    painter.setPen(QtCore.Qt.white)
                    style = option.widget.style() if option.widget else QtGui.QApplication.style()
                    style.drawPrimitive(QtGui.QStyle.PE_PanelItemViewItem,
                                        option, painter, None)
                    opt = QtGui.QStyleOptionViewItemV4()
                    self.initStyleOption(opt, index)
                    style.drawControl(QtGui.QStyle.CE_ItemViewItem, option,
                                      painter, option.widget)
                    painter.setPen(QtCore.Qt.black)

                if option.state & QtGui.QStyle.State_Open:
                    img = QtGui.QPixmap('img/arrow-down.png')
                elif option.state:
                    img = QtGui.QPixmap('img/arrow-right.png')

                icon_rect = QtCore.QRect(option.rect)

                x = icon_rect.x() + icon_dim/2
                y = icon_rect.center().y() - icon_dim/2

                painter.drawPixmap(x, y, icon_dim, icon_dim, img)

                img = QtGui.QPixmap('img/folder.png')
                icon_rect = QtCore.QRect(option.rect)

                x = icon_rect.x() + icon_dim * 2
                y = icon_rect.center().y() - icon_dim/2

                painter.drawPixmap(x, y, icon_dim, icon_dim, img)
                # painter.restore()

                br = option.rect.adjusted(icon_dim * 3.5, 0, 0, 0)
                flags = QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
                fm = painter.fontMetrics()
                text = index.data(QtCore.Qt.DisplayRole).toPyObject()
                text = fm.elidedText(text, QtCore.Qt.ElideRight, br.width())
                br = painter.boundingRect(br, int(flags), text)
                painter.drawText(br, 0, text)
                painter.setPen(QtGui.QPen(line_color, 0, QtCore.Qt.SolidLine,
                                          QtCore.Qt.SquareCap))
                painter.pen().setWidthF(0)
                painter.drawLine(option.rect.x(), option.rect.y() +
                                 option.rect.height(), option.rect.x() +
                                 option.rect.width(), option.rect.y() +
                                 option.rect.height())
                painter.drawLine(option.rect.x(), option.rect.y(),
                                 option.rect.x() + option.rect.width(),
                                 option.rect.y())
                painter.restore()

                return
            # stroke
            elif layer_data and layer_data['layerType'] == 0:
                painter.save()
                if option.state & QtGui.QStyle.State_Selected:
                    painter.setPen(QtCore.Qt.white)
                    style = option.widget.style() if option.widget else QtGui.QApplication.style()
                    style.drawPrimitive(QtGui.QStyle.PE_PanelItemViewItem,
                                        option, painter, None)
                    opt = QtGui.QStyleOptionViewItemV4()
                    self.initStyleOption(opt, index)
                    style.drawControl(QtGui.QStyle.CE_ItemViewItem, option,
                                      painter, option.widget)
                    painter.setPen(QtCore.Qt.black)

                # painter.restore()

                br = option.rect.adjusted(icon_dim * 2, 0, 0, 0)
                flags = QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
                fm = painter.fontMetrics()
                text = index.data(QtCore.Qt.DisplayRole).toPyObject()
                # this takes care of adding the ellipses as necessary
                text = fm.elidedText(text, QtCore.Qt.ElideRight, br.width())
                br = painter.boundingRect(br, int(flags), text)
                painter.drawText(br, 0, text)
                painter.setPen(QtGui.QPen(line_color, 0, QtCore.Qt.SolidLine,
                                          QtCore.Qt.SquareCap))
                painter.pen().setWidthF(0)
                painter.drawLine(option.rect.x(), option.rect.y() +
                                 option.rect.height(), option.rect.x() +
                                 option.rect.width(), option.rect.y() +
                                 option.rect.height())
                painter.drawLine(option.rect.x(), option.rect.y(),
                                 option.rect.x() + option.rect.width(),
                                 option.rect.y())
                painter.restore()

                return
            elif layer_data and layer_data['layerType'] == 2:
                if option.state & QtGui.QStyle.State_Enabled:
                    painter.save()
                    if option.state & QtGui.QStyle.State_Selected:
                        painter.setPen(QtCore.Qt.white)
                        style = option.widget.style() if option.widget else QtGui.QApplication.style()
                        style.drawPrimitive(QtGui.QStyle.PE_PanelItemViewItem,
                                            option, painter, None)
                        opt = QtGui.QStyleOptionViewItemV4()
                        self.initStyleOption(opt, index)
                        style.drawControl(QtGui.QStyle.CE_ItemViewItem,
                                          option, painter, option.widget)
                        painter.setPen(QtCore.Qt.black)
                    icon_rect = QtCore.QRect(option.rect)

                    br = option.rect.adjusted(icon_dim * 3, 0, 0, 0)
                    flags = QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
                    fm = painter.fontMetrics()
                    text = index.data(QtCore.Qt.DisplayRole).toPyObject()
                    # this takes care of adding the ellipses as necessary
                    text = fm.elidedText(text, QtCore.Qt.ElideRight,
                                         br.width())
                    br = painter.boundingRect(br, int(flags), text)
                    painter.drawText(br, 0, text)
                    painter.setPen(QtGui.QPen(line_color, 0,
                                              QtCore.Qt.SolidLine,
                                              QtCore.Qt.SquareCap))
                    painter.pen().setWidthF(0)
                    painter.drawLine(option.rect.x(), option.rect.y() +
                                     option.rect.height(), option.rect.x() +
                                     option.rect.width(), option.rect.y() +
                                     option.rect.height())
                    painter.drawLine(option.rect.x(), option.rect.y(),
                                     option.rect.x() + option.rect.width(),
                                     option.rect.y())
                    painter.restore()

                    return

                else:
                    painter.save()
                    icon_rect = QtCore.QRect(option.rect)

                    br = option.rect.adjusted(icon_dim * 3, 0, 0, 0)
                    flags = QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
                    fm = painter.fontMetrics()
                    text = index.data(QtCore.Qt.DisplayRole).toPyObject()
                    # this takes care of adding the ellipses as necessary
                    text = fm.elidedText(text, QtCore.Qt.ElideRight,
                                         br.width())
                    br = painter.boundingRect(br, int(flags), text)
                    painter.fillRect(option.rect, background)
                    painter.setPen(QtGui.QColor(0, 0, 0, 100))
                    painter.drawText(br, 0, text)
                    painter.setPen(QtGui.QPen(line_color, 0,
                                              QtCore.Qt.SolidLine,
                                              QtCore.Qt.SquareCap))
                    painter.pen().setWidthF(0)
                    painter.drawLine(option.rect.x(), option.rect.y() +
                                     option.rect.height(), option.rect.x() +
                                     option.rect.width(), option.rect.y() +
                                     option.rect.height())
                    painter.drawLine(option.rect.x(), option.rect.y(),
                                     option.rect.x() + option.rect.width(),
                                     option.rect.y())
                    painter.restore()

                return
        return super(TreeDelegate, self).paint(painter, option, index)
