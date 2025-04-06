from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFileDialog, QTabWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QStatusBar, QMessageBox, QMenu, QAction, QApplication,
                             QAbstractItemView, QSplitter, QMainWindow, QCheckBox)
from PyQt5.QtCore import Qt, QSettings
import os
from datetime import datetime
from DefineConst import *
from controller.xml_controller import XMLController
from model.history_model import HistoryModel
from view.editor_widget import XMLEditorWidget

class XMLExplorerView(QMainWindow):
    """Main view class for the XML Explorer application."""
    
    def __init__(self, controller):
        super().__init__()
        self.controller = XMLController(controller)
        self.history_model = HistoryModel()
        self.controller.set_view(self)
        self.results_data = {}  # Store references to result elements
        self.history_data = {}  # Store references to history items
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the user interface."""

        # Set window properties
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # File selection
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel(LABEL_XML_FILE))
        self.file_path_label = QLabel(LABEL_NO_FILE_SELECTED)
        self.file_path_edit = QLineEdit()
        file_layout.addWidget(self.file_path_edit)
        self.browse_button = QPushButton(BUTTON_BROWSE)
        self.browse_button.clicked.connect(self._browse_file)
        file_layout.addWidget(self.browse_button)
        main_layout.addLayout(file_layout)
        
        # Search
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel(LABEL_ELEMENT_TAG))
        self.tag_edit = QLineEdit()
        self.tag_edit.setPlaceholderText("Enter full or partial tag name (or leave empty to show all elements)")
        self.tag_edit.returnPressed.connect(self._on_key_pressed)
        self.tag_edit.textChanged.connect(self._text_changed)
        search_layout.addWidget(self.tag_edit, 1)
        self.search_button = QPushButton(BUTTON_SEARCH)
        self.search_button.clicked.connect(self._on_search_button_click)
        search_layout.addWidget(self.search_button)
        main_layout.addLayout(search_layout)

        self.partial_match_checkbox = QCheckBox("Partial tag matching")
        # self.partial_match_checkbox.setChecked(True)
        self.partial_match_checkbox.setToolTip("When checked, finds tags that contain the search text. When unchecked, requires exact tag matches.")
        self.partial_match_checkbox.stateChanged.connect(self._checkboxes_changed)
        main_layout.addWidget(self.partial_match_checkbox)
        
        # Search option
        main_layout.addWidget(QLabel(LABEL_SEARCH_ON))
        search_option_layout = QHBoxLayout()
        search_option_layout.setSpacing(0)

        self.validation_checkbox = []
        for column_name in RESULTS_COLUMNS:
            if column_name == 'XPath': continue # Skip Xpath field search
            search_checkbox = QCheckBox(column_name)
            search_checkbox.setToolTip("When checked, finds tags that contain the search text in " + f"{column_name}")
            search_checkbox.stateChanged.connect(self._checkboxes_changed)
            self.validation_checkbox.append(search_checkbox)
            search_option_layout.addWidget(search_checkbox,alignment=Qt.AlignLeft)

        # Add stretch to absorb extra space
        search_option_layout.addStretch(1)

        main_layout.addLayout(search_option_layout)

        # Create main splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter, 1)  # Make splitter take remaining space
        
        # Left side: Tab widget for results and history
        self._left_widget = QWidget()
        left_layout = QVBoxLayout(self._left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        left_layout.addWidget(self.tab_widget)
        
        # Results tab
        self._results_widget = QWidget()
        results_layout = QVBoxLayout(self._results_widget)
        
        self.results_table = QTableWidget()
        self.results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.results_table.setColumnCount(len(RESULTS_COLUMNS))
        self.results_table.setHorizontalHeaderLabels(RESULTS_COLUMNS)
        self.results_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self._show_results_context_menu)
        self.results_table.itemDoubleClicked.connect(self._handle_result_double_click)

        # Set column stretching
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)    # Element Name
        header.setSectionResizeMode(1, QHeaderView.Interactive)         # Value
        header.setSectionResizeMode(2, QHeaderView.Interactive)         # Attributes
        header.setSectionResizeMode(3, QHeaderView.Stretch)             # XPath
        
        # Setup context menu
        self.results_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self._show_results_context_menu)
        
        results_layout.addWidget(self.results_table)
        self.tab_widget.addTab(self._results_widget, TAB_RESULTS)
        
        # History tab
        self._history_widget = QWidget()
        history_layout = QVBoxLayout(self._history_widget)

        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(len(HISTORY_COLUMNS))
        self.history_table.setHorizontalHeaderLabels(HISTORY_COLUMNS)
        # Setup context menu
        self.history_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.history_table.customContextMenuRequested.connect(self._show_history_context_menu)
        # Double click to load history item
        self.history_table.cellDoubleClicked.connect(self._handle_history_double_click)
        
        # History buttons
        history_button_layout = QHBoxLayout()
        self.clear_history_button = QPushButton(BUTTON_CLEAR_ALL)
        self.clear_history_button.clicked.connect(self._clear_history)
        history_button_layout.addWidget(self.clear_history_button)

        self.export_csv_button = QPushButton("Export CSV")
        self.import_csv_button = QPushButton("Import CSV")
        self.export_csv_button.clicked.connect(self._export_csv)
        self.import_csv_button.clicked.connect(self._import_csv)
        history_button_layout.addWidget(self.export_csv_button)
        history_button_layout.addWidget(self.import_csv_button)

        history_button_layout.addStretch()
        history_layout.addLayout(history_button_layout)
        history_layout.addWidget(self.history_table)

        self.tab_widget.addTab(self._history_widget, TAB_HISTORY)
        
        # Set column stretching
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)    # Date & Time
        header.setSectionResizeMode(1, QHeaderView.Interactive)         # Tag Name
        header.setSectionResizeMode(2, QHeaderView.Interactive)         # File Path
        header.setSectionResizeMode(3, QHeaderView.Stretch)    # P
        header.setSectionResizeMode(4, QHeaderView.Stretch)    # N
        header.setSectionResizeMode(5, QHeaderView.Stretch)    # A
        header.setSectionResizeMode(6, QHeaderView.Stretch)    # V
        header.setSectionResizeMode(7, QHeaderView.Stretch)    # Results
        
        # Right side: Editor widget with header and controls
        self._right_widget = QWidget()
        right_layout = QVBoxLayout(self._right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Editor header with title and controls
        editor_header = QHBoxLayout()
        editor_header.addWidget(QLabel("<b>XML Editor</b>"))
        
        # Add refresh button to reload the editor content
        self.refresh_editor_button = QPushButton("Refresh")
        self.refresh_editor_button.setToolTip("Reload the XML content from file")
        self.refresh_editor_button.clicked.connect(self._refresh_editor)
        editor_header.addWidget(self.refresh_editor_button)
        
        right_layout.addLayout(editor_header)
        
        # Create and add editor widget
        self.editor_widget = XMLEditorWidget()
        self.editor_widget.fileSaved.connect(self._handle_file_saved)
        right_layout.addWidget(self.editor_widget)
        
        # Add both sides to the splitter
        self.main_splitter.addWidget(self._left_widget)
        self.main_splitter.addWidget(self._right_widget)
        
        # Set initial sizes for the splitter (50/50 split)
        self.main_splitter.setSizes([600, 600])

        # Status bar
        self.status_bar = QStatusBar()
        main_layout.addWidget(self.status_bar)
        self.status_bar.showMessage(STATUS_READY)
        
        # View menu for layout options
        self.view_menu = self.menuBar().addMenu("View Menu")
        
        # Actions for different layouts
        equal_split_action = QAction(SPLIT_OPTION_EQUAL, self)
        equal_split_action.triggered.connect(self._set_equal_split)
        self.view_menu.addAction(equal_split_action)
        
        expand_editor_action = QAction(SPLIT_OPTION_EDITOR, self)
        expand_editor_action.triggered.connect(self._expand_editor)
        self.view_menu.addAction(expand_editor_action)
        
        expand_results_action = QAction(SPLIT_OPTION_RESULT, self)
        expand_results_action.triggered.connect(self._expand_results)
        self.view_menu.addAction(expand_results_action)

        # Load history
        self._load_history()
    
    def _add_current_entry(self):
        entry = {'timestamp': datetime.now().strftime(TIMESTAMP_FORMAT),
            'tag_name': self.tag_edit.text(),
            'file_path': self.file_path_edit.text(),
            'partial_flag': 1 if self.partial_match_checkbox.isChecked() else 0,
            'name_flag': 1 if self.validation_checkbox[0].isChecked() else 0,
            'att_flag': 1 if self.validation_checkbox[1].isChecked() else 0,
            'value_flag': 1 if self.validation_checkbox[2].isChecked() else 0,
            'result_count': self.results_table.rowCount()
        }
        self.history_model.add_entry(entry)
    def _on_key_pressed(self):
        self._add_current_entry()
        self._search_tag()

    def _on_search_button_click(self):
        self._add_current_entry()
        self._search_tag()

    def _on_tab_changed(self):
        current_tab = self.tab_widget.currentIndex()
        if current_tab == self.tab_widget.indexOf(self._results_widget):
            ""
        elif current_tab == self.tab_widget.indexOf(self._history_widget):
            self._expand_results()
        else:
            # Other tab is selected, do nothing
            pass

    def _checkboxes_changed(self):
        try:
            self._search_tag(flag_ignore_error=True)
        except Exception: pass

    def _export_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export CSV", HISTORY_FILE_PATH, "CSV Files (*.csv)")
        if file_path:
            success, message = self.history_model.export_history(file_path)
            QMessageBox.information(self, "Export CSV", message)

    def _import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import CSV", HISTORY_FILE_PATH, "CSV Files (*.csv)")
        if file_path:
            success, result = self.history_model.import_history(file_path)
            if success:
                QMessageBox.information(self, "Import CSV", "Import successful")
                self._load_history()
                # self._refresh_editor()
            else:
                QMessageBox.critical(self, "Import CSV", result)


    def _refresh_editor(self):
        """Refresh the editor by reloading the current file."""
        current_file = self.controller.get_current_file_path()
        if current_file:
            if self.editor_widget.is_modified:
                reply = QMessageBox.question(
                    self,
                    "Unsaved Changes",
                    "The editor has unsaved changes. Do you want to discard them and reload?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
                    
            success, error = self.controller.load_xml_file(current_file)
            if success:
                self.file_path_label.setText(os.path.basename(current_file))
                self.status_bar.showMessage(STATUS_FILE_LOADED.format(file=os.path.basename(current_file)))
                
                # Also load the file in the editor
                if self.editor_widget.load_file(current_file):
                    self.status_bar.showMessage("Editor content refreshed.")
                else:
                    self.show_error("Failed to refresh editor content.")

                self.tag_edit.setFocus()

                # Show all tag
                self._search_tag()
            else:
                self.show_error(error)
        else:
            self.status_bar.showMessage("No file is currently loaded.")

    def _set_equal_split(self):
        """Set equal sizes for splitter."""
        width = self.main_splitter.width()
        self.main_splitter.setSizes([width//2, width//2])
        self.view_menu.setTitle(SPLIT_OPTION_EQUAL)
        self.status_bar.showMessage("Set equal split view.")

    def _expand_editor(self):
        """Give more space to the editor."""
        width = self.main_splitter.width()
        self.main_splitter.setSizes([width//3, 2*width//3])
        self.view_menu.setTitle(SPLIT_OPTION_EDITOR + f" ({width//3}/{2*width//3})")
        self.status_bar.showMessage("Expanded editor panel.")

    def _expand_results(self):
        """Give more space to the results panel."""
        width = self.main_splitter.width()
        self.main_splitter.setSizes([2*width//3, width//3])
        self.view_menu.setTitle(SPLIT_OPTION_RESULT + f" ({2*width//3}/{width//3})")
        self.status_bar.showMessage("Expanded results panel.")

    def _handle_file_saved(self, file_path):
        """Handle file saved event from the editor."""
        # Reload the XML file in the model if it's the currently loaded file
        if file_path == self.controller.get_current_file_path():
            success, error = self.controller.reload_xml_file()
            if success:
                self.status_bar.showMessage("XML file saved and reloaded successfully.")
            else:
                self.show_error(f"Error reloading XML file: {error}")

    def save_state(self):
        """Save application state to settings."""
        # Save the splitter sizes
        if hasattr(self, 'main_splitter'):
            settings = QSettings("XMLExplorer", "XMLExplorer")
            settings.setValue("splitter_sizes", self.main_splitter.saveState())
            settings.setValue("window_geometry", self.saveGeometry())
            settings.setValue("window_state", self.saveState())

    def restore_state(self):
        """Restore application state from settings."""
        settings = QSettings("XMLExplorer", "XMLExplorer")
        
        # Restore splitter state if available
        if hasattr(self, 'main_splitter'):
            splitter_state = settings.value("splitter_sizes")
            if splitter_state:
                self.main_splitter.restoreState(splitter_state)
        
        # Restore window geometry and state
        geometry = settings.value("window_geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        state = settings.value("window_state")
        if state:
            self.restoreState(state)

    def closeEvent(self, event):
        """Handle window close event."""
        # Check if there are unsaved changes in the editor
        if hasattr(self, 'editor_widget') and self.editor_widget.is_modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "The document has been modified. Do you want to save changes?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            
            if reply == QMessageBox.Save:
                if not self.editor_widget.save_file():
                    event.ignore()  # Cancel closing if save failed
                    return
            elif reply == QMessageBox.Cancel:
                event.ignore()  # Cancel closing
                return
        
         # Save application state
        self.save_state()

        # Proceed with normal closing
        event.accept()

    def _handle_file_saved(self, file_path):
        """Handle file saved event from the editor."""
        # Reload the XML file in the model if it's the currently loaded file
        if file_path == self.controller.get_current_file_path():
            success, error = self.controller.reload_xml_file()
            if success:
                self.status_bar.showMessage(EDITOR_STATUS_SAVED)
            else:
                self.show_error(f"{EDITOR_STATUS_ERROR.format(message=error)}")

    def _browse_file(self):
        """Open file dialog to select an XML file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open XML File",
            "",
            "XML Files (*.xml);;All Files (*)"
        )
        
        if file_path:
            # Check for unsaved changes
            if hasattr(self, 'editor_widget') and self.editor_widget.is_modified:
                reply = QMessageBox.question(
                    self,
                    "Unsaved Changes",
                    "The editor has unsaved changes. Do you want to discard them?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
            self.file_path_edit.setText(file_path)
            success, error = self.controller.load_xml_file(file_path)
            
            if success:
                self.file_path_label.setText(os.path.basename(file_path))
                self.status_bar.showMessage(STATUS_FILE_LOADED.format(file=os.path.basename(file_path)))
                
                # Also load the file in the editor
                self.editor_widget.load_file(file_path)
                self.editor_widget.format_xml()
                self.editor_widget.save_file()

                self.tag_edit.setFocus()

                # Show all tag
                self._search_tag()
            else:
                self.show_error(error)
    
    def _text_changed(self):
        """"""
        print(self.tag_edit.text())
        self._search_tag()

    def _search_tag(self, flag_ignore_error=False):
        """Search for elements with the specified tag name or all elements if empty."""
        # self.tag_edit.setText(self.search_layout.item(0, 0).text())
        tag_name = self.tag_edit.text().strip()
        
        # If tag_name is empty, show all elements
        if not tag_name and SEARCH_EMPTY_SHOWS_ALL:
            tag_name = SEARCH_ALL_ELEMENTS
        # Check if it's a "show all elements" request with "*"    
        elif tag_name == "*" and SHOW_ALL_ELEMENTS_ENABLED:
            tag_name = SEARCH_ALL_ELEMENTS
        
        partial_match = self.partial_match_checkbox.isChecked() if hasattr(self, 'partial_match_checkbox') else True
        name_tag_checkbox = self.validation_checkbox[0].isChecked()
        att_tag_checkbox = self.validation_checkbox[1].isChecked()
        value_tag_checkbox = self.validation_checkbox[2].isChecked()
        success, results, error = self.controller.search_tag(tag_name,
                                                             flag_name = name_tag_checkbox,
                                                             flag_att = att_tag_checkbox,
                                                             flag_value = value_tag_checkbox,
                                                             partial_flag = partial_match)
        
        if not success and not flag_ignore_error:
            self.show_error(error)
            return
        
        if (results != None):
            if not tag_name and SEARCH_EMPTY_SHOWS_ALL:
                self.status_bar.showMessage("Showing all XML elements...")
            self.display_results(results)
        
        # Refresh history
        self._load_history()
    
    def display_results(self, results):
        """
        Display search results in the table.
        
        Args:
            results: List of element information dictionaries
        """
        # Clear previous results
        self.results_table.setRowCount(0)
        self.results_data = {}
        
        # Add rows
        for i, element in enumerate(results):
            row_position = self.results_table.rowCount()
            self.results_table.insertRow(row_position)
            
            # Store reference to the element data
            self.results_data[row_position] = element
            
            # Set data
            self.results_table.setItem(row_position, 0, QTableWidgetItem(element['name']))
            # Format attributes as 'att1=value1;att2=value2;...'
            attributes = element.get('attributes', {})
            if attributes:
                attr_text = ";".join([f"{k}={v}" for k, v in attributes.items()])
            else:
                attr_text = ""
            
            self.results_table.setItem(row_position, 1, QTableWidgetItem(attr_text))
            self.results_table.setItem(row_position, 2, QTableWidgetItem(element['value']))
            self.results_table.setItem(row_position, 3, QTableWidgetItem(element['xpath']))
        
        # Update status
        plural = "elements" if len(results) != 1 else "element"
        self.status_bar.showMessage(STATUS_RESULTS_FOUND.format(count=len(results), plural=plural))

    def _load_history(self):
        """Load and display search history."""
        # Get history items
        history_items = self.history_model.get_history()
        
        # Clear previous items
        self.history_table.setRowCount(0)
        self.history_data = {}
        
        # Add rows
        for i, item in enumerate(history_items):
            row_position = self.history_table.rowCount()
            self.history_table.insertRow(row_position)
            
            # Store reference to the history item
            self.history_data[row_position] = item
            
            # Set data
            self.history_table.setItem(row_position, 0, QTableWidgetItem(item['timestamp']))
            self.history_table.setItem(row_position, 1, QTableWidgetItem(item['tag_name']))
            
            # Shorten file path for display
            file_path = item['file_path']
            display_path = os.path.basename(file_path)
            file_item = QTableWidgetItem(display_path)
            file_item.setToolTip(file_path)  # Show full path on hover
            self.history_table.setItem(row_position, 2, file_item)

            self.history_table.setItem(row_position, 3, QTableWidgetItem(item['partial_flag']))
            self.history_table.setItem(row_position, 4, QTableWidgetItem(item['name_flag']))
            self.history_table.setItem(row_position, 5, QTableWidgetItem(item['att_flag']))
            self.history_table.setItem(row_position, 6, QTableWidgetItem(item['value_flag']))
            
            # Results count
            count = str(item['result_count'])
            plural = "elements" if item['result_count'] != 1 else "element"
            self.history_table.setItem(row_position, 7, QTableWidgetItem(f"{count} {plural}"))
    
    def _clear_history(self):
        """Clear all search history."""
        # Confirm with user
        confirm = QMessageBox.question(
            self,
            "Clear History",
            CONFIRM_CLEAR_HISTORY,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            success = self.history_model.clear_history()
            if success:
                self._load_history()
                self.status_bar.showMessage(STATUS_HISTORY_CLEARED)
    
    def _show_results_context_menu(self, position):
        """Show context menu for results table."""
        menu = QMenu(self)
        
        copy_element_action = QAction(MENU_COPY_ELEMENT, self)
        copy_value_action = QAction(MENU_COPY_VALUE, self)
        copy_xpath_action = QAction(MENU_COPY_XPATH, self)
        copy_attr_action = QAction(MENU_COPY_ATT, self)
        open_in_xml_action = QAction(MENU_OPEN_XML, self)
        
        menu.addAction(copy_element_action)
        menu.addAction(copy_value_action)
        menu.addAction(copy_xpath_action)
        menu.addAction(copy_attr_action)
        menu.addSeparator()
        menu.addAction(open_in_xml_action)
        
        # Connect actions - ensure correct column indices
        copy_element_action.triggered.connect(lambda: self._copy_column_value(0))   # Element is column 1
        copy_attr_action.triggered.connect(lambda: self._copy_column_value(1))      # Attributes is column 2
        copy_value_action.triggered.connect(lambda: self._copy_column_value(2))     # Value is column 3
        copy_xpath_action.triggered.connect(lambda: self._copy_column_value(7))     # XPath is column 4
        open_in_xml_action.triggered.connect(self._open_in_xml)
        
        # Show menu
        menu.exec_(self.results_table.mapToGlobal(position))

    def _show_history_context_menu(self, position):
        """Show context menu for history table."""
        menu = QMenu(self)
        
        load_search_action = QAction(MENU_LOAD_SEARCH, self)
        remove_entry_action = QAction(MENU_REMOVE_ENTRY, self)
        
        menu.addAction(load_search_action)
        menu.addAction(remove_entry_action)
        
        # Connect actions
        load_search_action.triggered.connect(self._load_history_search)
        remove_entry_action.triggered.connect(self._remove_history_entry)
        
        # Show menu
        menu.exec_(self.history_table.mapToGlobal(position))
    
    def _copy_column_value(self, column_index):
        """
        Copy the value of the specified column to clipboard.
        
        Args:
            column_index: Index of the column
        """
        
        selected_rows = self.results_table.selectionModel().selectedRows()
        if not selected_rows:
            # If no rows are selected, use the current item
            current_row = self.results_table.currentRow()
            if current_row >= 0:
                selected_rows = [self.results_table.model().index(current_row, 0)]
        
        if selected_rows:
            row = selected_rows[0].row()
            item = self.results_table.item(row, column_index)
            if item:
                clipboard = QApplication.clipboard()
                clipboard.setText(item.text())
                
                # Update status
                column_name = self.results_table.horizontalHeaderItem(column_index).text()
                self.status_bar.showMessage(STATUS_COPIED.format(text=f"{column_name}: {item.text()}"))
    
    def _open_in_xml(self):
        """Open the XML file at the selected element's position."""
        self._right_widget.setFocus()
        
        selected_rows = self.results_table.selectionModel().selectedRows()
        if not selected_rows:
            # If no rows are selected, use the current item
            current_row = self.results_table.currentRow()
            if current_row >= 0:
                selected_rows = [self.results_table.model().index(current_row, 0)]
        
        if selected_rows:
            row = selected_rows[0].row()
            if row in self.results_data:
                element_info = self.results_data[row]
                
                # Get the current file path
                file_path = self.controller.get_current_file_path()
                
                # Check if we need to prompt to save changes in the editor
                if self.editor_widget.is_modified:
                    if not self.editor_widget.close_editor():
                        return  # User cancelled
                
                # Load the file in the editor
                if self.editor_widget.load_file(file_path):
                    # Navigate to the element
                    self.editor_widget.navigate_to_element(element_info)
                    self.editor_widget.setFocus()
                    self.status_bar.showMessage(EDITOR_STATUS_LOADED)
                else:
                    self.show_error(f"{EDITOR_STATUS_ERROR.format(message='Failed to open file in editor')}")
    
    def _load_history_search(self):
        """Load a search from history."""
        selected_rows = self.history_table.selectionModel().selectedRows()
        if not selected_rows:
            # If no rows are selected, use the current item
            current_row = self.history_table.currentRow()
            if current_row >= 0:
                selected_rows = [self.history_table.model().index(current_row, 0)]
        
        if selected_rows:
            row = selected_rows[0].row()
            if row in self.history_data:
                item = self.history_data[row]
                
                # Set file path and load XML
                self.file_path_edit.setText(item['file_path'])
                success, error = self.controller.load_xml_file(item['file_path'])
                
                if not success:
                    self.show_error(error)
                    return
                
                # Set tag and search
                self.tag_edit.setText(item['tag_name'])
                self._search_tag()
                
                # Switch to results tab
                self.tab_widget.setCurrentIndex(0)
                self.partial_match_checkbox.setChecked(item['partial_flag'])
                self.validation_checkbox[0].setChecked(item['name_flag'])
                self.validation_checkbox[1].setChecked(item['att_flag'])
                self.validation_checkbox[2].setChecked(item['value_flag'])
    
    def _remove_history_entry(self):
        """Remove the selected history entry."""
        selected_rows = self.history_table.selectionModel().selectedRows()
        if not selected_rows:
            # If no rows are selected, use the current item
            current_row = self.history_table.currentRow()
            if current_row >= 0:
                selected_rows = [self.history_table.model().index(current_row, 0)]
        
        if selected_rows:
            row = selected_rows[0].row()
            if row in self.history_data:
                item = self.history_data[row]
                
                # Confirm with user
                confirm = QMessageBox.question(
                    self,
                    "Remove Entry",
                    CONFIRM_REMOVE_ENTRY,
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if confirm == QMessageBox.Yes:
                    success = self.controller.remove_history_item(
                        item['timestamp'],
                        item['tag_name'],
                        item['file_path']
                    )
                    
                    if success:
                        self._load_history()
    
    def _handle_result_double_click(self, item):
        """Handle double-click on results table item."""
        # Open the file in the integrated editor
        self._open_in_xml()
    
    def _handle_history_double_click(self, row, column):
        """
        Handle double-click on history row.
        
        Args:
            row: Row index
            column: Column index
        """
        # Load this history search
        if row in self.history_data:
            item = self.history_data[row]
            
            # Set file path and load XML
            self.file_path_edit.setText(item['file_path'])
            success, error = self.controller.load_xml_file(item['file_path'])
            
            if not success:
                self.show_error(error)
                return
            
            # Set tag and search
            self.tag_edit.setText(item['tag_name'])
            self._search_tag()

            self.partial_match_checkbox.setChecked(True if item['partial_flag']=='1' else False)
            self.validation_checkbox[0].setChecked(True if item['name_flag']=='1' else False)
            self.validation_checkbox[1].setChecked(True if item['att_flag']=='1' else False)
            self.validation_checkbox[2].setChecked(True if item['value_flag']=='1' else False)
            
            # Switch to results tab
            self.tab_widget.setCurrentIndex(0)
    
    def update_status(self, message):
        """
        Update the status bar message.
        
        Args:
            message: Status message to display
        """
        self.status_bar.showMessage(message)
    
    def show_error(self, message):
        """
        Display an error message dialog.
        
        Args:
            message: Error message to display
        """
        QMessageBox.critical(self, "Error", message)