# 💖 CuteBot: A Custom Trigger & NLP Discord Bot

A customizable Discord bot built in Python that sends cute messages, fetches animal pictures, and uses Natural Language Processing (NLP) to suggest custom conversation triggers based on chat history.

## ✨ Features
* **Custom Triggers:** Users can set a specific "partner" and add custom text triggers that the bot will automatically reply to.
* **Smart Suggestions (NLP):** Analyzes logged messages to suggest the most frequently used words as new triggers (supports English and Hinglish).
* **Cute APIs:** Fetch random cat (`!cat`) and dog (`!dog`) pictures.
* **Shipping:** Send love and random kissing GIFs to other users (`!ship @user`).
* **Privacy First:** Message logging must be explicitly toggled on (`!togglelog`) and can be managed per user.

## 🛠️ Prerequisites
You will need Python 3.8+ and the following libraries:
* `discord.py`
* `aiohttp`
* `nltk`
* `python-dotenv`

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
   cd your-repo-name