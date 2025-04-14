```markdown
# Information Retrieval System  
A Streamlit app for PDF-based Q&A using Google's Gemini AI and LangChain.

---

## 📌 Declaration
This project is open for use under the MIT License. You are free to:
- Use the code for personal or commercial projects.
- Modify the implementation to suit your needs.
- Share your improvements with the community.

Please attribute the original work by linking back to this repository.

---

## 📂 File Structure
```bach
.
├── app.py               # Main Streamlit application
├── src/
│   ├── helper.py        # Helper functions (PDF processing, embeddings, etc.)
├── requirements.txt     # Python dependencies
├── research/
│   ├── trials.ipynb     # Jupyter notebook for testing components
├── .env.example         # Template for environment variables
└── README.md            # This file
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.9+
- Google API Key (for Gemini AI)

### 2. Installation
Clone the repository and install the dependencies:
```bash
git clone https://github.com/ammarmashal/Information-Retrieval-System-.git
cd your-repo
pip install -r requirements.txt
```

### 3. Configure Environment
Rename `.env.example` to `.env` and add your Google API key:
```env
GOOGLE_API_KEY=your_api_key_here
```

### 4. Run the App
Start the Streamlit app:
```bash
streamlit run app.py
```
Access the app at [http://localhost:8501](http://localhost:8501).

---

## 🔧 Key Functions (`helper.py`)
| Function                  | Description                                      |
|---------------------------|--------------------------------------------------|
| `get_pdf_text()`          | Extracts text from uploaded PDFs.                |
| `get_text_chunks()`       | Splits text into manageable chunks.              |
| `get_vector_store()`      | Generates embeddings using Gemini AI.            |
| `get_conversational_chain()` | Sets up the AI chat interface.                 |

---

## 🧪 Testing (`trials.ipynb`)
The Jupyter notebook includes:
- Component tests (e.g., PDF text extraction).
- Debugging snippets for embeddings and LLM calls.
- Sample queries to validate functionality.

---

## 💡 Customization
- **Adjust Quota Limits**: Modify `MAX_QUESTIONS` and `QUOTA_RESET_MINUTES` in `app.py`.
- **Change AI Model**: Swap `gemini-1.5-pro` for other models in `get_conversational_chain()`.
- **Add Storage**: Integrate a database (e.g., SQLite) for persistent chat history.

---

## 📜 License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## 🙏 Acknowledgments
- Built with [Streamlit](https://streamlit.io/) and [LangChain](https://langchain.com/).
- Uses Google's Gemini AI for embeddings and chat.

---

This updated README ensures:
✅ Clear attribution (license + declaration).  
✅ Easy setup (with requirements.txt and .env template).  
✅ Documented components (helper.py functions, trials.ipynb purpose).  
✅ Customization hints for advanced users.
```

### Key Adjustments:
1. **File Structure**: Updated to reflect your project structure.
2. **Quick Start**: Simplified and clarified installation and setup steps.
3. **Key Functions**: Added descriptions for the functions in `helper.py`.
4. **Testing Section**: Highlighted the purpose of trials.ipynb.
5. **Customization**: Added hints for modifying quota limits, AI models, and storage.
6. **Acknowledgments**: Properly credited tools and APIs used in the project.
