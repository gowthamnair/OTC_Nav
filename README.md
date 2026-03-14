# OTC Navigator (OTCN)

**OTC Navigator (OTCN)** is a multilingual, symptom-based decision-support tool designed to help users identify over-the-counter (OTC) medication options. The application features a dark-themed, glassmorphism UI and supports multiple languages including English, Hindi, Arabic, Malayalam, and Tagalog.

---

### ⚠️ Medical Disclaimer
**This project is for informational and educational reference purposes only.**
* **Not Medical Advice:** The information provided by this application does **not** constitute professional medical advice, diagnosis, or treatment.
* **Consult a Professional:** Always seek the advice of a physician or other qualified health provider with any questions you may have regarding a medical condition.
* **Emergency Use:** Never disregard professional medical advice or delay in seeking it because of something you have read on this application. In case of a medical emergency, call your local emergency services immediately.

---

### Key Features
* **Multilingual Support:** Fully translated symptom wizards and product data for English, Hindi, Arabic, Malayalam, and Tagalog.
* **Symptom-Based Wizard:** A 3-step hierarchical categorization logic (Primary Symptom > Specific Context > Form/Preference) to narrow down choices.
* **Smart Data Enrichment:** Product names are cleaned and one-liner benefit descriptions are generated using Gemini 2.0 Flash.
* **Safety First:** Automated extraction and display of critical warnings (e.g., "Contains Paracetamol", "External use only").
* **Utility Tools:** Integrated buttons to find the nearest pharmacy or hospital via Google Maps and a result-sharing feature.

---

### Technical Architecture
The project is built using a decoupled architecture:
1.  **Data Processing (Python/Jupyter):** Scrapes data from pharmaceutical sources and utilizes the **Gemini 2.0 Flash-Lite** model via OpenRouter for high-speed, cost-effective categorization and translation.
2.  **Frontend (Web Stack):** A lightweight, single-page application (SPA) built with:
    * **HTML5/CSS3:** Custom glassmorphism styling and responsive design.
    * **JavaScript (Vanilla):** Dynamic rendering of the question tree and filtering logic.
    * **PapaParse:** For high-performance client-side CSV parsing.
    * **FontAwesome:** For intuitive medical iconography.

---

### File Structure
To run this project, the following files must be present in the root directory:
* `index.html`: The core application UI and logic.
* `medication_master_multilingual_final.csv`: The master database of medications.
* `question_tree_english.json`: Logic for the English wizard.
* `question_tree_hindi.json`: Logic for the Hindi wizard.
* `question_tree_arabic.json`: Logic for the Arabic wizard.
* `question_tree_malayalam.json`: Logic for the Malayalam wizard.
* `question_tree_tagalog.json`: Logic for the Tagalog wizard.

---

### License
This project is provided "as-is" for reference. The developers assume no liability for the accuracy of the AI-generated translations or categorizations.
