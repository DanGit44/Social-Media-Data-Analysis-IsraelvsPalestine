# Social-Media-Data-Analysis-IsraelvsPalestine

## Overview
This project is my dive into data science, where I've built a comprehensive pipeline to analyze social media comments (specifically from YouTube) and some other content for more analsys. My goal is to use data collection, processing, and advanced analytical techniques to uncover patterns and gain insights into public sentiment and user behavior.

The pipeline is split into three primary stages:
1. **Data Acquisition (The Harvesting Tools)**
2. **Text Processing & Classification (The NLP Dictionary Tool)**
3. **Big Data Aggregation & Analysis (The PySpark Notebook)**

### 1. Data Acquisition (YouTube API Scrapers)
To overcome the limitations of the YouTube Data API quota and ensure a clean, historical dataset, two separate Python scripts were developed to harvest the raw data.
* **Hashtag Searcher:** Scans YouTube for videos containing specific thematic hashtags (#israel, #palestine, e.g.) up to a set chronological boundary (`before:2023` for comments specifically before certain date). It maintains a local caching system (`seen_videos_ids.csv`) to prevent duplicate data from running through the same videos.
* **Comment Extractor:** Iterates through the discovered Video IDs to pull top-level comments, view counts, like counts, and some author profile metadata. The data is saved into daily batched CSV files to ensure safe check-pointing.

### 2. Text Processing & Classification (The Dictionary Classifier)
To extract specific sentiment stances from unstructured social media text, a custom classification script processes the raw CSVs.
* **Emoji Normalization:** Utilizes the `emoji` library to translate Unicode emojis (e.g., 🍉, 🎗️, 🇮🇱) into identifiable string tags (e.g., `:watermelon:`, `:reminder_ribbon:`), ensuring vital non-textual sentiment is captured.
* **Dictionary Matching:** Compares the cleaned text against heavily curated target dictionaries to bin the comments into distinct analytical categories, discarding "unknown" noise and outputting cleaned `classification_` files.

### 3. Big Data Analysis (PySpark & Plotly)
With over 270,000 classified comments, the project transitions into a Databricks/Colab environment to handle the data volume.

* **Trend Mapping:** Uses PySpark to aggregate historical sentiment by Video Publish Year and Comment Publish Year. The findings are visualized using `plotly.graph_objects` to display the "Percentage Difference" in engagement (likes) over time, moving beyond simple volume metrics to highlight *resonance*.
* **Bot & Astroturfing Detection:** To ensure the integrity of the human sentiment, the project employs a heuristic bot-scoring system:
  * **Behavioral Flags:** PySpark Window functions calculate the frequency of comments per author and flag users who repeat the *exact* same text string across multiple videos (e.g., >30% identical comment rate).
  * **Lexical Analysis:** Integrates the `pyenchant` C-library to scan Author Usernames. Usernames that consist entirely of randomized alphanumeric gibberish (failing standard dictionary checks) are flagged as potential automated accounts.
* **Contextual Framing from more sources - GDELT Project, News API and Google Trends.


---
I'm using a variety of tools to make all this happen:
## 🚀 Examples of Technologies Used
* **Python 3.x**
* **Apache Spark (PySpark):** For distributed data processing, aggregations, and window functions.
* **Pandas:** For local data manipulation and API ingestion.
* **Youtube API Client:** Interacting with YouTube Data API v3.
* **Plotly:** Interactive data visualization.
* **Emoji & PyEnchant:** Specialized NLP pre-processing and lexical verification.

---

## 📊 Key Analytical Insights
* **For reviewing the all the analytics results please check out IsraelvsPalestine.ipynb**


---
## A slight caveat
There are a few assumptions that are important to remember:
1. There will be errors in using the dictionary to classify support for each side (for example, someone saying: "All those who write for free Palestine are ignorant") that we will certainly fall into, but they are few and probably exist on both sides so that they offset each other. Using an AI model would have been better but requires excessive resources.
2. The project mainly concerns comments from a specific social network, there are other social networks and it is possible that demographically the conclusions from the project will not necessarily represent the entire population.
3. Unfortunately, I was not able to obtain many responses from one time (before 2020) so in general it is difficult to analyze what was more than a few years ago.

## Overall Conclusions that can be noted
1. There is not exactly a clear-cut sequence and support on which it can be argued that one side has greater support, it seems that support overall rises and falls on each side based on a period of time and political events at those times.
2. Overall we see more support for Palestine.
3. There are quite a few bots - in the 20% range according to my calculations.
