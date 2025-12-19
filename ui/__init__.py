import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QLabel, QPushButton, QSpinBox,
    QTextBrowser, QTextEdit,
    QCheckBox,
    QVBoxLayout, QHBoxLayout,
    QFileDialog, QStatusBar,
    QMessageBox
)
from PyQt6.QtCore import Qt, QStandardPaths, QUrl
from PyQt6.QtGui import QDesktopServices

# IMPORT DOS GERADORES
from src.cograph_generator.generator import (
    generate_cographs_final_g6,
    generate_cotree_images
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("COGRAPH GENERATOR")
        self.resize(900, 600)

        central = QWidget()
        self.setCentralWidget(central)

        # =======================
        # Title
        # =======================
        title = QLabel("COGRAPH GENERATOR")
        title.setStyleSheet("font-size:18px; font-weight:bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # =======================
        # Range selection
        # =======================
        range_label = QLabel(
            "Generate graphs with a number of vertices in the range:"
        )

        self.minVertices = QSpinBox()
        self.minVertices.setRange(1, 50)
        self.minVertices.setValue(1)

        self.maxVertices = QSpinBox()
        self.maxVertices.setRange(1, 50)
        self.maxVertices.setValue(10)

        self.minVertices.valueChanged.connect(
            lambda v: self.maxVertices.setMinimum(v)
        )
        self.maxVertices.valueChanged.connect(
            lambda v: self.minVertices.setMaximum(v)
        )

        range_layout = QHBoxLayout()
        range_layout.addWidget(range_label)
        range_layout.addWidget(self.minVertices)
        range_layout.addWidget(self.maxVertices)
        range_layout.addStretch()

        # =======================
        # Connectivity options
        # =======================
        conn_label = QLabel("Select at least one option")

        self.cb_connected = QCheckBox("Connected cographs")
        self.cb_disconnected = QCheckBox("Disconnected cographs")

        conn_layout = QVBoxLayout()
        conn_layout.addWidget(conn_label)
        conn_layout.addWidget(self.cb_connected)
        conn_layout.addWidget(self.cb_disconnected)

        # =======================
        # Output options
        # =======================
        output_label = QLabel("Select at least one option")

        self.cb_graph6 = QCheckBox("Cographs in graph6 format")
        self.cb_cotree = QCheckBox("Image of cotree in .jpg file")

        output_layout = QVBoxLayout()
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.cb_graph6)
        output_layout.addWidget(self.cb_cotree)

        # =======================
        # Export location
        # =======================
        export_label = QLabel("Export location")

        self.export_path = QTextEdit()
        self.export_path.setFixedHeight(24)

        documents_path = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation
        )
        self.export_path.setText(documents_path)

        self.btn_select_folder = QPushButton("Select folder")
        self.btn_select_folder.clicked.connect(self.select_folder)

        export_layout = QHBoxLayout()
        export_layout.addWidget(export_label)
        export_layout.addWidget(self.export_path)
        export_layout.addWidget(self.btn_select_folder)

        # =======================
        # Warning box
        # =======================
        self.warning = QTextBrowser()
        self.warning.setFixedHeight(130)
        self.warning.setHtml(
            "<p><b>Warning:</b></p>"
            "<p>When choosing to generate the cotree image, consider the "
            "possibility of creating more than one million files.</p>"
            "<p>Above 30 vertices, the process may take many hours.</p>"
        )

        # =======================
        # Bottom buttons
        # =======================
        self.btn_refs = QPushButton("References")
        self.btn_tables = QPushButton("Tables")
        self.btn_docs = QPushButton("Documentation")

        self.btn_refs.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://www.graphclasses.org/classes/gc_151.html")
            )
        )
        self.btn_tables.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://houseofgraphs.org/meta-directory/cographs")
            )
        )
        self.btn_docs.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://github.com/fsoupimenta/cograph-generator")
            )
        )

        self.btn_run = QPushButton("Run")
        self.btn_run.setFixedWidth(120)
        self.btn_run.clicked.connect(self.run_generation)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.btn_refs)
        bottom_layout.addWidget(self.btn_tables)
        bottom_layout.addWidget(self.btn_docs)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.btn_run)

        # =======================
        # Main layout
        # =======================
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(15)
        main_layout.addWidget(title)
        main_layout.addLayout(range_layout)
        main_layout.addLayout(conn_layout)
        main_layout.addLayout(output_layout)
        main_layout.addLayout(export_layout)
        main_layout.addWidget(self.warning)
        main_layout.addLayout(bottom_layout)

        self.setStatusBar(QStatusBar())

    # =======================
    # Slots
    # =======================
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select export folder",
            self.export_path.toPlainText()
        )
        if folder:
            self.export_path.setText(folder)

    def run_generation(self):
        min_v = self.minVertices.value()
        max_v = self.maxVertices.value()
        output_dir = self.export_path.toPlainText().strip()

        if not output_dir:
            QMessageBox.warning(self, "Error", "Select an export directory.")
            return

        if not (self.cb_graph6.isChecked() or self.cb_cotree.isChecked()):
            QMessageBox.warning(
                self, "Error",
                "Select at least one output option."
            )
            return

        if not (self.cb_connected.isChecked() or self.cb_disconnected.isChecked()):
            QMessageBox.warning(
                self, "Error",
                "Select connected and/or disconnected cographs."
            )
            return

        connected_only = (
            self.cb_connected.isChecked() and
            not self.cb_disconnected.isChecked()
        )

        for node_count in range(min_v, max_v + 1):
            if self.cb_graph6.isChecked():
                generate_cographs_final_g6(
                    node_count=node_count,
                    output_dir=output_dir,
                    connected_only=connected_only
                )

            if self.cb_cotree.isChecked():
                generate_cotree_images(
                    node_count=node_count,
                    output_dir=output_dir
                )

        QMessageBox.information(
            self, "Done",
            "Cograph generation completed successfully."
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
