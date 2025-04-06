from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPlainTextEdit, 
                             QHBoxLayout, QLabel, 
                             QFileDialog, QInputDialog, QMessageBox,
                             QAction, QToolBar)
from PyQt5.QtGui import (QFont, QTextCursor, QColor, QTextCharFormat,
                         QSyntaxHighlighter)
from PyQt5.QtCore import Qt, QRegExp, pyqtSignal
import os
import xml.dom.minidom as minidom
from DefineConst import *

class XMLSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for XML content."""
    
    def __init__(self, document):
        super().__init__(document)
        
        self.highlighting_rules = []
        
        # XML tags
        tag_format = QTextCharFormat()
        tag_format.setForeground(QColor("#0000FF"))  # Blue
        tag_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((QRegExp("<[/]?[a-zA-Z0-9_:]+[^>]*>"), tag_format))
        
        # XML attributes
        attribute_format = QTextCharFormat()
        attribute_format.setForeground(QColor("#FF00FF"))  # Purple
        self.highlighting_rules.append((QRegExp("\\b[a-zA-Z0-9_:]+(?==)"), attribute_format))
        
        # XML attribute values
        value_format = QTextCharFormat()
        value_format.setForeground(QColor("#008000"))  # Green
        self.highlighting_rules.append((QRegExp("\"[^\"]*\"|'[^']*'"), value_format))
        
        # XML comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#808080"))  # Gray
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((QRegExp("<!--[^-]*-->"), comment_format))
        
        # XML declarations
        declaration_format = QTextCharFormat()
        declaration_format.setForeground(QColor("#800000"))  # Maroon
        declaration_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((QRegExp("<\\?[^?]*\\?>"), declaration_format))
    
    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text."""
        for pattern, format in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)


