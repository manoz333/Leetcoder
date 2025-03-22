"""Formatting utilities for code syntax highlighting and text processing."""
import re


class CodeColors:
    """Colors used for syntax highlighting code blocks."""
    KEYWORD = "#569CD6"     # Blue
    STRING = "#CE9178"      # Orange
    COMMENT = "#6A9955"     # Green
    FUNCTION = "#DCDCAA"    # Yellow
    CLASS = "#4EC9B0"       # Teal
    NUMBER = "#B5CEA8"      # Light Green
    OPERATOR = "#D4D4D4"    # Light Gray
    VARIABLE = "#9CDCFE"    # Light Blue
    BACKGROUND = "#1E1E1E"  # Darker background for better contrast
    TEXT = "#F8F8F8"        # Brighter text for better readability
    BORDER = "#454545"      # More visible border


def format_code_blocks(text):
    """Format code blocks in the response with minimal styling."""
    # Pattern to find Markdown code blocks - more robust pattern to handle multiline code
    code_pattern = r'```([\w]*)\n(.*?)\n```'
    
    def format_code_with_html(match):
        code = match.group(2)      # The code content
        
        # Apply simple italic formatting for code with line breaks preserved
        code_with_breaks = code.replace('\n', '<br>')
        return f'<p><i>{code_with_breaks}</i></p>'
    
    # Replace code blocks with simpler formatting
    formatted_text = re.sub(code_pattern, format_code_with_html, text, flags=re.DOTALL)
    
    # Convert Markdown headers to bold tags
    formatted_text = re.sub(r'# (.*?)\n', r'<p><b>\1</b></p>\n', formatted_text)
    formatted_text = re.sub(r'## (.*?)\n', r'<p><b>\1</b></p>\n', formatted_text)
    formatted_text = re.sub(r'### (.*?)\n', r'<p><b>\1</b></p>\n', formatted_text)
    
    # Convert Markdown bold to HTML bold
    formatted_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', formatted_text)
    
    # Convert Markdown italic to HTML italic
    formatted_text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', formatted_text)
    
    # Handle inline code with backticks - simple format
    formatted_text = re.sub(r'`([^`]+)`', r'<i>\1</i>', formatted_text)
    
    # Simple bullet list handling
    bullet_pattern = r'- (.*?)(?:\n|$)'
    bullet_matches = list(re.finditer(bullet_pattern, formatted_text))
    
    if bullet_matches:
        # Process bullet points to group them
        list_replacements = []
        i = 0
        while i < len(bullet_matches):
            start_match = bullet_matches[i]
            start_pos = start_match.start()
            
            # Find consecutive bullet points
            j = i + 1
            while j < len(bullet_matches) and (
                bullet_matches[j].start() - bullet_matches[j-1].end() <= 1 or
                formatted_text[bullet_matches[j-1].end():bullet_matches[j].start()].strip() == ''
            ):
                j += 1
                
            # Get all items in this list with simple formatting
            list_items = []
            for k in range(i, j):
                item_text = bullet_matches[k].group(1)
                list_items.append(f'• {item_text}<br>')
            
            # Create replacement HTML for the list
            end_pos = bullet_matches[j-1].end() if j > i else start_match.end()
            list_html = f'<p>{"".join(list_items)}</p>'
            
            list_replacements.append((start_pos, end_pos, list_html))
            i = j
            
        # Apply replacements from last to first to avoid position shifts
        for start_pos, end_pos, replacement in reversed(list_replacements):
            formatted_text = formatted_text[:start_pos] + replacement + formatted_text[end_pos:]
    
    # Basic numbered list handling
    number_pattern = r'(\d+)\.\s+(.*?)(?:\n|$)'
    number_matches = list(re.finditer(number_pattern, formatted_text))
    
    if number_matches:
        # Process numbered points to group them
        list_replacements = []
        i = 0
        while i < len(number_matches):
            start_match = number_matches[i]
            start_pos = start_match.start()
            
            # Find consecutive numbered points
            j = i + 1
            while j < len(number_matches) and (
                number_matches[j].start() - number_matches[j-1].end() <= 1 or
                formatted_text[number_matches[j-1].end():number_matches[j].start()].strip() == ''
            ):
                j += 1
                
            # Get all items in this list with simple formatting
            list_items = []
            for k in range(i, j):
                number = number_matches[k].group(1)
                item_text = number_matches[k].group(2)
                list_items.append(f'{number}. {item_text}<br>')
            
            # Create replacement HTML for the list
            end_pos = number_matches[j-1].end() if j > i else start_match.end()
            list_html = f'<p>{"".join(list_items)}</p>'
            
            list_replacements.append((start_pos, end_pos, list_html))
            i = j
            
        # Apply replacements from last to first to avoid position shifts
        for start_pos, end_pos, replacement in reversed(list_replacements):
            formatted_text = formatted_text[:start_pos] + replacement + formatted_text[end_pos:]
    
    # Also handle newlines in normal paragraphs by replacing them with <br> tags
    # Find paragraphs that aren't already in HTML tags or lists
    for paragraph in re.findall(r'(?<![>])[^<>]+(?![<])', formatted_text):
        if '\n' in paragraph:
            formatted_paragraph = paragraph.replace('\n', '<br>')
            formatted_text = formatted_text.replace(paragraph, formatted_paragraph)
    
    return formatted_text


def apply_syntax_highlighting(code, language):
    """Apply minimal formatting for code."""
    # Just return the code with no highlighting
    return code.replace('\n', '<br>') 