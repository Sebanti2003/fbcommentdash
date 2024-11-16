from instagrapi import Client
import pandas as pd
from datetime import datetime
import os

def fetch_instagram_insights(username, password, save_csv=False):
    cl = Client()
    cl.login(username, password)

    # Example: Fetching user data
    user_info = cl.account_info()
    media = cl.user_medias(user_info.pk, 20)

    # Process the data (example)
    insights = []
    for m in media:
        insights.append({
            "id": m.pk,
            "caption": m.caption_text,
            "likes": m.like_count,
            "comments": m.comment_count,
            "posted_at": m.taken_at
        })

    if save_csv:
        # Save the data to a CSV file in `output/` folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file_path = f"output/instagram_insights_{timestamp}.csv"
        os.makedirs("output", exist_ok=True)  # Ensure the folder exists
        pd.DataFrame(insights).to_csv(csv_file_path, index=False)
        return csv_file_path

    return insights
