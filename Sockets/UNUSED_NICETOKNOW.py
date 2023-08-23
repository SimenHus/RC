class IconDelegate(QStyledItemDelegate):
    size = (100, 100)

    def paint(self, painter, option, index):
        icon = index.data(Qt.DecorationRole)
        mode = QIcon.Normal
        if not (option.state & QStyle.State_Enabled):
            mode = QIcon.Disabled
        elif option.state & QStyle.State_Selected:
            mode = QIcon.Selected
        state = (
            QIcon.On
            if option.state & QStyle.State_Open
            else QIcon.Off
        )
        pixmap = icon.pixmap(option.rect.size(), mode, state)
        painter.drawPixmap(option.rect, pixmap)

    def sizeHint(self, option, index):
        return QSize(self.size[0], self.size[1])

    def setSizeHint(self, sizeHint):
        self.size = (sizeHint, sizeHint) if type(sizeHint) == int else sizeHint

        # Left side menu bar
        leftMenuWidth = 100
        icon = QIcon(f'{self.path}\\snorlax.png')
        self.leftMenu = QListWidget()
        iconItem = QListWidgetItem()
        iconItem.setIcon(icon)


        delegate = IconDelegate()
        delegate.setSizeHint(leftMenuWidth-4)
        self.leftMenu.setItemDelegate(delegate)
        self.leftMenu.addItem(iconItem)
        self.leftMenu.setFixedWidth(leftMenuWidth)