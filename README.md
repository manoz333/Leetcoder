# Leetcoder

A simple AI coding assistant to help with programming problems and LeetCode challenges.

## Features

- **Dual Modes**: Suggester (for hints) and Solver (for complete solutions)
- **Multiple Input Methods**: Text, screenshot, voice, and screen monitoring
- **Smart Responses**: Line-by-line code explanations using GPT-4o
- **Clean UI**: Minimalist interface with syntax highlighting

## Quick Start

1. Clone the repo:
```bash
git clone https://github.com/manoz333/Leetcoder.git
cd Leetcoder
```

2. Set up environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r ambient-assistant-mac/requirements.txt
```

3. Add OpenAI API key to `ambient-assistant-mac/.env`:
```
OPENAI_API_KEY=your_api_key_here
```

4. Run:
```bash
python -m ambient.app
```

## Usage Tips

- Use **Suggester Mode** for learning concepts
- Use **Solver Mode** for complete solutions with comments
- Press `Cmd+Enter` to submit questions
- Try screenshot capture for quick code analysis

## License

MIT License - See LICENSE file 