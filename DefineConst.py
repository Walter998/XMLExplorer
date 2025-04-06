"""
Constants definitions for the XML Explorer application.
This file centralizes all constants used throughout the application.
"""
import os

SEARCH_EMPTY_SHOWS_ALL = True  # When tag name is empty, show all elements
# Search behavior
SEARCH_PARTIAL_MATCH_ENABLED = True  # Enable partial tag matching by default

CHECKBOX_PARTIAL_SEARCH = "Partial search"

EDITOR_OPEN_DELAY = 1.5
SEARCH_DIALOG_DELAY = 1

# Split screen option
SPLIT_OPTION_EQUAL = "Equal Split"
SPLIT_OPTION_RESULT = "Expand Results"
SPLIT_OPTION_EDITOR = "Expand Editor"

# Editor constants
EDITOR_TAB_TITLE = "Editor"
EDITOR_STATUS_LOADING = "Loading XML content..."
EDITOR_STATUS_LOADED = "XML content loaded successfully"
EDITOR_STATUS_SAVED = "XML file saved successfully"
EDITOR_STATUS_ERROR = "Error: {message}"
EDITOR_MODIFIED_INDICATOR = "*"

# Status messages
STATUS_FILE_LOADED = "XML file '{file}' loaded successfully"

HISTORY_FILE_PATH = f"{os.getcwd()}\\history_record.csv"

# Editor menu items
MENU_SAVE = "Save"
MENU_SAVE_AS = "Save As..."
MENU_FORMAT_XML = "Format XML"
MENU_HIGHLIGHT_ELEMENT = "Highlight Selected Element"
MENU_FIND = "Find..."
MENU_FIND_NEXT = "Find Next"
MENU_GO_TO_LINE = "Go to Line..."

# Key shortcuts
SHORTCUT_SAVE = "Ctrl+S"
SHORTCUT_FIND = "Ctrl+F"
SHORTCUT_FIND_NEXT = "F3"
SHORTCUT_GO_TO_LINE = "Ctrl+G"

# Menu items
MENU_COPY_ATTRIBUTES = "Copy Attributes"

# Status messages
STATUS_COPIED_ATTRIBUTES = "Attributes copied to clipboard"

# Application settings
APP_NAME = "XML Explorer"
APP_VERSION = "1.0.0"

# Window settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
WINDOW_TITLE = APP_NAME

# Table settings
RESULTS_COLUMNS = ["Element Name", "Attributes", "Value", "XPath"]
HISTORY_COLUMNS = ["Date & Time", "Search value", "File Name", "P", "N", "A", "V", "Results"]

# XPath settings
XPATH_DEFAULT_ROOT = "/"

# Date and time format
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

# Show all elements feature
SHOW_ALL_ELEMENTS_ENABLED = True
SEARCH_ALL_ELEMENTS = "*"  # Special marker for "search all elements"

# Status messages
STATUS_READY = "Ready"
STATUS_SEARCHING = "Searching for <{tag}> tags..."
STATUS_SEARCHING_ALL = "Searching for all XML elements..."
STATUS_RESULTS_FOUND = "Found {count} {plural} matching the search criteria"
STATUS_ALL_ELEMENTS_FOUND = "Found {count} elements in the XML file"
STATUS_COPIED = "Copied to clipboard: {text}"
STATUS_HISTORY_CLEARED = "Search history cleared"
STATUS_ERROR_PREFIX = "Error: "
STATUS_SEARCHING_EMPTY = "Searching for all XML elements (empty tag)..."
STATUS_EMPTY_TAG_RESULTS = "Showing all {count} elements in the XML file"

# Error messages
ERROR_NO_FILE = "Please select an XML file."
ERROR_NO_TAG = "Please enter a tag name to search for or enable 'Show all elements' in settings."
ERROR_FILE_NOT_FOUND = "File not found: {file}"
ERROR_NOT_XML = "Not a valid XML file: {file}"
ERROR_PARSING_XML = "XML parsing error: {error}"
ERROR_LOADING_XML = "Error loading XML file: {error}"
ERROR_SEARCHING = "Error searching for tag: {error}"
ERROR_NO_XML_LOADED = "No XML file loaded"

# Confirmation messages
CONFIRM_CLEAR_HISTORY = "Are you sure you want to clear all search history?"
CONFIRM_REMOVE_ENTRY = "Remove this history entry?"

# Context menu labels
MENU_COPY_ELEMENT = "Copy Element"
MENU_COPY_VALUE = "Copy Value"
MENU_COPY_XPATH = "Copy XPath"
MENU_COPY_ATT = "Copy Attributes"
MENU_OPEN_XML = "Open in XML File"
MENU_LOAD_SEARCH = "Load Search"
MENU_REMOVE_ENTRY = "Remove Entry"

# Button labels
BUTTON_BROWSE = "Browse..."
BUTTON_SEARCH = "Search"
BUTTON_HISTORY = "History"
BUTTON_CLEAR_ALL = "Clear All"

# Label texts
LABEL_XML_FILE = "XML File:"
LABEL_NO_FILE_SELECTED = "No file selected"
LABEL_ELEMENT_TAG = "Element Tag:"
LABEL_SEARCH_HISTORY = "Search History:"
LABEL_SEARCH_ON = "Search on:"

# Tab labels
TAB_RESULTS = "Results"
TAB_HISTORY = "History"

# CSV
CSV_HEADER = ['timestamp','tag_name','file_path','partial_flag','name_flag','att_flag','value_flag','result_count']