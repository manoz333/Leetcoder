import logging
import time
import random
import re
from langchain_community.chat_models import ChatOpenAI
from ambient.core.event_bus import Events

class ModelManager:
    def __init__(self, event_bus, settings_manager):
        self.event_bus = event_bus
        self.settings_manager = settings_manager
        self.logger = logging.getLogger(__name__)
        self.demo_mode = False
        
        # Get API key
        self.api_key = self.settings_manager.get_setting('openai_api_key')
        
        # Initialize LLM
        self._initialize_llm()
        
    def _initialize_llm(self):
        """Initialize LLM with error handling and demo mode fallback."""
        if not self.api_key:
            self.logger.warning("No OpenAI API key found - running in demo mode")
            self.demo_mode = True
            return
            
        try:
            # Initialize with streaming support
            self.chat_model = ChatOpenAI(
                api_key=self.api_key,
                temperature=0.7,
                model_name="gpt-4o",
                request_timeout=30,
                streaming=True  # Enable streaming
            )
            self.logger.info("LLM initialized with OpenAI (streaming enabled)")
            self.demo_mode = False
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM: {e}")
            self.demo_mode = True
    
    def _format_prompt(self, question_data):
        """Format prompt with better context handling based on mode."""
        # Unpack the question data
        if isinstance(question_data, dict):
            question = question_data.get('text', '')
            mode = question_data.get('mode', 'normal')
        else:
            # For backward compatibility
            question = question_data
            mode = 'normal'
        
        # Base system message with emphasis on code efficiency
        system_message = """You are an AI coding assistant that helps with programming tasks.
Always prioritize writing the most efficient, optimized code solutions possible, focusing on:
- Time and space complexity optimization
- Clean, readable code structure
- Best practices and design patterns
- Proper error handling
- Appropriate comments explaining logic
- IMPORTANT: Include a comment for EACH line of code explaining its purpose

When possible, explicitly state the time/space complexity of your solutions and explain WHY your approach is efficient.
Choose appropriate data structures and algorithms to minimize computational complexity.
Aim for the optimal balance between readability and performance.

For LeetCode-style problems:
1. ALWAYS maintain the exact function/class signature as specified in the problem
2. Provide a detailed step-by-step analysis of your approach before the code
3. Include time and space complexity analysis
4. Write the solution with comprehensive comments explaining each step
5. Address ALL example test cases shown in the problem - not just a subset
6. Consider edge cases in your solution
7. DO NOT include print statements or test code unless requested
8. Ensure the solution follows proper LeetCode submission format
9. Your solution must satisfy ALL the examples shown in the problem statement
10. Provide REAL working code that will solve the problem, not simplified examples
11. Make sure your code can be directly submitted to LeetCode without modification
12. CRITICAL: EVERY line of code MUST have a comment explaining its purpose"""
        
        # Customize based on mode
        if mode == "suggester":
            system_message = """You are an expert coding teacher that helps students learn programming through detailed step-by-step guidance.
Your role is to GUIDE and TEACH rather than just give full solutions.

Focus on:
- Explaining concepts and principles clearly
- Breaking down problems into small, manageable steps
- Providing code snippets that illustrate each step
- Explaining WHY each step is necessary and HOW it works
- Suggesting approaches with clear explanations
- Correcting typos or syntax errors while explaining why they're wrong
- Maintaining a teaching tone that encourages learning
- Including detailed comments for EACH line of code to explain its purpose

ALWAYS prioritize efficiency in your code examples:
- Highlight the time and space complexity of solutions (Big O notation)
- Suggest optimizations when possible and explain the performance benefits
- Explain WHY certain approaches are more efficient than others
- Guide toward more efficient data structures and algorithms
- Point out potential performance bottlenecks
- Teach best practices for writing performant code

For LeetCode-style problems:
1. Identify the problem type and common patterns that apply
2. Explain multiple approaches, from brute force to optimized
3. Detail the time/space complexity tradeoffs of each approach
4. Provide hints and partial solutions that guide without giving the full answer
5. ALWAYS respect the exact function/class signature from the problem
6. Explain how to handle ALL example test cases from the problem statement
7. DO NOT just print example outputs - provide actual executable code for the solution
8. Ensure your code handles ALL the examples in the problem statement, not just a subset
9. All solution code should be usable for direct submission to LeetCode without modification
10. Include sufficient inline comments to explain key parts of the solution

Your responses should include:
1. An overview of the concepts involved
2. Step-by-step breakdown with explanations and reasoning
3. Small code examples that illustrate each step
4. Guidance on how to test and verify each step
5. Clear indications of the time/space complexity of different approaches

Provide code snippets to illustrate concepts, but remember your primary role is to teach."""

        elif mode == "solver":
            system_message = """You are an expert programming mentor that provides comprehensive solutions to coding problems.
Your role is to provide COMPLETE, PROFESSIONAL solutions with detailed explanations.

For LeetCode-style problems:
1. ALWAYS maintain the exact function/class signature as specified in the problem
2. Your solution MUST be in the correct format for direct submission to LeetCode
3. Include thorough inline comments explaining your logic
4. Analyze the time and space complexity in Big O notation
5. Address ALL examples from the problem statement - your solution must handle EVERY test case
6. Consider and handle all edge cases
7. DO NOT include print statements or test code unless specifically requested
8. For class-based problems (e.g., design questions), follow the exact class structure required
9. Provide REAL working code, not simplified print-output solutions
10. Make certain your solution handles ALL the examples shown in the problem, not just a simplified subset
11. CRITICAL: EVERY line of code MUST have a comment explaining its purpose and function

Your responses MUST follow this structure:
1. PROBLEM ANALYSIS: First explain your understanding of the problem, requirements, and important considerations
2. APPROACH OVERVIEW: Describe your solution strategy with a focus on efficiency
3. STEP-BY-STEP IMPLEMENTATION: Break down the solution into logical steps with explanations
4. COMPLETE CODE SOLUTION: Provide a full, working implementation with a comment for EVERY line of code
5. TESTING CONSIDERATIONS: Explain how your solution handles the examples and edge cases

ALWAYS provide the most EFFICIENT solution possible:
- Explicitly state the time and space complexity of your solution using Big O notation
- Explain WHY your solution has that complexity
- Optimize algorithms for the specific problem constraints
- Choose the most appropriate data structures for the task
- Avoid unnecessary operations or memory usage
- Consider edge cases, scale, and potential bottlenecks
- Include alternatives if there are multiple approaches with different trade-offs

Focus on:
- Breaking down problems into clear steps with explanations for each
- Providing clean, efficient, production-ready code
- Including detailed comments within code to explain functionality and efficiency considerations
- Following best practices and design patterns
- Handling edge cases and potential errors
- Writing code that is easy to maintain and extend

Always provide the COMPLETE working solution with a professional level of quality and optimization.
Ensure your solution code handles EVERY example in the problem statement."""
        
        # Format based on content type
        if "screenshot" in question.lower():
            if mode == "suggester":
                system_message += """
You're analyzing a screenshot captured by the user.
Identify patterns, potential issues, and inefficiencies in the code shown.
Analyze the time and space complexity of the existing code.
Provide step-by-step guidance with small code snippets that illustrate more efficient approaches.
Help the user understand HOW to optimize the solution rather than just giving them a solution.
Always analyze the code for efficiency improvements and optimization opportunities."""
            elif mode == "solver":
                system_message += """
You're analyzing a screenshot captured by the user.
First analyze the problem seen in the code, then explain your approach before providing a complete solution.
Your solution must include:
1. Analysis of what you're seeing and any inefficiencies in the current code with explicit complexity analysis
2. Your approach to solving it with optimizations and why they improve performance
3. Step-by-step implementation details with complexity considerations
4. Complete, well-commented code solution optimized for performance
5. Testing considerations and detailed complexity analysis"""
            else:
                system_message += """
You're analyzing a screenshot captured by the user.
Provide helpful information about what's shown in a balanced way.
Always look for opportunities to improve efficiency and optimize the code shown.
Include specific recommendations for performance improvements with explanations."""
        
        elif "continuous monitoring" in question.lower():
            if mode == "suggester": 
                system_message += """
You're analyzing content captured near the user's cursor during continuous monitoring.
Provide immediate guidance with step-by-step explanations and small code snippets that illustrate important concepts.
Always look for optimization opportunities and suggest more efficient alternatives with clear explanations of the performance benefits."""
            elif mode == "solver":
                system_message += """
You're analyzing content captured near the user's cursor during continuous monitoring.
Provide a comprehensive solution that includes problem analysis, approach overview, 
step-by-step implementation, full code solution with comments, and testing considerations.
Always prioritize efficiency and optimization in your suggested solutions.
Explicitly state the time and space complexity of your solution and explain why it's optimal."""
            else:
                system_message += """
You're analyzing content captured near the user's cursor during continuous monitoring.
Focus on providing immediate insights or suggestions about what's visible.
Highlight any potential performance issues or optimization opportunities.
Suggest efficiency improvements with clear explanations of the benefits."""
        
        # Prepare full prompt
        full_prompt = f"{system_message}\n\nQuestion/Content: {question}"
        return full_prompt
    
    def generate_response(self, question_data):
        """Generate response with error handling and demo mode fallback."""
        # Unpack the question data
        if isinstance(question_data, dict):
            question = question_data.get('text', '')
            mode = question_data.get('mode', 'normal')
            response_id = question_data.get('response_id', None)
        else:
            # For backward compatibility
            question = question_data
            mode = 'normal'
            response_id = None
            
        if not question:
            return "Please provide a question."
            
        if self.demo_mode:
            # In demo mode, simulate streaming with chunks for better UX
            return self._generate_demo_response_streaming(question, mode, response_id)
            
        try:
            # Add rate limiting
            max_retries = 2
            retry_delay = 1
            
            for attempt in range(max_retries):
                try:
                    # Format prompt with better context handling based on mode
                    input_text = self._format_prompt(question_data)
                    
                    # Stream responses in chunks
                    self._stream_response(input_text, mode, response_id)
                    
                    # Return empty string as the real response was streamed
                    return ""
                    
                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg and attempt < max_retries - 1:
                        self.logger.warning(f"Rate limit hit, retrying in {retry_delay}s")
                        time.sleep(retry_delay)
                        retry_delay *= 2
                        continue
                    raise e
                    
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"OpenAI API error: {error_msg}")
            
            # Send error as a response chunk
            error_response = f"⚠️ OpenAI API error: {error_msg}\n\nFalling back to demo mode."
            self.event_bus.publish(Events.RESPONSE_CHUNK, {
                'text': error_response,
                'response_id': response_id,
                'is_final': False
            })
            
            # Switch to demo mode for this response
            return self._generate_demo_response_streaming(question, mode, response_id)
    
    def _stream_response(self, input_text, mode, response_id):
        """Stream response from LLM with chunks sent to UI."""
        try:
            print(f"DEBUG: Starting streaming response with ID: {response_id}")
            full_response = ""
            chunk_size = 150  # Increased further for better handling of code blocks
            buffer = ""
            timeout = 60  # Increased timeout for large responses
            
            # Track code block state and content
            in_code_block = False
            code_buffer = ""
            code_language = None
            
            # Use callback handler in streaming mode
            for chunk in self.chat_model.stream(input_text, timeout=timeout):
                if not chunk.content:
                    continue
                
                current_content = chunk.content
                full_response += current_content
                
                # Check for code block markers
                if "```" in current_content:
                    # Count occurrences to handle multiple markers in a single chunk
                    markers = current_content.count("```")
                    
                    if not in_code_block and markers % 2 == 1:
                        # Starting a new code block
                        in_code_block = True
                        
                        # Find the position of the first marker
                        start_pos = current_content.find("```")
                        
                        # Add content before the code block to the buffer
                        if start_pos > 0:
                            buffer += current_content[:start_pos]
                            
                        # Check if there's a language specified
                        rest = current_content[start_pos+3:]
                        first_newline = rest.find("\n")
                        if first_newline != -1:
                            code_language = rest[:first_newline].strip()
                            code_buffer = rest[first_newline+1:]
                        else:
                            code_language = None
                            code_buffer = ""
                    
                    elif in_code_block and markers % 2 == 1:
                        # Ending a code block
                        in_code_block = False
                        
                        # Find the position of the closing marker
                        end_pos = current_content.find("```")
                        
                        # Add content before the closing marker to the code buffer
                        if end_pos > 0:
                            code_buffer += current_content[:end_pos]
                        
                        # Emit the complete code block
                        buffer += f"```{code_language or ''}\n{code_buffer}\n```"
                        
                        # After a complete code block, immediately emit the buffer
                        # to ensure code blocks are delivered as complete units
                        self._emit_chunk(buffer, response_id)
                        buffer = ""
                        
                        code_buffer = ""
                        code_language = None
                        
                        # Add content after the closing marker to the buffer
                        if end_pos + 3 < len(current_content):
                            buffer += current_content[end_pos+3:]
                    
                    else:
                        # Even number of markers in a single chunk - handle complete code blocks
                        if not in_code_block:
                            buffer += current_content
                        else:
                            code_buffer += current_content
                else:
                    # No code block markers in this chunk
                    if in_code_block:
                        code_buffer += current_content
                    else:
                        buffer += current_content
                
                # Check if we should emit a chunk
                if not in_code_block and len(buffer) >= chunk_size:
                    # Find a good breaking point
                    breaking_points = ['. ', '! ', '? ', ':', '\n\n', '. \n', '! \n', '? \n']
                    best_break = len(buffer)
                    
                    for point in breaking_points:
                        last_idx = buffer.rfind(point, max(0, best_break - chunk_size * 2))
                        if last_idx != -1 and last_idx < best_break:
                            best_break = last_idx + len(point)
                    
                    # If we couldn't find a good breaking point, take what we have
                    if best_break == len(buffer):
                        chunk_to_emit = buffer
                        buffer = ""
                    else:
                        chunk_to_emit = buffer[:best_break]
                        buffer = buffer[best_break:]
                    
                    if chunk_to_emit:
                        self._emit_chunk(chunk_to_emit, response_id)
            
            # Emit any remaining content
            if in_code_block:
                # Handle a code block that didn't close properly
                print(f"DEBUG: Handling unclosed code block, adding closing marker")
                buffer += f"```{code_language or ''}\n{code_buffer}\n```"
            
            if buffer:
                self._emit_chunk(buffer, response_id)
            
            # Mark the streaming as complete
            print(f"DEBUG: Marking streaming complete for ID: {response_id}")
            self.event_bus.publish(Events.RESPONSE_CHUNK, {
                'text': '',
                'response_id': response_id,
                'is_final': True
            })
            
        except Exception as e:
            self.logger.error(f"Error in streaming response: {e}")
            print(f"DEBUG: Error in streaming response: {e}")
            # Send error message as a chunk
            self.event_bus.publish(Events.RESPONSE_CHUNK, {
                'text': f"\n\n⚠️ Error during streaming: {str(e)}",
                'response_id': response_id,
                'is_final': True
            })
    
    def _should_emit_chunk(self, buffer, in_code_block, in_list, chunk_size):
        """Determine if the current buffer should be emitted as a chunk."""
        # Don't emit empty buffers
        if not buffer:
            return False
        
        # Don't emit if we're in a structure that shouldn't be broken
        if in_code_block:
            return False
        
        # Basic size check
        if len(buffer) >= chunk_size:
            # For lists, try to find good breaking points
            if in_list:
                # Look for a newline that's not followed by a list marker
                lines = buffer.split('\n')
                for i in range(len(lines) - 1):
                    if lines[i].strip() and not any(lines[i+1].strip().startswith(x) for x in ['-', '1', '2', '3', '4', '5', '6', '7', '8', '9']):
                        return True
                # If buffer is getting very large, emit anyway
                return len(buffer) >= chunk_size * 2
            return True
        
        # Check for natural breaking points
        sentence_endings = ['. ', '! ', '? ', ':', '\n\n']
        for ending in sentence_endings:
            if ending in buffer[-3:]:
                # Don't break in the middle of a formatting marker
                for marker in ['```', '##', '###', '- ', '**', '*', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.']:
                    if buffer.endswith(marker[:len(buffer) % len(marker)]):
                        return False
                return True
        
        return False
    
    def _emit_chunk(self, chunk, response_id):
        """Emit a chunk to the UI."""
        if not chunk:
            return
        
        print(f"DEBUG: Publishing chunk of size {len(chunk)}")
        self.event_bus.publish(Events.RESPONSE_CHUNK, {
            'text': chunk,
            'response_id': response_id,
            'is_final': False
        })
        
        # Small delay between chunks for readability
        time.sleep(0.08)
    
    def _generate_demo_response_streaming(self, question, mode="normal", response_id=None):
        """Generate a demo response with simulated streaming when API is unavailable."""
        # Get the full demo response
        full_response = self._generate_demo_response(question, mode)
        
        print(f"DEBUG: Generating demo response with ID: {response_id}")
        
        # If no response ID, just return the full response (backward compatibility)
        if not response_id:
            return full_response
            
        # Simulate streaming with chunks
        words = full_response.split()
        buffer = ""
        chunk_size = random.randint(3, 8)  # Random number of words per chunk
        
        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i+chunk_size]
            chunk = " ".join(chunk_words)
            buffer += chunk + " "
            
            # Send chunk
            print(f"DEBUG: Publishing demo chunk of size {len(chunk)}")
            self.event_bus.publish(Events.RESPONSE_CHUNK, {
                'text': chunk + " ",
                'response_id': response_id,
                'is_final': False
            })
            
            # Simulate typing delay
            time.sleep(0.1)
        
        # Mark streaming as complete
        print(f"DEBUG: Marking demo streaming complete for ID: {response_id}")
        self.event_bus.publish(Events.RESPONSE_CHUNK, {
            'text': '',
            'response_id': response_id,
            'is_final': True
        })
        
        return ""  # Return empty string since we streamed the response
    
    def _format_suggester_response(self, response):
        """Format the response for suggester mode with minimal formatting."""
        # Check if response already has a step-by-step structure
        if "Step 1:" not in response and "### Step 1:" not in response and "1. " not in response:
            # Add step-by-step structure
            sections = response.split("\n\n")
            
            formatted_sections = []
            formatted_sections.append("# Concept Overview")
            formatted_sections.append(sections[0] if sections else "Let's understand the key concepts first.")
            
            formatted_sections.append("# Step-by-Step Guidance")
            
            # Add steps
            step_count = 1
            for i in range(1, min(len(sections), 4)):
                if sections[i].strip():
                    formatted_sections.append(f"## Step {step_count}")
                    formatted_sections.append(f"{sections[i]}")
                    step_count += 1
            
            # Add practice suggestions
            formatted_sections.append("# Practice Suggestions")
            formatted_sections.append("Try implementing the solution by following these steps. Here are some additional tips:")
            formatted_sections.append("- Start with a simple example and test each step")
            formatted_sections.append("- Pay attention to the logic flow and error handling")
            formatted_sections.append("- Test your solution with different inputs")
            
            return "\n\n".join(formatted_sections)
        
        return response
        
    def _format_solver_response(self, response):
        """Format the response for solver mode with minimal formatting."""
        # Check if response already has the required structure
        required_sections = ["Problem Analysis", "Approach Overview", "Step-by-Step Implementation", 
                            "Complete Solution", "Testing Considerations"]
        has_structure = True
        for section in required_sections:
            if section.lower() not in response.lower() and section.replace(" ", "-").lower() not in response.lower():
                has_structure = False
                break
        
        if not has_structure:
            # Add structured format
            sections = response.split("\n\n")
            
            formatted_sections = []
            formatted_sections.append("# Complete Solution")
            
            # Problem Analysis
            formatted_sections.append("## Problem Analysis")
            formatted_sections.append(sections[0] if sections else "Let's analyze the problem carefully.")
            
            # Approach Overview
            formatted_sections.append("## Approach Overview")
            if len(sections) > 1:
                formatted_sections.append(sections[1])
            else:
                formatted_sections.append("Here's my strategy for solving this problem.")
            
            # Step-by-Step Implementation
            formatted_sections.append("## Step-by-Step Implementation")
            step_count = 1
            for i in range(2, min(len(sections), 5)):
                if sections[i].strip() and "```" not in sections[i]:
                    formatted_sections.append(f"### Step {step_count}")
                    formatted_sections.append(f"{sections[i]}")
                    step_count += 1
            
            # Complete Code Solution
            formatted_sections.append("## Complete Code Solution")
            code_found = False
            for section in sections:
                if "```" in section:
                    formatted_sections.append("Here's the complete implementation with detailed comments:")
                    formatted_sections.append(section)
                    code_found = True
                    break
            
            if not code_found:
                formatted_sections.append("Here's the implementation:")
                formatted_sections.append("```python\n# Implementation with detailed comments\n```")
            
            # Complexity Analysis
            formatted_sections.append("## Complexity Analysis")
            formatted_sections.append("- **Time Complexity**: O(?)\n- **Space Complexity**: O(?)\n\nPlease see the inline comments for detailed analysis.")
            
            # Testing Considerations
            formatted_sections.append("## Example Test Cases")
            if len(sections) > 5:
                formatted_sections.append(sections[-1])
            else:
                formatted_sections.append("The solution correctly handles all the provided examples and common edge cases.")
            
            return "\n\n".join(formatted_sections)
        
        return response
    
    def _generate_demo_response(self, question, mode="normal"):
        """Generate a demo response when API is unavailable."""
        question_lower = question.lower()
        
        # Handle different modes
        mode_prefix = ""
        if mode == "suggester":
            mode_prefix = "## Teacher Mode Activated\n\nI'm providing guidance to help you learn, without giving away complete solutions.\n\n"
        elif mode == "solver":
            mode_prefix = "## Solution Mode Activated\n\nI'm providing a complete solution with detailed explanations.\n\n"
        
        # Handle screen monitoring or screenshot analysis in demo mode
        if "screenshot" in question_lower or "continuous monitoring" in question_lower:
            if mode == "suggester":
                return mode_prefix + """I've analyzed your screen content in teacher mode.

I can see some code that appears to have a few issues to address:

### Concepts to Review:
- Variable scope and lifetime
- Error handling patterns
- Control flow structures

### Hints (without giving the solution):
1. Look at how your variables are being initialized
2. Consider what happens if certain conditions aren't met
3. Think about error cases that might occur

Try to identify these issues yourself first, then implement a solution based on these principles."""
            elif mode == "solver":
                return mode_prefix + """# Complete Solution

## Problem Analysis
I can see code in your screenshot that has several issues to fix. The main problems appear to be:
- Improper error handling
- Variable scope issues
- Inefficient algorithm implementation

## Step-by-Step Approach

### Step 1: Fix the error handling
The current error handling is incomplete. We need to add proper try/except blocks.

### Step 2: Resolve variable scope issues
Some variables are being accessed before initialization or outside their scope.

### Step 3: Optimize the algorithm
The current implementation has O(n²) complexity, but we can improve it.

## Implemented Solution
```python
def improved_function(data):
    # Initialize with default values
    result = []
    
    try:
        # Process the data more efficiently
        for item in data:
            # Properly handle each item
            processed = item * 2
            result.append(processed)
            
    except TypeError as e:
        # Proper error handling
        print(f"Error processing data: {e}")
        return None
        
    return result
```

## Summary
This solution fixes the main issues by implementing proper error handling, ensuring variables are correctly scoped, and optimizing the algorithm for better performance."""
            else:
                return """I'm analyzing the screen content in demo mode.

I can see what appears to be some code or text in your screenshot. 
In regular mode, I would provide specific suggestions about:
- Code quality and potential bugs
- Performance optimization opportunities
- Best practices for the language detected
- Documentation suggestions

To enable full functionality:
1. Configure a valid OpenAI API key in your settings
2. Ensure you have proper API credits
3. Restart the application"""
        
        if "python" in question_lower:
            return mode_prefix + """Python is a versatile programming language known for its readability and simplicity.

Some key Python features:
- Dynamic typing
- Indentation-based syntax
- Rich standard library
- Great for beginners and experts alike

Here's a simple example:
```python
def greet(name):
    return f"Hello, {name}!"

print(greet("World"))
```

You can try running this code to see the output!"""
        
        elif "javascript" in question_lower or "js" in question_lower:
            return mode_prefix + """JavaScript is a programming language commonly used for web development.

Key features:
- Client-side scripting
- Event-driven programming
- Asynchronous capabilities with Promises
- Object-oriented with prototypal inheritance

Example:
```javascript
function greet(name) {
  return `Hello, ${name}!`;
}

console.log(greet("World"));
```"""
        
        elif "html" in question_lower or "css" in question_lower:
            return mode_prefix + """HTML and CSS are the foundation of web development.

HTML provides the structure:
```html
<!DOCTYPE html>
<html>
<head>
    <title>My Page</title>
</head>
<body>
    <h1>Hello World</h1>
    <p>This is a paragraph.</p>
</body>
</html>
```

CSS provides the styling:
```css
body {
    font-family: Arial, sans-serif;
    background-color: #f0f0f0;
}
h1 {
    color: #333;
}
```"""
        
        elif "git" in question_lower:
            return mode_prefix + """Git is a distributed version control system.

Common Git commands:
```
git init            # Initialize a repository
git clone <url>     # Clone a repository
git add .           # Stage all changes
git commit -m "msg" # Commit changes
git push            # Push to remote
git pull            # Pull from remote
```

Git helps teams collaborate on code effectively."""
        
        else:
            # Generic response based on mode
            if mode == "suggester":
                return """## Teacher Mode (Demo)

I'm currently in demo mode due to API limitations, but I'm in teacher mode.

In this mode, I would:
- Provide guidance without giving complete solutions
- Explain concepts and principles
- Help you understand how to solve problems yourself
- Correct minor issues while explaining the reasoning

To get full functionality:
1. Configure a valid OpenAI API key in your settings
2. Ensure you have proper API credits
3. Restart the application"""
            elif mode == "solver":
                return """## Solution Mode (Demo)

I'm currently in demo mode due to API limitations, but I'm in solution mode.

In this mode, I would:
- Provide complete, detailed solutions
- Include explanations for each step
- Present well-commented code
- Ensure the solution is production-ready

To get full functionality:
1. Configure a valid OpenAI API key in your settings
2. Ensure you have proper API credits
3. Restart the application"""
            else:
                # Generic response
                return f"""I'm currently in demo mode due to API limitations.

Your question was about: "{question}"

To get a proper response:
1. Configure a valid OpenAI API key in your settings
2. Ensure you have proper API credits
3. Restart the application

In the meantime, you can try asking about Python, JavaScript, HTML/CSS, or Git for some prepared demo responses."""
            
    def on_settings_changed(self, settings):
        """Handle settings changes, especially API key updates."""
        api_key = settings.get('openai_api_key')
        if api_key != self.api_key:
            self.api_key = api_key
            self._initialize_llm()
            
            # Notify UI of demo mode change
            self.event_bus.publish(Events.SETTINGS_CHANGED, {'demo_mode': self.demo_mode}) 