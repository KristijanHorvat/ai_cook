# AI Cook Assistant

---

## Project Overview

**AI Cook Assistant** is a smart meal creation tool designed to help users prepare meals based on the ingredients they have and their dietary preferences.

### Key Features:

1. **Ingredient-Based Meal Suggestions**:

   - Users input available ingredients (e.g., chicken 250g, rice 100g, curry 50g) and desired nutritional targets (e.g., proteins, fats, and calories).
     
      > e.g. _For lunch, I have chicken, rice, and curry. The chicken is 200 grams, rice is 100 grams, and curry is 50 grams. I need 600 calories, 60 grams of protein and 20 grams of fat._
   - The assistant generates tailored meal ideas.
2. **Recipe Generation**:

   - Recipes include detailed instructions, ingredients, and nutritive breakdown (macros: proteins, fats, carbohydrates, and calories).
3. **Local Recipe Storage**:

   - Recipes and data are stored locally using a vector database for efficient retrieval.
4. **Advanced AI Integration**:

   - Utilizes large language models (LLMs) for recipe generation.
   - Employs OpenAI-based retrieval systems for contextual recommendations.

This project is designed to make meal planning efficient, healthy, and fun by combining advanced AI technologies with user-friendly design.

### Tech Stack

This project leverages a combination of tools and technologies:

- **Backend**: Flask API for handling requests.
- **Database**: Weaviate for storing and retrieving vectorized data.
- **Local LLMs**: Managed using Ollama for running models like `llama3.2` and `nomic-embed-text`.
- **Mobile App**: Built with Flutter to provide a seamless user interface.

---

## Project Setup

### Prerequisites

Ensure you have the following installed on your system before proceeding:

1. **Python**: Version 3.11 or above.
   - [Download Python](https://www.python.org/downloads/)
2. **Docker**: For running the Weaviate database.
   - [Install Docker](https://docs.docker.com/get-docker/)
3. **Docker Compose**: For managing Docker containers.
   - [Install Docker Compose](https://docs.docker.com/compose/install/)
4. **Pip**: Python package manager for installing dependencies.
5. **Ollama**: A tool for running and managing LLMs locally.
   - Instructions are provided in the **Ollama Setup** section.
6. **Flutter**: For the mobile application development.
   - [Install Flutter](https://docs.flutter.dev/get-started/install)

---

### Setup Instructions

#### Step 1: Clone the Repository

```bash
git clone git@github.com:KristijanHorvat/ai_cook.git
cd ai_cook
```

#### Step 2: Install Python Dependencies

1. Create a virtual environment (or use existing inside _backend_ and _db_):

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows, use `venv\\Scripts\\activate`
   ```
2. Install required Python libraries (once in _backend_, once in _db_):

   ```bash
   pip install -r requirements.txt
   ```

---

#### Step 3: Ollama Setup

Ollama is a tool to run local language models. Follow these steps:

1. **Install Ollama**:Run the following command to install Ollama:

   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```
2. **Start Ollama**:Once installed, start the Ollama service:

   ```bash
   ollama start
   ```
3. **Pull Required Models**:
   Download the required models for embedding and text generation:

   ```bash
   ollama pull llama3.2
   ollama pull nomic-embed-text
   ```

   > **Note**: Ensure Ollama is running before pulling models. Use `ollama list` to verify the models are downloaded.
   >

---

#### Step 4: Database Setup with Weaviate

Weaviate is an open-source vector database. The setup involves running it in a Docker container.

1. **Start Weaviate in a Docker Container**:

   ```bash
   docker-compose up -d
   ```

   This command will pull the necessary Docker image and start the Weaviate database.
2. **Populate the Database**:
   Once the database is running, populate it with the required data using the provided script:

   ```bash
   python populate_db.py
   ```

---

#### Step 5: Backend Setup

The backend is a Flask application that interacts with the database and handles API requests.

1. Start the Flask backend:

   ```bash
   python backend.py
   ```
2. The backend will run locally, typically on `http://127.0.0.1:8090`.

---

#### Step 6: Mobile App Setup

The mobile application is built using Flutter. Follow these steps to set it up:

1. Navigate to the Flutter project directory:

   ```bash
   cd mobile-app
   ```
2. Install Flutter dependencies:

   ```bash
   flutter pub get
   ```
3. Build and Run the Flutter application:

   ```bash
   flutter build
   ```
   ```bash
   flutter run
   ```

   > **Note**: Ensure that your emulator or physical device is properly set up and connected.
   > 
   > **Note**: For iOS builds, run `flutter build ios` before running the app.
   > 
   > **Note**: If running iOS fails, try running the app with Xcode.

---

### Additional Notes

#### Requirements Description

- **requests**: For making HTTP requests in Python.
- **urllib3**: A powerful library for working with HTTP/1.1.
- **python-dotenv**: For managing environment variables.
- **weaviate-client**: Python client for interacting with the Weaviate database.
- **flask**: A lightweight web framework for the backend.
- **ollama**: A tool to run LLMs locally.
- **numpy**: For numerical computations.
- **pandas**: For data manipulation and analysis.

### Troubleshooting

1. **Docker Issues**:Ensure Docker Desktop is running and has sufficient resources (e.g., memory and CPUs) allocated for the container.
2. **Ollama Errors**:

   - If Ollama fails to start, verify that it is installed correctly by running `ollama --version`.
   - Ensure the required models are downloaded with `ollama list`.
3. **Flutter Issues**:If `flutter run` fails:

   - Verify your emulator or device is connected.
   - Run `flutter doctor` to check for any missing dependencies.

---
