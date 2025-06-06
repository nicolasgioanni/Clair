#!/usr/bin/env python3
import sys, json, shutil
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFileDialog,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QSpacerItem, QSizePolicy, QScrollArea, QGridLayout,
    QInputDialog, QGroupBox, QCheckBox
)
from PySide6.QtGui import QPalette, QColor, QFont, QIcon
from PySide6.QtCore import Qt, QTimer

# --- CONFIGURATION & DEFAULTS ---
CONFIG_PATH = Path(__file__).parent / "categories.json"  # path to save categories
default_cats = {                                       # built-in default file categories
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx"],
    "Images":    [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"],
    "Videos":    [".mp4", ".mov", ".avi", ".mkv", ".flv"],
    "Music":     [".mp3", ".wav", ".aac", ".flac"],
    "Archives":  [".zip", ".tar", ".gz", ".rar", ".7z"]
}
ordered_types    = ["Documents", "Images", "Videos", "Music", "Archives"]
type_exts        = {t: default_cats[t] for t in ordered_types}         # per-type extension lists
all_exts_grouped = {t: default_cats[t] for t in ordered_types}         # grouped for "All" view

# custom extensions list (loaded/saved from categories.json → "custom_extensions")
CUSTOM_EXTS = []

# --- LOAD / SAVE CATEGORY CONFIG ---
def load_config():
    # read existing categories.json or initialize defaults
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text())
            # Expect file format:
            # {
            #   "categories": { "Documents": [...], ... },
            #   "custom_extensions": [".dv", ...]
            # }
            cats = data.get("categories", default_cats.copy())
            CUSTOM_EXTS[:] = data.get("custom_extensions", [])
            return cats
        except:
            pass
    # if no valid file, write defaults + empty custom list
    save_config(default_cats, [])
    return default_cats.copy()

def save_config(cats, custom_exts=None):
    # write both categories and custom‐extension list back to categories.json
    if custom_exts is None:
        custom_exts = CUSTOM_EXTS
    data = {
        "categories": cats,
        "custom_extensions": custom_exts
    }
    CONFIG_PATH.write_text(json.dumps(data, indent=4))

# --- PRESETS SUPPORT ---
PRESETS_PATH = Path(__file__).parent / "presets.json"  # path to save presets

def load_presets():
    # load saved presets or fallback to Default
    presets = {"Default": default_cats.copy()}
    if PRESETS_PATH.exists():
        try:
            presets.update(json.loads(PRESETS_PATH.read_text()))
        except:
            pass
    return presets

def save_presets(user_presets):
    # write user-defined presets
    PRESETS_PATH.write_text(json.dumps(user_presets, indent=4))

# --- EXTENSION CHECKBOX WIDGET BUILDER ---
def make_extension_widget(exts, selected, on_change):
    # create scrollable checkboxes for extensions
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(0,0,0,0)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    content = QWidget()

    if isinstance(exts, dict):
        # grid layout for "All" grouped categories + custom extensions row
        grid = QGridLayout(content)
        # one row per built-in type
        for r, t in enumerate(ordered_types):
            for c, e in enumerate(exts[t]):
                cb = QCheckBox(e)
                cb.setChecked(e in selected)
                cb.clicked.connect(lambda _, x=e: on_change(x))
                grid.addWidget(cb, r, c)

        # add extra row after built-in types for any custom extensions
        custom_row = len(ordered_types)
        for c, e in enumerate(CUSTOM_EXTS):
            cb = QCheckBox(e)
            cb.setChecked(e in selected)
            cb.clicked.connect(lambda _, x=e: on_change(x))
            grid.addWidget(cb, custom_row, c)

        content.setLayout(grid)

    else:
        # horizontal layout for single-type
        from PySide6.QtWidgets import QHBoxLayout
        row = QHBoxLayout(content)
        for e in exts:
            cb = QCheckBox(e)
            cb.setChecked(e in selected)
            cb.clicked.connect(lambda _, x=e: on_change(x))
            row.addWidget(cb)
        row.addStretch()
        content.setLayout(row)

    scroll.setWidget(content)
    layout.addWidget(scroll)
    return widget

