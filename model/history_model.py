import csv
import os

from DefineConst import *
from model.singleton import Singleton

class HistoryModel(Singleton):
    """Model to manage history data stored in a CSV file."""
    
    def __init__(self, file_path=HISTORY_FILE_PATH):
        # Initialize only once (Singleton pattern)
        if not hasattr(self, 'initialized'):
            self._file_path = file_path
            self._history = self.load_history()
            self.initialized = True
        
    def get_history(self):
        """Return the history data."""
        return self._history
    
    def add_entry(self, entry):
        """Add a new entry to history."""
        self._history.append(entry)
        self.save_history()
    
    def clear_history(self):
        """Clear all history entries."""
        self._history = []
        self.save_history()
    
    def load_history(self):
        """Load history from the CSV file."""
        if not os.path.exists(self._file_path):
            return []
        
        with open(self._file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            return [row for row in reader]
    
    def save_history(self):
        """Save history to the CSV file."""
        if not self._history:
            # If history is empty, remove the file
            if os.path.exists(self._file_path):
                os.remove(self._file_path)
            return
        
        with open(self._file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = CSV_HEADER
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self._history)

    def export_history(history_model, export_path):
        """Export history to a specified CSV file."""
        try:
            with open(export_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = CSV_HEADER
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(history_model._history)
            return True, "Export successful"
        except Exception as e:
            return False, f"Export failed: {str(e)}"

    def import_history(history_model, import_path):
        """Import history from a specified CSV file."""
        try:
            with open(import_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                history_model._history = [row for row in reader]
                # history_model.save_history()
            return True, "Import successful"
        except Exception as e:
            return False, f"Import failed: {str(e)}"