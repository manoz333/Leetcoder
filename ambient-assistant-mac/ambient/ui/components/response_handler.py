"""Response handling utilities for displaying and managing AI responses."""
import logging
import time
import uuid
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QTextCursor, QColor
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QTextEdit, QHBoxLayout, QSizePolicy
import re
import threading
import queue

from ambient.utils.formatting import format_code_blocks


class ResponseHandler:
    """Handles response formatting, display, and management."""
    
    def __init__(self, response_text_widget, status_label):
        """Initialize with the text widget to display responses."""
        self.response_text = response_text_widget
        self.status_label = status_label
        self.logger = logging.getLogger(__name__)
        self.current_response_id = None
        self.last_question_position = None
        
    def format_question(self, question, mode="normal"):
        """Format a user question for display."""
        timestamp = time.strftime("%H:%M:%S")
        response_id = str(uuid.uuid4())
        self.current_response_id = response_id
        
        # Create a clear marker for the question with timestamp
        question_html = f'<div><h3>Question ({timestamp}):</h3><p>{question}</p></div>'
        
        # Store current position
        cursor = self.response_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.question_pos = cursor.position()
        
        # Append the question
        self._append_html_response(question_html)
        
        # Update status
        self._update_status("Processing your question...")
        
        # Create a placeholder for the response
        if mode == "suggester":
            response_type = "Suggestion"
            # Append instruction for line-by-line comments to the question if it contains a code request
            if "code" in question.lower():
                question += "\n\nPlease provide detailed explanations for any code concepts."
        elif mode == "solver":
            response_type = "Solution"
            # Append instruction for line-by-line comments to the question if it contains a code request
            if "code" in question.lower():
                question += "\n\nIMPORTANT: Add a comment for EACH line of code to explain its purpose."
        else:
            response_type = "Response"
            # Append instruction for line-by-line comments to the question if it contains a code request
            if "code" in question.lower():
                question += "\n\nIf you provide any code, ensure EACH line has a comment explaining its purpose."
        
        # Store response ID and question position for scrolling
        self.response_text.response_id = response_id
        self.response_text.response_type = response_type
        self.response_text.timestamp = timestamp
        self.response_text.question_pos = self.question_pos
        self.response_text.accumulated_response = ""
        self.response_text.question_with_instructions = question  # Store the modified question
        
        print(f"DEBUG: Set up for response with ID: {response_id}, type: {response_type}")
        
        return response_id
        
    def format_screenshot_content(self, content, mode="normal"):
        """Format screenshot content for display."""
        timestamp = time.strftime("%H:%M:%S")
        response_id = str(uuid.uuid4())
        self.current_response_id = response_id
        
        # Add screenshot content with HTML formatting
        formatted_content = content.replace('\n', '<br>')
        screenshot_html = (
            f'<div><h3>Screenshot ({timestamp}):</h3>'
            f'<pre style="background-color: rgba(30, 30, 35, 80); color: #E0E0E0; '
            f'padding: 10px; border-radius: 5px; overflow-x: auto; font-family: Menlo, monospace;">'
            f'{formatted_content}</pre></div>'
        )
        
        # Store current position
        cursor = self.response_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.question_pos = cursor.position()
        
        # Append the screenshot content
        self._append_html_response(screenshot_html)
        
        # Create prompt based on mode
        if mode == "suggester":
            prompt_text = f"Acting as a coding teacher, analyze this code without providing complete solutions. Give hints, explain concepts, and suggest improvements:\n\n{content}"
            response_type = "Suggestion"
        elif mode == "solver":
            prompt_text = f"Provide a detailed step-by-step solution for this code problem. Include explanations for each step, proper comments, and the complete solution. IMPORTANT: Add a comment for EACH line of code to explain its purpose:\n\n{content}"
            response_type = "Solution"
        else:
            prompt_text = f"Analyze this code or text and provide helpful suggestions. If you provide any code, ensure EACH line has a comment explaining its purpose:\n\n{content}"
            response_type = "Response"
        
        # Store response ID and question position for scrolling
        self.response_text.response_id = response_id
        self.response_text.response_type = response_type
        self.response_text.timestamp = timestamp
        self.response_text.question_pos = self.question_pos
        self.response_text.accumulated_response = ""
        
        print(f"DEBUG: Set up for screenshot response with ID: {response_id}, type: {response_type}")
        
        return response_id, prompt_text
        
    def format_voice_input(self, text, mode="normal"):
        """Format voice input for display."""
        timestamp = time.strftime("%H:%M:%S")
        response_id = str(uuid.uuid4())
        self.current_response_id = response_id
        
        # Add voice input with HTML formatting
        voice_html = (
            f'<div><h3>Voice Input ({timestamp}):</h3>'
            f'<p>{text}</p></div>'
        )
        
        # Store current position
        cursor = self.response_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.question_pos = cursor.position()
        
        # Append the voice input
        self._append_html_response(voice_html)
        
        # Create a placeholder for the response
        if mode == "suggester":
            response_type = "Suggestion"
            # Append instruction for line-by-line comments to the text if it contains a code request
            if "code" in text.lower():
                text += "\n\nPlease provide detailed explanations for any code concepts."
        elif mode == "solver":
            response_type = "Solution"
            # Append instruction for line-by-line comments to the text if it contains a code request
            if "code" in text.lower():
                text += "\n\nIMPORTANT: Add a comment for EACH line of code to explain its purpose."
        else:
            response_type = "Response"
            # Append instruction for line-by-line comments to the text if it contains a code request
            if "code" in text.lower():
                text += "\n\nIf you provide any code, ensure EACH line has a comment explaining its purpose."
            
        # Store response ID and question position for scrolling
        self.response_text.response_id = response_id
        self.response_text.response_type = response_type
        self.response_text.timestamp = timestamp
        self.response_text.question_pos = self.question_pos
        self.response_text.accumulated_response = ""
        self.response_text.question_with_instructions = text  # Store the modified text
        
        print(f"DEBUG: Set up for voice response with ID: {response_id}, type: {response_type}")
        
        return response_id
        
    def handle_response(self, response_data):
        """Handle complete response data."""
        print(f"DEBUG: ResponseHandler.handle_response called with: {response_data}")
        self.logger.info(f"Handling response in ResponseHandler: {type(response_data)}")
        
        # If it's a string, for backward compatibility
        if isinstance(response_data, str):
            response = response_data
            response_id = self.current_response_id
        else:
            response = response_data.get('text', '')
            response_id = response_data.get('response_id', self.current_response_id)
        
        print(f"DEBUG: Processing response with ID: {response_id}, length: {len(response) if response else 0}")
        
        # Format the response
        formatted_response = format_code_blocks(response)
        
        # Check if we have a response type and timestamp from our stored attributes
        response_type = getattr(self.response_text, 'response_type', 'Response')
        timestamp = getattr(self.response_text, 'timestamp', time.strftime("%H:%M:%S"))
        
        # Create response HTML
        response_html = f'<div><h3>{response_type} ({timestamp}):</h3>{formatted_response}</div>'
        
        # Append the formatted response
        self._append_html_response(response_html)
        print(f"DEBUG: Appended full response for ID: {response_id}")
        
        # Update status
        self._update_status("Response received")
        
        # Scroll back to the question
        self._scroll_to_question(response_id)
        
    def handle_response_chunk(self, chunk_data):
        """Handle streaming response chunks."""
        chunk = chunk_data.get('text', '')
        response_id = chunk_data.get('response_id', self.current_response_id)
        is_final = chunk_data.get('is_final', False)
        
        print(f"DEBUG: Response chunk received: ID={response_id}, is_final={is_final}, length={len(chunk)}")
        
        if not response_id or (not chunk and not is_final):
            print(f"DEBUG: Skipping chunk - no response_id or empty non-final chunk")
            return
        
        # Retrieve or initialize accumulated response
        accumulated_response = getattr(self.response_text, 'accumulated_response', '') + chunk
        self.response_text.accumulated_response = accumulated_response
        
        # Get response type and timestamp
        response_type = getattr(self.response_text, 'response_type', 'Response')
        timestamp = getattr(self.response_text, 'timestamp', time.strftime("%H:%M:%S"))
        
        # If this is the final chunk, just mark it as complete without showing a duplicate response
        if is_final:
            # Reset accumulated response
            self.response_text.accumulated_response = ""
            
            # Update status without creating a new response element
            words = accumulated_response.split()
            word_count = len(words)
            self._update_status(f"Response completed ({len(accumulated_response)} chars, ~{word_count} words)")
            
            # Publish the event that the response is ready, but don't append a new one
            print(f"DEBUG: Marking response as complete for ID: {response_id}")
            
            # No need to publish another event or append anything more - the streaming response is already displayed
            return
        else:
            # For intermediate chunks, apply streaming-optimized formatting
            formatted_stream = self._format_streaming_code_blocks(accumulated_response)
            
            # Clear the existing content
            self.response_text.clear()
            
            # If we have a stored question, reinsert it
            question_pos = getattr(self.response_text, 'question_pos', None)
            if question_pos is not None:
                # Move cursor to the stored position and reinsert question
                cursor = self.response_text.textCursor()
                try:
                    cursor.setPosition(question_pos)
                    self.response_text.setTextCursor(cursor)
                except Exception as e:
                    print(f"DEBUG: Error setting cursor position: {e}")
            
            # Create response HTML with plain formatting
            response_html = f'<div><h3>{response_type} ({timestamp}):</h3>{formatted_stream}</div>'
            
            # Append the partial response
            self._append_html_response(response_html)
            
            # Force update and repaint of the text widget
            self.response_text.update()
            QApplication.processEvents()  # Process pending events to ensure UI updates
            
            # Update status to show streaming is active and how many characters/words received
            words = accumulated_response.split()
            word_count = len(words)
            self._update_status(f"Receiving response... ({len(accumulated_response)} chars, ~{word_count} words)")
    
    def _format_streaming_code_blocks(self, text):
        """Format streaming response content with very minimal Markdown processing."""
        # Use a simplified approach to formatting
        formatted_html = []
        
        # Process the text by splitting into blocks based on double newlines
        blocks = re.split(r'\n\n+', text)
        
        # Track if we're inside a code block that hasn't closed yet
        in_code_block = False
        code_content = []
        language = None
                
        for block in blocks:
            # Skip empty blocks
            if not block.strip():
                continue
                
            # Check for code blocks
            if '```' in block:
                # Handle both opening and closing code blocks in the same chunk
                if block.count('```') >= 2:
                    # Complete code block - use more robust regex to handle multiline code
                    code_pattern = r'```([\w]*)\n(.*?)```'
                    match = re.search(code_pattern, block, re.DOTALL)
                    
                    if match:
                        # Simple italic formatting for code with line breaks preserved
                        code = match.group(2)
                        # Replace newlines with <br> tags to preserve line breaks
                        code_with_breaks = code.replace('\n', '<br>')
                        formatted_html.append(f'<p><i>{code_with_breaks}</i></p>')
                    else:
                        # Fallback if regex failed - preserve the block as-is with line breaks
                        clean_code = block.replace("```", "")
                        code_with_breaks = clean_code.replace('\n', '<br>')
                        formatted_html.append(f'<p><i>{code_with_breaks}</i></p>')
                
                elif block.startswith('```'):
                    # Opening a code block
                    in_code_block = True
                    # Extract language if present
                    code_start = block.split('\n', 1)
                    language = code_start[0].replace('```', '').strip()
                    
                    if len(code_start) > 1:
                        # If there's content after the opening, add it to code_content
                        code_content.append(code_start[1])
                    
                elif in_code_block and '```' in block:
                    # Closing a code block
                    code_content.append(block.split('```')[0])
                    code = '\n'.join(code_content)
                    # Simple italic formatting for code with line breaks preserved
                    code_with_breaks = code.replace('\n', '<br>')
                    formatted_html.append(f'<p><i>{code_with_breaks}</i></p>')
                    in_code_block = False
                    code_content = []
                    language = None
                    
                    # Check if there's content after the closing ```
                    after_code = block.split('```')[1]
                    if after_code.strip():
                        formatted_html.append(f'<p>{after_code}</p>')
            
            # Continue building code block content
            elif in_code_block:
                code_content.append(block)
            
            # Handle headers
            elif block.startswith('# '):
                # h1 header - bold
                header_text = block[2:].strip()
                formatted_html.append(f'<p><b>{header_text}</b></p>')
            
            elif block.startswith('## '):
                # h2 header - bold
                header_text = block[3:].strip()
                formatted_html.append(f'<p><b>{header_text}</b></p>')
            
            elif block.startswith('### '):
                # h3 header - bold
                header_text = block[4:].strip()
                formatted_html.append(f'<p><b>{header_text}</b></p>')
            
            # Handle bullet lists
            elif block.strip().startswith('- '):
                # Process bullet list - simple formatting with line breaks
                list_items = block.split('\n')
                items_html = []
                
                for item in list_items:
                    if item.strip().startswith('- '):
                        item_text = item.strip()[2:]
                        # Process any inline formatting within list items
                        item_text = self._process_inline_formatting(item_text)
                        items_html.append(f'• {item_text}<br>')
                
                formatted_html.append(f'<p>{"".join(items_html)}</p>')
            
            # Handle numbered lists
            elif re.match(r'^\d+\.\s', block.strip()):
                # Process numbered list - simple formatting with line breaks
                list_items = block.split('\n')
                items_html = []
                
                for item in list_items:
                    if re.match(r'^\d+\.\s', item.strip()):
                        item_match = re.match(r'^\d+\.\s+(.*)', item.strip())
                        if item_match:
                            item_text = item_match.group(1)
                            # Process any inline formatting within list items
                            item_text = self._process_inline_formatting(item_text)
                            items_html.append(f'{item.strip().split(".", 1)[0]}. {item_text}<br>')
                
                formatted_html.append(f'<p>{"".join(items_html)}</p>')
            
            # Regular paragraph
            else:
                # Process any inline formatting and preserve line breaks
                processed_text = self._process_inline_formatting(block)
                # Replace newlines with <br> tags
                processed_with_breaks = processed_text.replace('\n', '<br>')
                formatted_html.append(f'<p>{processed_with_breaks}</p>')
        
        # Handle case where we're still in a code block (incomplete code block)
        if in_code_block and code_content:
            # Format the incomplete code block - simple italic with line breaks preserved
            code = '\n'.join(code_content)
            code_with_breaks = code.replace('\n', '<br>')
            formatted_html.append(f'<p><i>{code_with_breaks}</i></p>')
            formatted_html.append(f'<p><i>...</i></p>')  # Indicate continuation
        
        return ''.join(formatted_html)
    
    def _process_inline_formatting(self, text):
        """Process inline formatting elements like bold, italic, code, etc."""
        # Handle inline code - simple italic
        text = re.sub(r'`([^`]+)`', r'<i>\1</i>', text)
        
        # Handle bold text
        text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
        
        # Handle italic text
        text = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', text)
        
        return text
    
    def _format_code_block(self, code, language):
        """Format a code block with minimal formatting."""
        # Basic styling for code blocks
        return f'<pre><i>{code}</i></pre>'

    def set_welcome_message(self):
        """Set initial welcome message."""
        welcome_text = """# Ambient Assistant

Welcome! I'm your coding assistant. I can:
- Answer questions about code
- Analyze your screen for code
- Provide suggestions and tips

Use the controls below to interact with me.

## Modes:
- **Normal**: Basic assistance with code
- **Suggester**: Provides detailed step-by-step guidance with code snippets
- **Solver**: Provides comprehensive solutions with approach explanation and commented code
"""
        self._update_response(welcome_text)
        
    def _update_response(self, text):
        """Set response text."""
        try:
            # Convert to HTML with code formatting if it contains code blocks
            if "```" in text:
                formatted_text = format_code_blocks(text)
                self.response_text.setHtml(formatted_text)
            else:
                self.response_text.setText(text)
        except Exception as e:
            self.logger.error(f"Error updating response: {e}")
            
    def _append_html_response(self, html_text):
        """Append HTML formatted text to response area safely."""
        try:
            print(f"DEBUG: Appending HTML with length: {len(html_text)}")
            cursor = self.response_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            
            # Add spacing before the response
            cursor.insertHtml("<br><br>")
            
            # Ensure HTML is properly formatted
            if not html_text.strip().startswith('<'):
                # If it's not already HTML, wrap it
                html_text = f"<div>{html_text}</div>"
                
            try:
                # Insert HTML content
                cursor.insertHtml(html_text)
                
                # Make sure the inserted HTML is displayed
                self.response_text.setTextCursor(cursor)
                self.response_text.ensureCursorVisible()
            except Exception as e:
                # If insertHtml fails, try with setHtml as a fallback
                print(f"DEBUG: insertHtml failed, trying alternative approach: {e}")
                current_html = self.response_text.toHtml()
                # Insert at the end of the document body
                insert_pos = current_html.rfind('</body>')
                if insert_pos > 0:
                    new_html = current_html[:insert_pos] + html_text + current_html[insert_pos:]
                    self.response_text.setHtml(new_html)
                else:
                    # Last resort, just append text
                    self.response_text.append(html_text.replace('<', '&lt;').replace('>', '&gt;'))
            
            # Refresh the view to make sure content is visible
            self.response_text.update()
            QApplication.processEvents()  # Ensure UI updates
            
        except Exception as e:
            print(f"DEBUG: Error in _append_html_response: {e}")
            self.logger.error(f"Error appending HTML response: {e}")
            # Fallback to plain text
            self._append_response(html_text.replace('<br>', '\n').replace(re.compile(r'<[^>]+>'), ''))
            
    def _append_response(self, text):
        """Append text to response area safely."""
        try:
            current = self.response_text.toPlainText()
            new_text = current + "\n\n" + text if current else text
            self.response_text.setText(new_text)
            
            # Scroll to bottom
            self.response_text.verticalScrollBar().setValue(
                self.response_text.verticalScrollBar().maximum()
            )
        except Exception as e:
            self.logger.error(f"Error appending response: {e}")
    
    def _scroll_to_question(self, response_id):
        """Scroll to the question that prompted this response."""
        # Use the stored question position if available
        question_pos = getattr(self.response_text, 'question_pos', None)
        if question_pos is not None:
            cursor = self.response_text.textCursor()
            cursor.setPosition(question_pos)
            self.response_text.setTextCursor(cursor)
            self.response_text.ensureCursorVisible()
            print(f"DEBUG: Scrolled to stored question position")
        else:
            # As a fallback, try to scroll to the top
            cursor = self.response_text.textCursor()
            cursor.setPosition(0)
            self.response_text.setTextCursor(cursor)
            self.response_text.ensureCursorVisible()
            print(f"DEBUG: No stored question position, scrolled to top")
        
    def _update_status(self, message):
        """Update status message safely from any thread."""
        try:
            self.status_label.setText(message)
            # Auto-reset after delay
            QTimer.singleShot(3000, lambda: self.status_label.setText("Ready"))
        except Exception as e:
            self.logger.error(f"Error updating status: {e}") 