# --- MAIN APPLICATION WINDOW ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clair Organizer")
        self.setFixedSize(800, 820)
        self._setup_dark_theme()                   # apply dark theme
        self.cats    = load_config()               # current categories
        self.presets = load_presets()              # presets dictionary

        central = QWidget()
        main = QVBoxLayout(central)

        # folder selection row
        frow = QHBoxLayout()
        frow.addWidget(QLabel("Folder:"))
        self.path = QLineEdit()
        self.path.setReadOnly(True)
        frow.addWidget(self.path)
        btn_b = QPushButton("Browse...")
        btn_b.setIcon(QIcon.fromTheme("folder-open"))
        btn_b.clicked.connect(self.choose_folder)
        frow.addWidget(btn_b)
        main.addLayout(frow)

        # subfolder and delete-empty toggles
        orow = QHBoxLayout()
        self.rec       = QCheckBox("Include Subfolders")
        self.del_empty = QCheckBox("Delete Empty Subfolders")
        self.del_empty.setVisible(False)  # hidden until needed
        orow.addWidget(self.rec)
        orow.addWidget(self.del_empty)
        orow.addItem(QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum))
        main.addLayout(orow)
        self.rec.toggled.connect(self.del_empty.setVisible)

        # organize button
        btn_o = QPushButton("Organize Now")
        btn_o.setIcon(QIcon.fromTheme("system-run"))
        btn_o.setFixedHeight(40)
        btn_o.clicked.connect(self.run_organizer)
        main.addWidget(btn_o)

        # presets toolbar
        prow = QHBoxLayout()
        prow.addWidget(QLabel("Preset:"))
        self.pcombo = QComboBox()
        self.pcombo.addItems(self.presets.keys())
        self.pcombo.currentTextChanged.connect(self.load_preset)
        prow.addWidget(self.pcombo)
        for label, fn in (
            ("Add Preset",    self.add_preset),
            ("Rename Preset", self.rename_preset),
            ("Save Preset",   self.save_preset),
            ("Delete Preset", self.delete_preset)
        ):
            b = QPushButton(label)
            b.clicked.connect(fn)
            prow.addWidget(b)
        prow.addItem(QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum))
        main.addLayout(prow)

        # categories management table
        cg = QGroupBox("Manage Categories")
        cgl = QVBoxLayout(cg)
        self.tbl = QTableWidget(0,3)
        self.tbl.setHorizontalHeaderLabels(["Folder Name","Type","Extensions"])
        self.tbl.setSelectionBehavior(QTableWidget.SelectRows)
        self.tbl.setStyleSheet(
            "QTableWidget::item:selected {"
            " background: transparent;"
            " border-top: 1px solid white; border-bottom: 1px solid white;"
            " color: white;}"
        )
        hdr = self.tbl.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.Stretch)
        cgl.addWidget(self.tbl)

        # add/remove category buttons
        b2 = QHBoxLayout()
        ba = QPushButton("Add Category")
        ba.clicked.connect(self.add_category)
        br = QPushButton("Remove Category")
        br.clicked.connect(self.remove_category)
        b2.addWidget(ba)
        b2.addWidget(br)
        b2.addItem(QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum))
        cgl.addLayout(b2)
        main.addWidget(cg)

        # status message label
        self.status = QLabel("")
        self.status.setStyleSheet("color:#4caf50;font-weight:bold;")
        main.addWidget(self.status)

        # -- Add Extension button at bottom right --
        grow = QHBoxLayout()
        grow.addItem(QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum))
        btn_add_ext = QPushButton("Add Extension")
        btn_add_ext.clicked.connect(self.add_extension)
        grow.addWidget(btn_add_ext)
        main.addLayout(grow)

        self.setCentralWidget(central)

        # load default preset on startup
        self.pcombo.setCurrentText("Default")
        self.load_preset("Default")
        self.populate_table()

    def _setup_dark_theme(self):
        # configure a dark palette
        p = QPalette()
        p.setColor(QPalette.Window,        QColor(30,30,30))
        p.setColor(QPalette.WindowText,    Qt.white)
        p.setColor(QPalette.Base,          QColor(45,45,45))
        p.setColor(QPalette.AlternateBase, QColor(53,53,53))
        p.setColor(QPalette.Text,          Qt.white)
        p.setColor(QPalette.Button,        QColor(53,53,53))
        p.setColor(QPalette.ButtonText,    Qt.white)
        p.setColor(QPalette.Highlight,     QColor(42,130,218))
        p.setColor(QPalette.HighlightedText, Qt.black)
        QApplication.setPalette(p)
        QApplication.setFont(QFont("Segoe UI",10))

    def populate_table(self):
        # rebuild table rows from self.cats
        self.tbl.setRowCount(0)
        for name, exts in self.cats.items():
            r = self.tbl.rowCount()
            self.tbl.insertRow(r)
            self.tbl.setItem(r,0, QTableWidgetItem(name))

            combo = QComboBox()
            combo.addItems(["All"] + ordered_types)
            combo.setCurrentText(name if name in ordered_types else "All")
            combo.currentTextChanged.connect(lambda t,row=r: self.on_type_change(row,t))
            combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
            self.tbl.setCellWidget(r,1, combo)

            w = make_extension_widget(
                all_exts_grouped if combo.currentText()=="All" else type_exts[combo.currentText()],
                exts,
                lambda e,row=r: self.on_ext_change(row,e)
            )
            self.tbl.setCellWidget(r,2, w)
            self.tbl.setRowHeight(r, 200 if combo.currentText()=="All" else 50)

    def on_type_change(self, row, t):
        # update category when type dropdown changes
        nm = self.tbl.item(row,0).text()
        default = all_exts_grouped if t=="All" else type_exts[t]
        self.cats[nm] = default.copy()
        save_config(self.cats, CUSTOM_EXTS)
        self.populate_table()

    def on_ext_change(self, row, ext):
        # update extension list when a checkbox toggles
        nm = self.tbl.item(row,0).text()
        btns = self.tbl.cellWidget(row,2).findChildren(QCheckBox)
        self.cats[nm] = [b.text() for b in btns if b.isChecked()]
        save_config(self.cats, CUSTOM_EXTS)

    def add_category(self):
        # prompt and add new category
        txt, ok = QInputDialog.getText(self,"New Category","Category name:")
        if ok and txt.strip():
            self.cats[txt.strip()] = []
            save_config(self.cats, CUSTOM_EXTS)
            self.populate_table()
            self.show_status(f"Added '{txt.strip()}'")

    def remove_category(self):
        # remove selected category row
        r = self.tbl.currentRow()
        if r>=0:
            nm = self.tbl.item(r,0).text()
            self.cats.pop(nm, None)
            save_config(self.cats, CUSTOM_EXTS)
            self.populate_table()
            self.show_status(f"Removed '{nm}'")

    def choose_folder(self):
        # open folder dialog
        d = QFileDialog.getExistingDirectory(self,"Select Folder")
        if d:
            self.path.setText(d)

    def run_organizer(self):
        # perform file organization and optional cleanup
        d = self.path.text()
        if not d:
            return self.show_status("Choose folder first.", True)

        organize_folder(Path(d), self.cats, self.rec.isChecked())
        if self.rec.isChecked() and self.del_empty.isChecked():
            for sub in sorted(Path(d).rglob("*"), key=lambda p: len(str(p)), reverse=True):
                if sub.is_dir() and not any(sub.iterdir()):
                    sub.rmdir()
        self.show_status(f"Organized {Path(d).name}.")

    def load_preset(self, name):
        # load categories from selected preset
        if name in self.presets:
            self.cats = self.presets[name].copy()
            save_config(self.cats, CUSTOM_EXTS)
            self.populate_table()

    def add_preset(self):
        # create a brand-new preset with three empty, "All"-type categories
        default_name = datetime.now().strftime("Preset %Y-%m-%d %H-%M-%S")
        name, ok = QInputDialog.getText(self, "New Preset", "Preset name:", QLineEdit.Normal, default_name)
        if ok and name.strip():
            new_cats = {
                "Category 1": [],
                "Category 2": [],
                "Category 3": []
            }
            self.presets[name.strip()] = new_cats.copy()
            save_presets({k: v for k, v in self.presets.items() if k != "Default"})
            self.pcombo.addItem(name.strip())
            self.pcombo.setCurrentText(name.strip())
            self.cats = new_cats.copy()
            save_config(self.cats, CUSTOM_EXTS)
            self.populate_table()
            self.show_status(f"Added preset '{name.strip()}'")

    def rename_preset(self):
        # rename currently selected preset
        cur = self.pcombo.currentText()
        if cur == "Default":
            return self.show_status("Cannot rename Default.", True)
        new, ok = QInputDialog.getText(self, "Rename Preset", "New name:", QLineEdit.Normal, cur)
        if ok and new.strip() and new.strip() != cur:
            self.presets[new.strip()] = self.presets.pop(cur)
            save_presets({k: v for k, v in self.presets.items() if k != "Default"})
            idx = self.pcombo.currentIndex()
            self.pcombo.setItemText(idx, new.strip())
            self.pcombo.setCurrentText(new.strip())
            self.show_status(f"Renamed preset to '{new.strip()}'")

    def save_preset(self):
        # overwrite existing preset
        cur = self.pcombo.currentText()
        if cur == "Default":
            return self.show_status("Use 'Add Preset' to create.", True)
        self.presets[cur] = self.cats.copy()
        save_presets({k: v for k, v in self.presets.items() if k != "Default"})
        self.show_status(f"Saved preset '{cur}'")

    def delete_preset(self):
        # remove selected preset
        cur = self.pcombo.currentText()
        if cur == "Default":
            return
        self.presets.pop(cur, None)
        save_presets({k: v for k, v in self.presets.items() if k != "Default"})
        self.pcombo.clear()
        self.pcombo.addItems(self.presets.keys())
        self.load_preset("Default")
        self.show_status(f"Deleted preset '{cur}'")

    def add_extension(self):
        # prompt user to add a new extension to the "All" grid
        ext, ok = QInputDialog.getText(self, "Add Extension", "Extension (include leading '.'):",
                                       QLineEdit.Normal, "")
        if not ok:
            return
        ext = ext.strip().lower()
        if not ext.startswith("."):
            ext = "." + ext
        # don’t duplicate either in custom or in any built-in type
        if ext in CUSTOM_EXTS or any(ext in lst for lst in type_exts.values()):
            self.show_status(f"'{ext}' already exists.", True)
            return
        CUSTOM_EXTS.append(ext)
        # now save both cats and custom exts into categories.json
        save_config(self.cats, CUSTOM_EXTS)
        self.populate_table()
        self.show_status(f"Added extension '{ext}' to All.")

    def show_status(self, text, error=False):
        # display a temporary status message
        self.status.setText(text)
        color = "#f44336" if error else "#4caf50"
        self.status.setStyleSheet(f"color:{color};font-weight:bold;")
        QTimer.singleShot(3000, lambda: self.status.setText(""))

# --- ORGANIZATION LOGIC ---
def organize_folder(folder: Path, cats: dict, recursive: bool):
    # move files into folders based on extension categories
    files = folder.rglob("*") if recursive else folder.iterdir()
    for f in files:
        if not f.is_file():
            continue
        ext = f.suffix.lower()
        for cat, exts in cats.items():
            if ext in exts:
                dest = folder / cat
                dest.mkdir(exist_ok=True)
                shutil.move(str(f), str(dest / f.name))
                break
        else:
            oth = folder / "Others"
            oth.mkdir(exist_ok=True)
            shutil.move(str(f), str(oth / f.name))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