class XMLEditorWidget(QWidget):
    """Widget for editing XML content."""
    
    # Define signals
    fileSaved = pyqtSignal(str)  # Signal emitted when file is saved
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.current_file = None
        self.is_modified = False
        self.search_text = ""
        self.last_search_position = 0
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the editor UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        toolbar = QToolBar()
        
        # Save action
        self.save_action = QAction("Save", self)
        self.save_action.setShortcut(SHORTCUT_SAVE)
        self.save_action.triggered.connect(self.save_file)
        toolbar.addAction(self.save_action)
        
        # Save As action
        self.save_as_action = QAction("Save As...", self)
        self.save_as_action.triggered.connect(self.save_file_as)
        toolbar.addAction(self.save_as_action)
        
        toolbar.addSeparator()
        
        # Format XML action
        self.format_action = QAction("Format XML", self)
        self.format_action.triggered.connect(self.format_xml)
        toolbar.addAction(self.format_action)
        
        toolbar.addSeparator()
        
        # Find action
        self.find_action = QAction("Find", self)
        self.find_action.setShortcut(SHORTCUT_FIND)
        self.find_action.triggered.connect(self.show_find_dialog)
        toolbar.addAction(self.find_action)
        
        # Find Next action
        self.find_next_action = QAction("Find Next", self)
        self.find_next_action.setShortcut(SHORTCUT_FIND_NEXT)
        self.find_next_action.triggered.connect(self.find_next)
        toolbar.addAction(self.find_next_action)
        
        # Go to Line action
        self.goto_action = QAction("Go to Line", self)
        self.goto_action.setShortcut(SHORTCUT_GO_TO_LINE)
        self.goto_action.triggered.connect(self.show_goto_dialog)
        toolbar.addAction(self.goto_action)
        
        layout.addWidget(toolbar)
        
        # File info bar
        self.info_layout = QHBoxLayout()
        self.file_label = QLabel("No file loaded")
        self.info_layout.addWidget(self.file_label)
        
        self.line_col_label = QLabel("Line: 1, Col: 1")
        self.info_layout.addWidget(self.line_col_label, alignment=Qt.AlignRight)
        
        layout.addLayout(self.info_layout)
        
        # Text editor
        self.editor = QPlainTextEdit()
        self.editor.setFont(QFont("Courier New", 10))
        self.editor.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.editor.textChanged.connect(self._text_changed)
        self.editor.cursorPositionChanged.connect(self._cursor_position_changed)
        layout.addWidget(self.editor)
        
        # Apply syntax highlighting
        self.highlighter = XMLSyntaxHighlighter(self.editor.document())
    
    def load_file(self, file_path):
        """Load XML content from file."""
        if not file_path or not os.path.exists(file_path):
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            self.editor.setPlainText(content)
            self.current_file = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.is_modified = False
            self._update_window_title()
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading file: {str(e)}")
            return False
    
    def navigate_to_element(self, element_info):
        """Navigate to a specific element in the XML document."""
        if not self.current_file:
            return False

        # Find the element in the text by its XPath
        if 'xpath' in element_info:
            # Simple implementation - search for the element's opening tag
            tag_name = element_info['name']
            attributes = element_info['attributes']
            attributes_text = ''
            if attributes:
                for key, value in attributes.items():
                    attributes_text += f' {key}="{value}"'
            search_text = f"<{tag_name}{attributes_text}"
            
            # Reset search position to start of document
            self.editor.moveCursor(QTextCursor.Start)
            
            # Search for the tag
            found = self.editor.find(search_text)
            
            if found:
                # Select the entire element if possible
                cursor = self.editor.textCursor()
                pos = cursor.position()
                
                # Try to find the matching closing tag or end of self-closing tag
                text = self.editor.toPlainText()
                
                # Simple heuristic - not perfect but works for most cases
                # This would ideally use actual XML parsing for precision
                open_tags = 1
                start_pos = pos
                i = pos
                
                # Look for matching end tag or self-closing tag
                while i < len(text) and open_tags > 0:
                    if text[i:i+2] == "/>":  # Self-closing tag
                        i += 2
                        open_tags = 0
                        break
                    elif text[i:i+2] == "</":  # Closing tag
                        open_tags -= 1
                        i += 2
                    elif text[i:i+1] == "<" and text[i:i+2] != "</":  # Opening tag
                        open_tags += 1
                        i += 1
                    else:
                        i += 1
                
                if open_tags == 0:
                    # Found the entire element
                    cursor.setPosition(start_pos)
                    cursor.setPosition(i, QTextCursor.KeepAnchor)
                    self.editor.setTextCursor(cursor)
                
                # Center the view on the found text
                self.editor.centerCursor()
                return True
        
        return False
    
    def save_file(self):
        """Save the current file."""
        if not self.current_file:
            return self.save_file_as()
        
        try:
            with open(self.current_file, 'w', encoding='utf-8') as file:
                file.write(self.editor.toPlainText())
            
            self.is_modified = False
            self._update_window_title()
            self.fileSaved.emit(self.current_file)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving file: {str(e)}")
            return False
    
    def save_file_as(self):
        """Save the current file with a new name."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save XML File",
            self.current_file if self.current_file else "",
            "XML Files (*.xml);;All Files (*)"
        )
        
        if file_path:
            self.current_file = file_path
            self.file_label.setText(os.path.basename(file_path))
            return self.save_file()
        
        return False
    
    def format_xml(self):
        """Format the XML content with proper indentation."""
        try:
            # Get the current text
            xml_text = self.editor.toPlainText()
            
            # Parse and format the XML
            dom = minidom.parseString(xml_text)
            pretty_xml = dom.toprettyxml(indent="  ")
            
            # Remove extra blank lines (common issue with minidom)
            pretty_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])
            
            # Set the formatted text
            cursor_position = self.editor.textCursor().position()
            self.editor.setPlainText(pretty_xml)
            
            # Try to restore cursor position approximately
            cursor = self.editor.textCursor()
            cursor.setPosition(min(cursor_position, len(pretty_xml)))
            self.editor.setTextCursor(cursor)
            
        except Exception as e:
            QMessageBox.warning(self, "Format Error", f"Could not format XML: {str(e)}")
    
    def show_find_dialog(self):
        """Show dialog to find text in the document."""
        text, ok = QInputDialog.getText(
            self, 
            "Find Text", 
            "Enter text to find:",
            text=self.search_text
        )
        
        if ok and text:
            self.search_text = text
            self.last_search_position = 0  # Reset search position
            self.find_next()
    
    def find_next(self):
        """Find the next occurrence of the search text."""
        if not self.search_text:
            self.show_find_dialog()
            return
        
        # Start from current position or last search position
        cursor = self.editor.textCursor()
        current_pos = cursor.position()
        
        # If we're at the same position as last time, move forward to avoid finding the same text
        if current_pos == self.last_search_position and current_pos < len(self.editor.toPlainText()):
            cursor.setPosition(current_pos + 1)
            self.editor.setTextCursor(cursor)
        
        # Search for the text
        found = self.editor.find(self.search_text)
        
        if found:
            self.last_search_position = self.editor.textCursor().position()
            self.editor.centerCursor()
        else:
            # If not found, wrap around to the beginning
            cursor.setPosition(0)
            self.editor.setTextCursor(cursor)
            
            found = self.editor.find(self.search_text)
            if found:
                self.last_search_position = self.editor.textCursor().position()
                self.editor.centerCursor()
                QMessageBox.information(self, "Find", "Search wrapped to beginning of document.")
            else:
                QMessageBox.information(self, "Find", f"Text '{self.search_text}' not found.")
    
    def show_goto_dialog(self):
        """Show dialog to go to a specific line."""
        line, ok = QInputDialog.getInt(
            self,
            "Go to Line",
            "Enter line number:",
            1,
            1,
            self.editor.document().blockCount()
        )
        
        if ok:
            self._goto_line(line)
    
    def _goto_line(self, line_number):
        """Go to the specified line number."""
        # Ensure line number is within bounds
        line_number = max(1, min(line_number, self.editor.document().blockCount()))
        
        # Create a cursor at the start of the specified line
        cursor = QTextCursor(self.editor.document().findBlockByLineNumber(line_number - 1))
        self.editor.setTextCursor(cursor)
        self.editor.centerCursor()
    
    def _text_changed(self):
        """Handle text changes in the editor."""
        if not self.is_modified:
            self.is_modified = True
            self._update_window_title()
    
    def _cursor_position_changed(self):
        """Update line and column information when cursor position changes."""
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        self.line_col_label.setText(f"Line: {line}, Col: {column}")
    
    def _update_window_title(self):
        """Update the window title to show modified indicator."""
        if self.current_file:
            filename = os.path.basename(self.current_file)
            modified_indicator = EDITOR_MODIFIED_INDICATOR if self.is_modified else ""
            self.file_label.setText(f"{filename}{modified_indicator}")
    
    def close_editor(self):
        """Handle editor closing with unsaved changes."""
        if self.is_modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "The document has been modified. Do you want to save changes?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            
            if reply == QMessageBox.Save:
                return self.save_file()
            elif reply == QMessageBox.Cancel:
                return False
        
        return True