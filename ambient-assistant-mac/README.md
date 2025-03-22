# Ambient Assistant

An intelligent ambient assistant for macOS that observes your screen, detects questions, and provides helpful responses using advanced language models.

## 🌟 Features

- **Ambient Intelligence**: Monitors your screen and automatically detects when you ask questions
- **Context-Aware Responses**: Uses the content on your screen to provide more relevant answers
- **Multiple LLM Support**: Works with OpenAI, Anthropic, and DeepSeek models
- **Privacy-First Design**: All processing happens locally when possible, with configurable retention policies
- **Elegant UI**: Beautiful, non-intrusive floating response window with customizable appearance
- **Keyboard Shortcuts**: Quick access to the assistant with customizable shortcuts
- **Customizable Settings**: Configure the behavior, appearance, and privacy settings to suit your needs

## 🚀 Installation

### Prerequisites

- macOS 11 (Big Sur) or later
- Python 3.9+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (optional, for improved text recognition)

### Option 1: Install from source

```bash
# Clone the repository
git clone https://github.com/ambient-team/ambient-assistant.git
cd ambient-assistant

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install the package
pip install -e .

# Run the assistant
ambient-assistant
```

### Option 2: Install using pip

```bash
# Install from PyPI
pip install ambient-assistant

# Run the assistant
ambient-assistant
```

### Option 3: Download the App Bundle

1. Download the latest app bundle from the [releases page](https://github.com/ambient-team/ambient-assistant/releases)
2. Move the app to your Applications folder
3. Open the app

## ⚙️ Configuration

On first launch, you'll be prompted to:

1. Grant necessary permissions (accessibility, screen recording)
2. Configure your API keys for language models
3. Choose your preferred settings

You can access the settings window at any time by clicking the tray icon and selecting "Settings".

### Required API Keys

To use the assistant with online language models, you'll need to obtain API keys from:

- [OpenAI](https://platform.openai.com/)
- [Anthropic](https://anthropic.com/)
- [DeepSeek](https://deepseek.com/)

Add these keys in the Settings window under the "Models" tab.

## 🔧 Usage

### Basic Usage

1. Launch the application
2. The assistant will appear in your system tray (top menu bar)
3. Ask a question in any application by typing a question mark followed by your question
4. The assistant will detect your question, analyze the context, and show a response window

### Keyboard Shortcuts

- **Cmd+Shift+Space**: Toggle the response window visibility
- **Esc**: Hide the response window
- **Custom Shortcut**: Configure your own shortcut in settings

### Feedback

After each response, you can provide feedback using the 👍 or 👎 buttons in the response window.

## 🛡️ Privacy

Ambient Assistant is designed with privacy in mind:

- Screen content is processed locally on your device
- API requests only include the minimum context needed for accurate responses
- You can configure data retention policies in the settings
- The application can be paused automatically when screen sharing is detected

## 🧩 Architecture

Ambient Assistant is built with a modular architecture:

- **Core**: Event bus, settings manager, app manager
- **UI**: Tray icon, response window, settings window
- **Processing**: Screen capture, OCR, question detection, app detection
- **LLM**: Model integration, context building, prompt construction, memory management
- **Storage**: Django-based persistent storage for conversations and settings

## 🤝 Contributing

Contributions are welcome! Please check out our [contribution guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Documentation

Full documentation is available at [docs.ambient-assistant.com](https://docs.ambient-assistant.com).

## 🙏 Acknowledgements

- OpenAI, Anthropic, and DeepSeek for their powerful language models
- The PyQt, Django, and LangChain projects
- All our contributors and supporters
