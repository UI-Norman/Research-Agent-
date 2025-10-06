# Credibility-Aware Research Agent

A Streamlit-based application that performs credibility-aware research on a given topic, analyzing claims from web sources and uploaded documents. The agent evaluates the credibility of claims, generates a research report, and allows updates with new information.

## Features
- **Web Research**: Conducts research on a user-provided topic using the Serper API to fetch web results.
- **Claim Extraction**: Extracts factual claims from web content or uploaded files (.txt or .md).
- **Credibility Analysis**: Scores claims based on source type, language, bias, and context, providing a credibility score (0-10).
- **Report Generation**: Produces a detailed report summarizing high and medium credibility claims.
- **Research Updates**: Supports updating existing research with new claims from uploaded files.
- **Streamlit UI**: User-friendly interface for entering topics, viewing reports, and uploading files.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/credibility-research-agent.git
   cd credibility-research-agent
   ```

2. **Install Dependencies**:
   Ensure Python 3.8+ is installed, then install required packages:
   ```bash
   pip install -r requirements.txt
   ```

   Required packages:
   - `streamlit`
   - `langchain`
   - `langchain-google-genai`
   - `requests`
   - `python-dotenv`

3. **Set Up Environment Variables**:
   Create a `.env` file in the project root with the following:
   ```
   GOOGLE_API_KEY=your-google-api-key
   SERPER_API_KEY=your-serper-api-key
   ```
   - Obtain a Google API key from [Google MakerSuite](https://makersuite.google.com/app/apikey).
   - Obtain a Serper API key from [Serper.dev](https://serper.dev/) (optional; mock data used if not provided).

4. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

## Usage
1. **Launch the App**:
   Open the app in your browser (typically at `http://localhost:8501`).

2. **Enter a Research Topic**:
   Input a topic (e.g., "What is the meaning of life") and click "Research" to generate a report.

3. **View Results**:
   - The report displays high and medium credibility claims, an overall credibility score, and the number of sources analyzed.
   - Claims are marked with their credibility scores and recommended actions (INCLUDE, INCLUDE_WITH_WARNING, EXCLUDE).

4. **Update Research**:
   Upload a `.txt` or `.md` file to update the research with new claims. The app reconciles new claims with existing ones and generates an updated report.

## Project Structure
- `app.py`: Main Streamlit application for the user interface.
- `agent.py`: Core `ResearchAgent` class for conducting research and updating results.
- `credibility.py`: `CredibilityAnalyzer` class for scoring claims based on source, bias, and language.
- `tools.py`: Utility functions for web searching and claim extraction.
- `config.py`: Environment setup and configuration for API keys and thresholds.

## Configuration
- **API Keys**: Set `GOOGLE_API_KEY` for Gemini LLM and `SERPER_API_KEY` for web searches (optional).
- **Credibility Thresholds** (`config.py`):
  - HIGH
  - MEDIUM
  - LOW
- **KPIs**: Tracks metrics like average credibility score, high-credibility ratio, and processing time.

## Limitations
- Requires internet access for web searches (Serper API) and Gemini LLM.
- Mock data is used if `SERPER_API_KEY` is not set.
- File uploads are limited to `.txt` and `.md` formats.
- Research updates require prior research in the session cache.

## License
This project is licensed under the MIT License.