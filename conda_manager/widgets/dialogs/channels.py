# -*- coding:utf-8 -*-
#
# Copyright © 2015 The Spyder Development Team
# Copyright © 2014 Gonzalo Peña-Castellanos (@goanpeca)
#
# Licensed under the terms of the MIT License

"""

"""

# Standard library imports
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)
import gettext
import requests
import sys

# Third party imports
from qtpy.QtCore import Qt, QObject, Signal, QThread
from qtpy.QtWidgets import (QDialog, QHBoxLayout, QListWidget, QListWidgetItem,
                            QPushButton, QVBoxLayout)


_ = gettext.gettext


class ChannelsDialog(QDialog):
    """
    A dialog to add delete and select active channels to search for pacakges.
    """
    sig_channels_updated = Signal(tuple, tuple)  # channels, active_channels

    def __init__(self,
                 parent=None,
                 channels=None,
                 active_channels=None,
                 conda_url=None,
                 ):

        # Check arguments: active channels, must be witbhin channels
        for ch in active_channels:
            if ch not in channels:
                raise Exception("'active_channels' must be also within "
                                "'channels'")

        super(ChannelsDialog, self).__init__(parent)
        self._parent = parent
        self._channels = channels
        self._active_channels = active_channels
        self._conda_url = conda_url
        self._edited_channel_text = ''
        self._temp_channels = channels
        self._thread = QThread(self)

        # Widgets
        self.list = QListWidget(self)
        self.button_add = QPushButton(_('Add'))
        self.button_delete = QPushButton(_('Delete'))

        # Widget setup
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setWindowOpacity(0.96)
        self.setModal(False)
        self.setStyleSheet('''ChannelsDialog {border-style: outset;
                                              border-width: 1px;
                                              border-color: beige;
                                              border-radius: 4px;}''')

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.list)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.button_delete)
        button_layout.addWidget(self.button_add)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Signals
        self.button_add.clicked.connect(self.add_channel)
        self.button_delete.clicked.connect(self.delete_channel)

        self.setup()

        self.list.itemChanged.connect(self.edit_channel)
        self.button_add.setFocus()

    def refresh(self):
        if self.list.count() == 1:
            self.button_delete.setDisabled(True)
        else:
            self.button_delete.setDisabled(False)

    def setup(self):
        for channel in sorted(self._channels):
            item = QListWidgetItem(channel, self.list)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)

            if channel in self._active_channels:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

            self.list.addItem(item)

        self.list.setCurrentRow(0)
        self.refresh()

    def add_channel(self):
        item = QListWidgetItem('', self.list)
        item.setFlags(item.flags() | Qt.ItemIsEditable |
                      Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Unchecked)
        self.list.addItem(item)
        self.list.setCurrentRow(self.list.count()-1)
        self.list.editItem(item)
        self.refresh()

    def edit_channel(self, item):
        channel = item.data(Qt.DisplayRole).strip().lower()

        if channel in self._temp_channels:
            return

        if channel != u'':
            self._edited_channel_text = channel

            if channel.startswith('https://') or channel.startswith('http://'):
                url = channel
            else:
                url = "{0}/{1}".format(self._conda_url, channel)

            # To avoid blocking the GUI
            self._worker = RequestWorker(item, url)
            self._worker.sig_finished.connect(self.handle_request)
            self._worker.sig_finished.connect(self._thread.quit)
            self._worker.moveToThread(self._thread)
            self._thread.started.connect(self._worker.start)
            self._thread.start()
            self.list.itemChanged.disconnect()
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsSelectable)
            self.button_add.setDisabled(True)
            self.button_delete.setDisabled(True)

    def handle_request(self, request, item):
        """ """
        channel = item.data(Qt.DisplayRole).strip().lower()

        if request.status_code == 200:
            temp = list(self._temp_channels)
            temp.append(channel)
            self._temp_channels = tuple(temp)
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled |
                          Qt.ItemIsSelectable)
            item.setCheckState(Qt.Checked)
            item.setData(Qt.DisplayRole, channel)
        else:
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled |
                          Qt.ItemIsSelectable | Qt.ItemIsEditable)
            item.setData(Qt.DisplayRole, u'')
            item.setCheckState(Qt.Unchecked)
            self.list.editItem(item)

        self.list.itemChanged.connect(self.edit_channel)
        self.button_add.setDisabled(False)
        self.button_delete.setDisabled(False)

    def delete_channel(self):
        index = self.list.currentIndex().row()

        if self.list.count() > 1:
            self.list.takeItem(index)
            self.button_delete.setDisabled(False)

        if self.list.count() == 1:
            self.button_delete.setDisabled(True)

    def update_channels(self):
        temp_active_channels = []
        channels = []

        for i in range(self.list.count()):
            item = self.list.item(i)
            channel = item.data(Qt.DisplayRole)

            if channel:
                channels.append(channel)

                if item.checkState() == Qt.Checked:
                    temp_active_channels.append(item.data(Qt.DisplayRole))

        self.sig_channels_updated.emit(tuple(channels),
                                       tuple(temp_active_channels))
        self.accept()

    def closeEvent(self, event):
        if self._thread.isFinished() or not self._thread.isRunning():
            self.update_channels()
        event.ignore()

    def keyPressEvent(self, event):
        key = event.key()
        if key in [Qt.Key_Return, Qt.Key_Enter]:
            self.update_channels()
        elif key in [Qt.Key_Escape]:
            self.reject()


class RequestWorker(QObject):
    sig_finished = Signal(object, object)

    def __init__(self, item, url):
        QObject.__init__(self)
        self._item = item
        self._url = url

    def start(self):
        r = requests.head(self._url)
        self.sig_finished.emit(r, self._item)


def test_widget():
    from spyderlib.utils.qthelpers import qapplication
    app = qapplication()
    widget = ChannelsDialog(
        None,
        ['spyder-ide', 'https://conda.anaconda.org/malev'],
        ['https://conda.anaconda.org/malev'],
        'https://conda.anaconda.org',
        )
    widget.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    test_widget()