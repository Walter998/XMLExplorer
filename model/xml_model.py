import xml.etree.ElementTree as ET
import os

from model.singleton import Singleton
from DefineConst import *

class XMLModel(Singleton):
    """Model for XML processing. Implements Singleton pattern."""
    
    def __init__(self):
        # Initialize only once (Singleton pattern)
        if not hasattr(self, 'initialized'):
            self.xml_file_path = None
            self.xml_tree = None
            self.root = None
            self.cache = {}  # Cache for faster repeated searches
            self.initialized = True
        
    def is_file_loaded(self):
        """
        Check if an XML file is currently loaded.
        
        Returns:
            bool: True if a file is loaded, False otherwise
        """
        return hasattr(self, 'root') and self.root is not None
    
    def load_xml_file(self, file_path):
        """
        Load an XML file for processing.
        
        Args:
            file_path: Path to the XML file
            
        Returns:
            (bool, str): Success status and error message if any
        """
        # If same file, don't reload
        if self.xml_file_path == file_path and self.xml_tree is not None:
            return True, None
            
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                return False, ERROR_FILE_NOT_FOUND.format(file=file_path)
                
            # Validate file is an XML file
            if not file_path.lower().endswith('.xml') and not self._is_xml_content(file_path):
                return False, ERROR_NOT_XML.format(file=file_path)
                
            self.xml_file_path = file_path
            
            # Use standard parser
            self.xml_tree = ET.parse(file_path)

            self.root = self.xml_tree.getroot()  # Set the root attribute
            self.file_path = file_path
            
            self.cache = {}  # Clear cache when loading a new file
            return True, None
        except ET.ParseError as e:
            return False, ERROR_PARSING_XML.format(error=e)
        except Exception as e:
            return False, ERROR_LOADING_XML.format(error=str(e))
    
    def _is_xml_content(self, file_path):
        """Check if file content appears to be XML regardless of extension."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1000)  # Read first 1000 chars
                return content.strip().startswith('<?xml') or '<' in content
        except:
            return False
    
    def _generate_xpath(self, element):
        """
        Generate an XPath expression for the specified element.
        
        Args:
            element: The XML element to generate an XPath for
        
        Returns:
            str: The XPath expression
        """
        # Start with an empty path
        path = []
        
        # Traverse up the tree to build the path
        current = element
        while current is not None:
            # Get the tag name (remove namespace if present)
            tag = current.tag
            if '}' in tag:
                tag = tag.split('}', 1)[1]
            
            # Check if there are siblings with the same tag
            parent = current.getparent() if hasattr(current, 'getparent') else None
            
            if parent is not None:
                # Count siblings with the same tag that come before this element
                siblings = parent.findall(f"./{tag}")
                if len(siblings) > 1:
                    # There are multiple siblings with the same tag, so include an index
                    for i, sibling in enumerate(siblings):
                        if sibling == current:
                            path.insert(0, f"{tag}[{i+1}]")
                            break
                else:
                    # This is the only child with this tag
                    path.insert(0, tag)
            else:
                # This is the root element
                path.insert(0, tag)
            
            # Move up to the parent
            current = parent
        
        # Construct the final XPath
        xpath = "/" + "/".join(path)
        return xpath

    def find_elements_by_tag(self, tag_name, flag_name, flag_att, flag_value, partial_match):
        """
        Find all elements with the specified tag name.
        
        Args:
            tag_name (str): The tag name to search for
            partial_match (bool): If True, return elements with tags that contain the search string
                                If False, only return exact matches
        
        Returns:
            list: List of element dictionaries containing name, value, XPath, and attributes
        """
        try:
            if not hasattr(self, 'root') or self.root is None:
                return ([], "No XML file is loaded")
            
            results = []
            elements = []
            
            # Special case for showing all elements
            if tag_name == SEARCH_ALL_ELEMENTS:
                elements = list(self.root.iter())
            else:
                # For partial matching, we need to iterate through all elements and check manually
                if partial_match:
                    elements = []
                    for elem in self.root.iter():
                        # Check if tag_name is a substring of the element's tag
                        flag_append = False
                        if (
                            ((flag_name == True) and (tag_name.lower() in elem.tag.lower()))
                            or ((flag_value == True) and (elem.text != None) and (tag_name.lower() in elem.text.lower()) )
                        ):
                            flag_append = True
                        elif (flag_att == True):
                            for key,value in elem.attrib.items():
                                if (tag_name.lower() in key.lower()):
                                    flag_append = True
                                    break
                                else:
                                    try:
                                        if (tag_name.lower() in value.lower()):
                                            flag_append = True
                                            break
                                    except AttributeError:
                                        if (tag_name in str(value)):
                                            flag_append = True
                                            break
                        if flag_append:
                            element_info = self._get_element_details(elem)
                            results.append(element_info)

                else:
                    # For exact matching, use the existing behavior
                    elements = self.root.findall(f".//{tag_name}")

            for elem in elements:
                element_info = self._get_element_details(elem)
                results.append(element_info)
            return (results, "")
        
        except Exception as e:
            # Log the error
            error_msg = ERROR_SEARCHING.format(error=str(e))
            print(error_msg)
            return ([], error_msg)
    
    def find_all_elements(self):
        """
        Find all elements in the XML file.
        
        Returns:
            (list, str): List of element information and error message if any
        """
        if not self.xml_tree:
            return None, ERROR_NO_XML_LOADED
        
        # Check cache first
        cache_key = f"{self.xml_file_path}:{SEARCH_ALL_ELEMENTS}"
        if cache_key in self.cache:
            return self.cache[cache_key], None
        
        try:
            root = self.xml_tree.getroot()
            results = []
            
            # Gather all elements
            for elem in root.iter():
                # Get element details
                element_info = self._get_element_details(elem)
                results.append(element_info)
            
            # Cache the results
            self.cache[cache_key] = results
            return results, None
        except Exception as e:
            return None, ERROR_SEARCHING.format(error=str(e))
    
    def _get_element_details(self, element):
        """Get comprehensive details about an XML element."""
        # Get element tag name (remove namespace if present)
        tag = element.tag
        if '}' in tag:
            tag = tag.split('}', 1)[1]
        
        # Get element text value
        text = element.text.strip() if element.text else ""
        
        # Get full path and XPath
        path = self._get_element_path(element)
        xpath = self._get_element_xpath(element)
        
        # Get attributes
        attributes = {k: v for k, v in element.attrib.items()}
        
        return {
            'name': tag,
            'value': text,
            'path': path,
            'xpath': xpath,
            'attributes': attributes,
            'element': element  # Keep reference to the element
        }
    
    def _get_element_path(self, element):
        """Generate a human-readable path to the element."""
        path_parts = []
        current = element
        root = self.xml_tree.getroot()
        
        # Build path by traversing up to root
        while current is not None:
            if current.tag:
                # Remove namespace from tag if present
                tag = current.tag
                if '}' in tag:
                    tag = tag.split('}', 1)[1]
                
                # Add attributes to distinguish elements with same tag
                if current.attrib:
                    attribs = []
                    for key, value in current.attrib.items():
                        # Skip namespace declarations
                        if not key.startswith('xmlns'):
                            attribs.append(f'{key}="{value}"')
                    
                    if attribs:
                        tag += f" [{' '.join(attribs)}]"
                
                path_parts.append(tag)
            
            # Find parent - ElementTree doesn't have direct parent access
            parent = None
            for p in root.iter():
                if current in list(p):
                    parent = p
                    break
            
            current = parent
            if current == root:
                # Add root and break
                path_parts.append(root.tag)
                break
        
        # Reverse to get root->leaf order and join with '/'
        path_parts.reverse()
        return XPATH_DEFAULT_ROOT + '/'.join(path_parts)
    
    def _get_element_xpath(self, element):
        """Generate a standard XPath for the element."""
        # This is an approximation since ElementTree doesn't provide direct XPath
        path_parts = []
        
        # Track the current element
        current = element
        root = self.xml_tree.getroot()
        
        # Walk up the tree to build the XPath
        while current is not None:
            # Find the parent
            parent = None
            for p in root.iter():
                if current in list(p):
                    parent = p
                    break
            
            if parent is None:
                # This is the root element
                path_parts.append(current.tag)
                break
            
            # Count the position among siblings with the same tag
            position = 1
            for sibling in parent:
                if sibling is current:
                    break
                if sibling.tag == current.tag:
                    position += 1
            
            # Get the tag name (with namespace)
            tag_name = current.tag
            
            # Add this element to the path
            path_parts.append(f"{tag_name}[{position}]")
            
            # Move up to the parent
            current = parent
        
        # Reverse and join with '/'
        path_parts.reverse()
        return XPATH_DEFAULT_ROOT + '/'.join(path_parts)
    