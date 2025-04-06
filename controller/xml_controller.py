from model.xml_model import XMLModel
from model.history_model import HistoryModel
from DefineConst import *

class XMLController:
    """Controller class to handle application logic."""
    
    def __init__(self, view=None):
        self.view = view
        self.xml_model = XMLModel()
        self.history_model = HistoryModel()

    def get_current_file_path(self):
        """Get the path of the currently loaded XML file."""
        return self.xml_model.xml_file_path

    def reload_xml_file(self):
        """Reload the current XML file after it has been edited."""
        if not self.xml_model.xml_file_path:
            return False, ERROR_NO_FILE
        
        return self.load_xml_file(self.xml_model.xml_file_path)
    
    def set_view(self, view):
        """
        Set the view to be used by the controller.
        
        Args:
            view: View object
        """
        self.view = view
    
    def load_xml_file(self, file_path):
        """
        Load an XML file for processing.
        
        Args:
            file_path: Path to the XML file
            
        Returns:
            (bool, str): Success status and error message if any
        """
        return self.xml_model.load_xml_file(file_path)
    
    def search_tag(self, tag_name, flag_name, flag_att, flag_value, partial_flag=True):
        """
        Search for elements with the specified tag name or all elements if tag is empty.
        
        Args:
            tag_name: Tag name to search for
            
        Returns:
            (bool, list, str): Success status, results, and error message if any
        """
        # Check if a file is loaded
        if not self.xml_model.xml_file_path:
            return False, None, ERROR_NO_FILE
        
        # Check if tag name is empty and convert to wildcard search if appropriate
        if not tag_name:
            if SEARCH_EMPTY_SHOWS_ALL:
                tag_name = SEARCH_ALL_ELEMENTS
            else:
                return False, None, ERROR_NO_TAG
        
        # Update status in the view
        if self.view:
            if tag_name == SEARCH_ALL_ELEMENTS:
                self.view.update_status(STATUS_SEARCHING_ALL)
            else:
                self.view.update_status(STATUS_SEARCHING.format(tag=tag_name))
        
        # Process search
        if tag_name == SEARCH_ALL_ELEMENTS:
            results, error = self.xml_model.find_all_elements()
        else:
            results, error = self.xml_model.find_elements_by_tag(tag_name, flag_name, flag_att, flag_value, partial_flag)
            
        if error:
            return False, None, error
        
        return True, results, None
    