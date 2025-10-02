# Menlo Park City Council Meeting Analyzer

## Overview

This streamlit app helps stakeholders explore and understand the activities of the Menlo Park City Council. It visualizes data from council meetings in the first half of 2025, making it easy to see meeting highlights, track planning projects, and understand the stances of council members on key issues.

This application is a great learning resource for beginners interested in Python, data visualization, and the Streamlit framework.

## Features

*   **Meeting Highlights:** An interactive bar chart showing the duration and topics of each council meeting.
*   **Interactive Project Map:** A map displaying the locations of planning projects, with details available on hover and click.
*   **Council Member Stances:** A color-coded table summarizing the positions of council members on various topics.
*   **Detailed Information:** Tables providing more in-depth information about meetings, projects, and council member positions.
*   **Video Explainers:** Embedded videos offering analysis for homeowners, renters, and investors.

## Technologies Used

*   **Python:** The core programming language.
*   **Streamlit:** For creating the interactive web application.
*   **Pandas:** For data manipulation and analysis.
*   **Folium:** For generating the interactive map.
*   **Altair:** For creating the interactive bar chart.

## Data Sources

The application uses the following CSV files for its data:

*   `mpcc_topics_2025-09-06_v2_with_youtube_links.csv`: Contains data about council meetings, including dates, durations, and major topics.
*   `mpcc_projects_2025-09-08_geocoded_fixed.csv`: Contains information about planning projects, including their names, descriptions, and geographic coordinates.
*   `mpcc_stances_2025-09-08.csv`: Contains data on the stances of council members on different issues.

## Setup and Usage

To run this application locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/menlopark-council/streamlit-lwa-poc-6.git
    cd streamlit-lwa-poc-6
    ```

2.  **Install the dependencies:**
    Make sure you have Python 3.x installed. Then, install the required packages using pip:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Streamlit application:**
    ```bash
    streamlit run streamlit_app.py
    ```

4.  **View the application:**
    Open your web browser and go to the local URL provided by Streamlit (usually `http://localhost:8501`).

## How to Use

*   Use the navigation links to jump to different sections of the page.
*   Hover over the bars in the "Meeting Highlights" chart to see more details.
*   On the "Project Map," hover over pins to see project information and click on them for more details.
*   Use the tabs in the "Interpretations" section to watch the different explainer videos.

## License

This project is licensed under the terms of the LICENSE file.
