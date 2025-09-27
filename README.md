# 📚 EasyRead: *"Where great books meet great fluency"*

Built for the **Open-Source Foundations for Founders: AI You Can Build On (Apertus)** hackathon, this project transforms your favorite books into an immersive, trustworthy language-learning experience powered by **open-source** models and infrastructure.

## 🌟 Overview

EasyRead is a safe, engaging platform for language learners of all levels. Users can select books they genuinely enjoy or would love to discover, and have them adapted to their target language and proficiency level (A1, A2, B1, B2, C1, C2). The application enhances the learning journey with integrated audiobook functionality and interactive quizzes throughout the text, creating a comprehensive learning experience.

## 🚀 Innovation and Future

EasyRead is built on top of **Apertus**, a cutting-edge language model with unique advantages:

- **Fully Open Model**: Complete transparency with open weights, open data, and comprehensive training documentation
- **Massively Multilingual**: Native support for 1,811 languages, making our solution truly global
- **Ethically Compliant**: Respects opt-out consent of data owners (even retrospectively) and avoids memorization of training data

Learn more: [Apertus Documentation](https://huggingface.co/docs/transformers/en/model_doc/apertus)

This technology promises to promote language education worldwide through open-source principles, safety guarantees, and explainable AI.


## 💼 Market Opportunity

With its foundation in open-source literature, EasyRead presents a potential billion-dollar opportunity through strategic partnerships with governmental education initiatives and commercial collaborations with platforms like Amazon. These partnerships would expand our library to include modern authors' works, significantly broadening our market reach while maintaining our educational mission.

---



## 🛠️ Setup Instructions

### 🔑 Swisscom Keys

To use the Swisscom API keys, you must follow their [Fair Use Policy](https://zh.swiss-ai-weeks.ch/tools/fair-use-policy-to-use-apertus-on-the-swisscom-plattform).  
Refer to the [Quickstart Guide](https://zh.swiss-ai-weeks.ch/tools/swiss-ai-platform-quickstart-guide) for detailed instructions.

Add your Swisscom API key to a `.env` file at the root of the project:
```plaintext
SWISS_AI_PLATFORM_API_KEY=your_api_key_here
```


### 1. Create a Virtual Environment
Run the following command to create a virtual environment:
```bash
python3 -m venv book_env
```

### 2. Activate the Virtual Environment
- On macOS/Linux:
  ```bash
  source book_env/bin/activate
  ```
- On Windows:
  ```bash
  book_env\Scripts\activate
  ```

### 3. Install Dependencies
Install the required libraries using UV:
```bash
uv sync --active
```
To add new dependencies, use:
```bash
uv add <package_name> --active
```
or manually edit the `pyproject.toml` file and then run:
```bash
uv sync --active
```
---


## ▶️ Running the Script

Once the environment is set up, run the Streamlit app:
```bash
python -m streamlit run frontend/app.py
```
---

## 🛑 Deactivating the Virtual Environment

When you're done, deactivate the virtual environment:
```bash
deactivate
```
---
