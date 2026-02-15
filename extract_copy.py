import xml.etree.ElementTree as ET
import re
import html

def clean_text(text):
    if not text:
        return ""
    # Decode HTML entities
    text = html.unescape(text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Remove WordPress block comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_copy(xml_file, output_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Namespaces
        namespaces = {
            'content': 'http://purl.org/rss/1.0/modules/content/',
            'wp': 'http://wordpress.org/export/1.2/'
        }
        
        extracted_text = []
        
        # Find the channel element
        channel = root.find('channel')
        if channel is None:
            print("No channel found in XML.")
            return

        # Iterate through items
        for item in channel.findall('item'):
            post_type = item.find('wp:post_type', namespaces).text if item.find('wp:post_type', namespaces) is not None else ""
            
            # Filter out non-copy post types
            if post_type in ['wp_global_styles', 'attachment', 'wp_navigation', 'nav_menu_item', 'wp_template_part']:
                continue

            title = item.find('title').text if item.find('title') is not None else ""
            content = item.find('content:encoded', namespaces).text if item.find('content:encoded', namespaces) is not None else ""
            
            clean_title = clean_text(title)
            clean_content = clean_text(content)
            
            # Skip if both title and content are empty
            if not clean_title and not clean_content:
                continue
                
            if clean_title:
                extracted_text.append(clean_title)
            
            if clean_content:
                extracted_text.append(clean_content)
                
            extracted_text.append("") # Blank line separator

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(extracted_text))
            
        print(f"Successfully extracted text to {output_file}")

    except ET.ParseError as e:
        print(f"XML Parse Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    xml_path = '/home/idleslot/copperk.com/old_site/copperk.WordPress.2026-02-14.xml'
    output_path = '/home/idleslot/copperk.com/extracted_copy.txt'
    extract_copy(xml_path, output_path)
