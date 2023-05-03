import PIL
from PIL.Image import Image
from PyQt5 import QtCore
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QAbstractItemView, QMenu
from .q_dymo_label_widgets import TextDymoLabelWidget, QrDymoLabelWidget, BarcodeDymoLabelWidget, \
    ImageDymoLabelWidget


class QDymoLabelList(QListWidget):
    """
    A custom QListWidget for displaying and managing Dymo label widgets.
    Args:
        render_engine (RenderEngine): The render engine to use for rendering the label.
        parent (QWidget): The parent widget of this QListWidget.
    Attributes:
        renderSignal (QtCore.pyqtSignal): A signal emitted when the label is rendered.
        render_engine (RenderEngine): The render engine used for rendering the label.
    Methods:
        __init__(self, render_engine, parent=None): Initializes the QListWidget with the given render engine and parent.
        dropEvent(self, e) -> None: Overrides the default drop event to update the label rendering.
        update_render_engine(self, render_engine): Updates the render engine used for rendering the label.
        render_label(self): Renders the label using the current render engine and emits the renderSignal.
        contextMenuEvent(self, event): Overrides the default context menu event to add or delete label widgets.
    """

    renderSignal = QtCore.pyqtSignal(PIL.Image.Image, name='renderSignal')

    def __init__(self, render_engine, parent=None):
        super(QDymoLabelList, self).__init__(parent)
        self.render_engine = render_engine
        self.setAlternatingRowColors(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        for item_widget in [TextDymoLabelWidget(self.render_engine) ]:
            item = QListWidgetItem(self)
            item.setSizeHint(item_widget.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, item_widget)
            item_widget.itemRenderSignal.connect(self.render_label)
        self.render_label()

    def dropEvent(self, e) -> None:
        """
        Overrides the default drop event to update the label rendering.
        Args:
            e (QDropEvent): The drop event.
        """
        super().dropEvent(e)
        self.render_label()

    def update_render_engine(self, render_engine):
        """
        Updates the render engine used for rendering the label.
        Args:
            render_engine (RenderEngine): The new render engine to use.
        """
        self.render_engine = render_engine
        for i in range(self.count()):
            item_widget = self.itemWidget(self.item(i))
            item_widget.render_engine = render_engine
        self.render_label()

    def render_label(self):
        """
        Renders the label using the current render engine and emits the renderSignal.
        """
        bitmaps = []
        for i in range(self.count()):
            item = self.item(i)
            item_widget = self.itemWidget(self.item(i))
            if item_widget and item:
                item.setSizeHint(item_widget.sizeHint())
                bitmaps.append(item_widget.render_label())
        label_bitmap = self.render_engine.merge_render(bitmaps)

        self.renderSignal.emit(label_bitmap)

    def contextMenuEvent(self, event):
        """
        Overrides the default context menu event to add or delete label widgets.
        Args:
            event (QContextMenuEvent): The context menu event.
        """
        contextMenu = QMenu(self)
        add_text = contextMenu.addAction("AddText")
        add_qr = contextMenu.addAction("AddQR")
        add_barcode = contextMenu.addAction("AddBarcode")
        add_img = contextMenu.addAction("AddImage")
        delete = contextMenu.addAction("Delete")
        menu_click = contextMenu.exec(event.globalPos())

        if menu_click == add_text:
            item = QListWidgetItem(self)
            item_widget = TextDymoLabelWidget(self.render_engine)
            item.setSizeHint(item_widget.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, item_widget)
            item_widget.itemRenderSignal.connect(self.render_label)

        if menu_click == add_qr:
            item = QListWidgetItem(self)
            item_widget = QrDymoLabelWidget(self.render_engine)
            item.setSizeHint(item_widget.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, item_widget)
            item_widget.itemRenderSignal.connect(self.render_label)

        if menu_click == add_barcode:
            item = QListWidgetItem(self)
            item_widget = BarcodeDymoLabelWidget(self.render_engine)
            item.setSizeHint(item_widget.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, item_widget)
            item_widget.itemRenderSignal.connect(self.render_label)

        if menu_click == add_img:
            item = QListWidgetItem(self)
            item_widget = ImageDymoLabelWidget(self.render_engine)
            item.setSizeHint(item_widget.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, item_widget)
            item_widget.itemRenderSignal.connect(self.render_label)
        if menu_click == delete:
            try:
                item = self.itemAt(event.pos())
                self.takeItem(self.indexFromItem(item).row())  # self.update()
            except Exception as e:
                print(f"No item selected {e}")
        self.render_label()
