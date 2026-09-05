import pandas as pd
import re
from datetime import date
import glob
import os
import emoji 

today = date.today()

def clean_text(text):
    # 1. Translate emojis to text (e.g., 🍉 becomes ":watermelon:", 🇮🇱 becomes ":Israel:")
    text = emoji.demojize(text)
    
    # 2. Run normal cleaning
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#\w+", "", text)
    
    # 3. THE CRITICAL FIX: [^\w\s:] 
    # This deletes all punctuation EXCEPT colons, preserving the demojized emojis.
    text = re.sub(r"[^\w\s:]", "", text) 
    
    return text.lower().strip()


comment_dictionary = {
    "support_israel": [
        "am israel chai",
        "am israel hai",
        "i stand with israel",
        "viva israel",
        "long live israel",
        "from the river to the sea israel will prevail",
        "israel has the right to defend itself",
        "i support israel",
        "we support israel",
        "defend israel",
        "free israel",
        "god bless israel",
        "we stand with israel",
        "i love israel",
        "israel forever",
        "israel is not alone",
        "pray for israel",
        "stop hamas",
        "hamas is a terrorist organization",
        "free palestine from hamas",
        "hamas = terrorism",
        "death to hamas",
        "israel is under attack",
        "save israel",
        "solidarity with israel",
        "no ceasefire with terrorists",
        "hamas hides behind civilians",
        "israel is defending itself",
        "support idf",
        "idf is fighting terror",
        "good job israel",
        "praise israel",
        "thank you israel",
        "fuck palestine",
        "well done israel",
        "bring them home",
        "release the hostages",
        "bring the hostages",
        "israel has a right to exist",
        "anti-zionism is antisemitism",
        "stand with the idf",
        "we love israel",
        "pislam",
        ":star_and_crescent:ancer",
        ":star_and_crescent:ult",
        "religion of peace",
        # EMOJIS (Wrapped in colons so they never match regular English words)
        ":israel:",             # 🇮🇱
        ":reminder_ribbon:",    # 🎗️
        ":star_of_david:"       # ✡
    ],

    "support_palestine": [
        "free palestine",
        "from the river to the sea palestine will be free",
        "zionism is terrorism",
        "end the occupation",
        "i stand with palestine",
        "viva palestina",
        "long live palestine",
        "stop the genocide",
        "stop killing children",
        "stop israel",
        "down with israel",
        "boycott israel",
        "free gaza",
        "pray for gaza",
        "gaza under attack",
        "israel is a terrorist state",
        "apartheid israel",
        "zionists are terrorists",
        "i support palestine",
        "we support palestine",
        "liberate palestine",
        "zionism = racism",
        "palestine will be free",
        "israel is committing genocide",
        "intifada now",
        "death to israel",
        "israel war crime",
        "israhell",
        "good job iran",
        "fuck israel",
        "baby killers",
        "killing children",
        "good job hamas",
        "delete israel",
        "nuke israel",
        "kike",
        "destroy israel",
        "all eyes on rafah",
        "stop arming israel",
        "stop funding israel",
        "defund israel",
        "freedom for palestine",
        "save gaza",
        "end the apartheid",
        "freepalestine",
        "sanction israel",
        "stop the ethnic cleansing",
        "was promised to",
        "jill kews",
        # EMOJIS (Wrapped in colons)
        ":palestinian_territories:",   # 🇵🇸
        ":watermelon:",                # 🍉
        ":red_triangle_pointed_down:", # 🔻
        ":beverage_box:"               # 🧃
    ]
}

# This is the function that analyze the comment based on the dictionary
# It return the classification and the phrase it captured on from the dictionary
def classify_comment(text, dictionary):
    text = text.lower()
    for phrase in dictionary["support_israel"]:
        if phrase in text:
            return "support_israel", phrase
    for phrase in dictionary["support_palestine"]:
        if phrase in text:
            return "support_palestine", phrase
    return "unknown", ""

# comments_reddit varibale is a dataframe
comments_youtube = pd.read_csv(f"comments_youtube_{today}.csv", encoding="utf-8")
comments_youtube = comments_youtube[[
            "video_id", "title", "description", "video_publish_date",
            "views", "video_likes", "comment", "comment_likes",
            "comment_date", "author_name", "author_id", "tag"
        ]].dropna()
comments_youtube["comment"] = comments_youtube["comment"].astype(str).apply(clean_text)

unknown_comment_count = 0
support_israel_count = 0
support_palestine_count = 0

# classification_comments is a dataframe that contains the classification comments and the phrase they captured on
# classification type is 1 of 3 - "support_israel", "support_palestine", "unknown"
classification_comments = pd.DataFrame({
    "video_id": [],
    "title": [],
    "description": [],
    "video_publish_date": [],
    "views": [],
    "video_likes": [],
    "classification": [],
    "phrase_in_comment": [],
    "comment_likes": [],
    "comment_date": [],
    "comment_author_name": [],
    "comment_author_id": [],
    "tag": [],
    "full_comment": []
})

for index, row in comments_youtube.iterrows():
    support_of, phrase = classify_comment(row['comment'], comment_dictionary)
    if support_of == "unknown":
        classification_comments.loc[len(classification_comments)] = [row["video_id"], row["title"], row["description"],
                                                                     row["video_publish_date"], row["views"], row["video_likes"],
                                                                     support_of, "", row["comment_likes"], row["comment_date"],
                                                                     row["author_name"], row["author_id"], row["tag"], row["comment"]]
    if support_of == "support_israel":
        classification_comments.loc[len(classification_comments)] = [row["video_id"], row["title"], row["description"],
                                                                     row["video_publish_date"], row["views"], row["video_likes"],
                                                                     support_of, phrase, row["comment_likes"], row["comment_date"],
                                                                     row["author_name"], row["author_id"], row["tag"], row["comment"]]
        print(f"{row['video_id']} comment is about {support_of}")
    if support_of == "support_palestine":
        classification_comments.loc[len(classification_comments)] = [row["video_id"], row["title"], row["description"],
                                                                     row["video_publish_date"], row["views"], row["video_likes"],
                                                                     support_of, phrase, row["comment_likes"], row["comment_date"],
                                                                     row["author_name"], row["author_id"], row["tag"], row["comment"]]
        print(f"{row['video_id']} comment is about {support_of}")

#print(f"Israel has {support_israel['count']} support comments")
#print(f"This is the support Israel comments: {support_israel['comments']}")
#print(f"Palestine has {support_palestine['count']} support comments")
#print(f"This is the support Palestine comments: {support_palestine['comments']}")
#print(f"There are {unknown_comment['count']} unknown comments")

comments_without_unknown = classification_comments[classification_comments["classification"] != "unknown"]
print(comments_without_unknown)
comments_without_unknown.to_csv(f"classification_comments_youtube_{today}.csv", index=False, encoding="utf-8-sig")
