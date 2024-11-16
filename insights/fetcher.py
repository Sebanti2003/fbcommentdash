
from instagrapi import Client
import pandas as pd
from datetime import datetime
from textblob import TextBlob
import os
from config import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD

def fetch_instagram_insights(username=INSTAGRAM_USERNAME, password=INSTAGRAM_PASSWORD):
    cl = Client()

    try:
        # Login to Instagram
        cl.login(username, password)
        print("Login successful!")

        # Fetch the user's account
        user_id = cl.user_id_from_username(username)

        # Fetch the user's profile
        user_info = cl.user_info(user_id)

        # Display basic profile information
        print(f"Username: {user_info.username}")
        print(f"Followers: {user_info.follower_count}")

        # Fetch user's recent media (posts)
        medias = cl.user_medias(user_id)  # Fetch all posts

        comment_count = 0
        insights_data = []
        summary_data_list = []  # List to hold summary data

        total_likes = 0
        total_comments = 0
        total_view_counts = 0
        total_content = 0
        monthly_comment_sentiment = {'positive': 0, 'neutral': 0, 'negative': 0}

        # Store the previous month for comparison
        previous_month = None

        # Loop through each media item to get insights
        for media in reversed(medias):  # Start from the most recent
            media_info = cl.media_info(media.id)

            # Extract the month and year from the media's created time
            media_month = media_info.taken_at.month
            media_year = media_info.taken_at.year

            # Check if the month has changed
            if previous_month is None:
                previous_month = (media_month, media_year)  # Initialize the first month
            elif (media_month, media_year) != previous_month:
                # If month has changed, save the summary for the previous month
                summary_data = {
                    "Total Likes": total_likes,
                    "Total Comments": total_comments,
                    "Total Views": total_view_counts,
                    "Total Content": total_content,
                    "Engagement Rate": ((total_likes + total_comments) / (user_info.follower_count * total_content) * 100) if total_content > 0 else 0,
                    "Followers": user_info.follower_count,
                    "Following": user_info.following_count,
                    "Month": datetime(previous_month[1], previous_month[0], 1).strftime("%B"),  # Month name
                    "Year": previous_month[1]  # Year of the media
                }
                summary_data_list.append(summary_data)  # Add to the list of summaries

                # Reset totals for the new month
                total_likes = 0
                total_comments = 0
                total_view_counts = 0
                total_content = 0
                previous_month = (media_month, media_year)  # Update to the new month

            comments = cl.media_comments(media.id)
            for comment in comments:
                polarity = TextBlob(comment.text).sentiment.polarity
                if polarity > 0:
                    monthly_comment_sentiment['positive'] += 1
                elif polarity < 0:
                    monthly_comment_sentiment['negative'] += 1
                else:
                    monthly_comment_sentiment['neutral'] += 1
                comment_count += 1

            # Process media information
            insights_data.append({
                "media_id": media.id,
                "likes": media_info.like_count,  # Likes
                "comments": media_info.comment_count,  # Comments
                "caption": media_info.caption_text,  # Caption  # Type of media
                "created_time": media_info.taken_at,
                "no_of_views": media_info.view_count,
            })

            # Update total counts
            total_likes += media_info.like_count
            total_comments += comment_count
            total_view_counts += media_info.view_count or 0  # Handle None case
            total_content += 1

        # After processing all media, add the final summary for the last month
        summary_data = {
            "Total Likes": total_likes,
            "Total Comments": total_comments,
            "Total Views": total_view_counts,
            "Total Content": total_content,
            "Engagement Rate": ((total_likes + total_comments) / (user_info.follower_count * total_content) * 100) if total_content > 0 else 0,
            "Followers": user_info.follower_count,
            "Following": user_info.following_count,
            "Month": datetime(previous_month[1], previous_month[0], 1).strftime("%B"),  # Month name
            "Year": previous_month[1],
            "Positive Comments": monthly_comment_sentiment['positive'],
            "Neutral Comments": monthly_comment_sentiment['neutral'],
            "Negative Comments": monthly_comment_sentiment['negative']
        }
        summary_data_list.append(summary_data)  # Add the last month's summary to the list

        # Create a DataFrame from the summary data list
        summary_df = pd.DataFrame(summary_data_list)

        # Prepare the file name
        summary_file_name = f"output/{username}_insta_summary.csv"

        # Check if the file already exists
        if os.path.exists(summary_file_name):
            existing_summary_df = pd.read_csv(summary_file_name)

            for index, row in summary_df.iterrows():
                month_year = (row["Month"], row["Year"])

                existing_row = existing_summary_df[
                    (existing_summary_df["Month"] == row["Month"]) &
                    (existing_summary_df["Year"] == row["Year"])
                ]

                if existing_row.empty:
                    existing_summary_df = existing_summary_df.append(row, ignore_index=True)
                else:
                    existing_row = existing_row.iloc[0]
                    if (existing_row["Total Likes"] != row["Total Likes"] or
                        existing_row["Total Comments"] != row["Total Comments"] or
                        existing_row["Total Views"] != row["Total Views"] or
                        existing_row["Total Content"] != row["Total Content"] or
                        existing_row["Engagement Rate"] != row["Engagement Rate"]):
                        existing_summary_df.loc[
                            existing_summary_df.index[
                                (existing_summary_df["Month"] == row["Month"]) &
                                (existing_summary_df["Year"] == row["Year"])
                            ][0]
                        ] = row
        else:
            existing_summary_df = summary_df

        existing_summary_df['YearMonth'] = existing_summary_df['Year'].astype(str) + '-' + existing_summary_df['Month']
        existing_summary_df['YearMonth'] = pd.to_datetime(existing_summary_df['YearMonth'])

        if existing_summary_df['YearMonth'].isnull().any():
            pass
        existing_summary_df = existing_summary_df.sort_values(by='YearMonth', ascending=False).drop(columns=['YearMonth'])
        existing_summary_df.to_csv(summary_file_name, index=False)
        print(f"Summary data saved to {summary_file_name}")

    except Exception as e:
        print(f"An error occurred: {e}")
























































































































# # from instagrapi import Client
# # import pandas as pd
# # from datetime import datetime
# # import os

# # def fetch_instagram_insights(username, password, save_csv=False):
# #     cl = Client()
# #     cl.login(username, password)

# #     # Example: Fetching user data
# #     user_info = cl.account_info()
# #     media = cl.user_medias(user_info.pk, 20)

# #     # Process the data (example)
# #     insights = []
# #     for m in media:
# #         insights.append({
# #             "id": m.pk,
# #             "caption": m.caption_text,
# #             "likes": m.like_count,
# #             "comments": m.comment_count,
# #             "posted_at": m.taken_at
# #         })

# #     if save_csv:
# #         # Save the data to a CSV file in `output/` folder
# #         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# #         csv_file_path = f"output/instagram_insights_{timestamp}.csv"
# #         os.makedirs("output", exist_ok=True)  # Ensure the folder exists
# #         pd.DataFrame(insights).to_csv(csv_file_path, index=False)
# #         return csv_file_path

# #     return insights
# # insights/fetcher.py
# # from instagrapi import Client
# # import pandas as pd
# # from datetime import datetime
# # from textblob import TextBlob
# # import os
# # from config import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD

# # def fetch_instagram_insights(username=INSTAGRAM_USERNAME, password=INSTAGRAM_PASSWORD):
# #     cl = Client()

# #     try:
# #         # Login to Instagram
# #         cl.login(username, password)
# #         print("Login successful!")

# #         # Fetch the user's account
# #         user_id = cl.user_id_from_username(username)

# #         # Fetch the user's profile
# #         user_info = cl.user_info(user_id)

# #         # Display basic profile information
# #         print(f"Username: {user_info.username}")
# #         print(f"Followers: {user_info.follower_count}")

# #         # Fetch user's recent media (posts)
# #         medias = cl.user_medias(user_id)  # Fetch all posts

# #         comment_count = 0
# #         insights_data = []
# #         summary_data_list = []  # List to hold summary data

# #         total_likes = 0
# #         total_comments = 0
# #         total_view_counts = 0
# #         total_content = 0
# #         monthly_comment_sentiment = {'positive': 0, 'neutral': 0, 'negative': 0}

# #         # Store the previous month for comparison
# #         previous_month = None

# #         # Loop through each media item to get insights
# #         for media in reversed(medias):  # Start from the most recent
# #             media_info = cl.media_info(media.id)

# #             # Extract the month and year from the media's created time
# #             media_month = media_info.taken_at.month
# #             media_year = media_info.taken_at.year

# #             # Check if the month has changed
# #             if previous_month is None:
# #                 previous_month = (media_month, media_year)  # Initialize the first month
# #             elif (media_month, media_year) != previous_month:
# #                 # If month has changed, save the summary for the previous month
# #                 summary_data = {
# #                     "Total Likes": total_likes,
# #                     "Total Comments": total_comments,
# #                     "Total Views": total_view_counts,
# #                     "Total Content": total_content,
# #                     "Engagement Rate": ((total_likes + total_comments) / (user_info.follower_count * total_content) * 100) if total_content > 0 else 0,
# #                     "Followers": user_info.follower_count,
# #                     "Following": user_info.following_count,
# #                     "Month": datetime(previous_month[1], previous_month[0], 1).strftime("%B"),  # Month name
# #                     "Year": previous_month[1]  # Year of the media
# #                 }
# #                 summary_data_list.append(summary_data)  # Add to the list of summaries

# #                 # Reset totals for the new month
# #                 total_likes = 0
# #                 total_comments = 0
# #                 total_view_counts = 0
# #                 total_content = 0
# #                 previous_month = (media_month, media_year)  # Update to the new month

# #             comments = cl.media_comments(media.id)
# #             for comment in comments:
# #                 polarity = TextBlob(comment.text).sentiment.polarity
# #                 if polarity > 0:
# #                     monthly_comment_sentiment['positive'] += 1
# #                 elif polarity < 0:
# #                     monthly_comment_sentiment['negative'] += 1
# #                 else:
# #                     monthly_comment_sentiment['neutral'] += 1
# #                 comment_count += 1

# #             # Process media information
# #             insights_data.append({
# #                 "media_id": media.id,
# #                 "likes": media_info.like_count,  # Likes
# #                 "comments": media_info.comment_count,  # Comments
# #                 "caption": media_info.caption_text,  # Caption  # Type of media
# #                 "created_time": media_info.taken_at,
# #                 "no_of_views": media_info.view_count,
# #             })

# #             # Update total counts
# #             total_likes += media_info.like_count
# #             total_comments += comment_count
# #             total_view_counts += media_info.view_count or 0  # Handle None case
# #             total_content += 1

# #         # After processing all media, add the final summary for the last month
# #         summary_data = {
# #             "Total Likes": total_likes,
# #             "Total Comments": total_comments,
# #             "Total Views": total_view_counts,
# #             "Total Content": total_content,
# #             "Engagement Rate": ((total_likes + total_comments) / (user_info.follower_count * total_content) * 100) if total_content > 0 else 0,
# #             "Followers": user_info.follower_count,
# #             "Following": user_info.following_count,
# #             "Month": datetime(previous_month[1], previous_month[0], 1).strftime("%B"),  # Month name
# #             "Year": previous_month[1],
# #             "Positive Comments": monthly_comment_sentiment['positive'],
# #             "Neutral Comments": monthly_comment_sentiment['neutral'],
# #             "Negative Comments": monthly_comment_sentiment['negative']
# #         }
# #         summary_data_list.append(summary_data)  # Add the last month's summary to the list

# #         # Create a DataFrame from the summary data list
# #         summary_df = pd.DataFrame(summary_data_list)

# #         # Prepare the file name
# #         summary_file_name = f"output/{username}_insta_summary.csv"

# #         # Check if the file already exists
# #         if os.path.exists(summary_file_name):
# #             existing_summary_df = pd.read_csv(summary_file_name)

# #             for index, row in summary_df.iterrows():
# #                 month_year = (row["Month"], row["Year"])

# #                 existing_row = existing_summary_df[
# #                     (existing_summary_df["Month"] == row["Month"]) &
# #                     (existing_summary_df["Year"] == row["Year"])
# #                 ]

# #                 if existing_row.empty:
# #                     existing_summary_df = existing_summary_df.append(row, ignore_index=True)
# #                 else:
# #                     existing_row = existing_row.iloc[0]
# #                     if (existing_row["Total Likes"] != row["Total Likes"] or
# #                         existing_row["Total Comments"] != row["Total Comments"] or
# #                         existing_row["Total Views"] != row["Total Views"] or
# #                         existing_row["Total Content"] != row["Total Content"] or
# #                         existing_row["Engagement Rate"] != row["Engagement Rate"]):
# #                         existing_summary_df.loc[
# #                             existing_summary_df.index[
# #                                 (existing_summary_df["Month"] == row["Month"]) &
# #                                 (existing_summary_df["Year"] == row["Year"])
# #                             ][0]
# #                         ] = row
# #         else:
# #             existing_summary_df = summary_df

# #         existing_summary_df['YearMonth'] = existing_summary_df['Year'].astype(str) + '-' + existing_summary_df['Month']
# #         existing_summary_df['YearMonth'] = pd.to_datetime(existing_summary_df['YearMonth'])
# #         if existing_summary_df['YearMonth'].isnull().any():
# #             pass
# #         existing_summary_df = existing_summary_df.sort_values(by='YearMonth', ascending=False).drop(columns=['YearMonth'])
# #         existing_summary_df.to_csv(summary_file_name, index=False)
# #         print(f"Summary data saved to {summary_file_name}")

# #     except Exception as e:
# #         print(f"An error occurred: {e}")
# from instagrapi import Client
# import pandas as pd
# from datetime import datetime
# from textblob import TextBlob
# import os
# from config import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD

# def fetch_instagram_insights(username=INSTAGRAM_USERNAME, password=INSTAGRAM_PASSWORD):
#     cl = Client()

#     try:
#         # Login to Instagram
#         cl.login(username, password)
#         print("Login successful!")

#         # Fetch the user's account
#         user_id = cl.user_id_from_username(username)

#         # Fetch the user's profile
#         user_info = cl.user_info(user_id)

#         # Display basic profile information
#         print(f"Username: {user_info.username}")
#         print(f"Followers: {user_info.follower_count}")

#         # Fetch user's recent media (posts)
#         medias = cl.user_medias(user_id)  # Fetch all posts

#         comment_count = 0
#         insights_data = []
#         summary_data_list = []  # List to hold summary data

#         total_likes = 0
#         total_comments = 0
#         total_view_counts = 0
#         total_content = 0
#         monthly_comment_sentiment = {'positive': 0, 'neutral': 0, 'negative': 0}

#         # Store the previous month for comparison
#         previous_month = None

#         # Loop through each media item to get insights
#         for media in reversed(medias):  # Start from the most recent
#             media_info = cl.media_info(media.id)

#             # Extract the month and year from the media's created time
#             media_month = media_info.taken_at.month
#             media_year = media_info.taken_at.year

#             # Check if the month has changed
#             if previous_month is None:
#                 previous_month = (media_month, media_year)  # Initialize the first month
#             elif (media_month, media_year) != previous_month:
#                 # If month has changed, save the summary for the previous month
#                 summary_data = {
#                     "Total Likes": total_likes,
#                     "Total Comments": total_comments,
#                     "Total Views": total_view_counts,
#                     "Total Content": total_content,
#                     "Engagement Rate": ((total_likes + total_comments) / (user_info.follower_count * total_content) * 100) if total_content > 0 else 0,
#                     "Followers": user_info.follower_count,
#                     "Following": user_info.following_count,
#                     "Month": datetime(previous_month[1], previous_month[0], 1).strftime("%B"),  # Month name
#                     "Year": previous_month[1]  # Year of the media
#                 }
#                 summary_data_list.append(summary_data)  # Add to the list of summaries

#                 # Reset totals for the new month
#                 total_likes = 0
#                 total_comments = 0
#                 total_view_counts = 0
#                 total_content = 0
#                 previous_month = (media_month, media_year)  # Update to the new month

#             comments = cl.media_comments(media.id)
#             for comment in comments:
#                 polarity = TextBlob(comment.text).sentiment.polarity
#                 if polarity > 0:
#                     monthly_comment_sentiment['positive'] += 1
#                 elif polarity < 0:
#                     monthly_comment_sentiment['negative'] += 1
#                 else:
#                     monthly_comment_sentiment['neutral'] += 1
#                 comment_count += 1

#             # Process media information
#             insights_data.append({
#                 "media_id": media.id,
#                 "likes": media_info.like_count,  # Likes
#                 "comments": media_info.comment_count,  # Comments
#                 "caption": media_info.caption_text,  # Caption  # Type of media
#                 "created_time": media_info.taken_at,
#                 "no_of_views": media_info.view_count,
#             })

#             # Update total counts
#             total_likes += media_info.like_count
#             total_comments += comment_count
#             total_view_counts += media_info.view_count or 0  # Handle None case
#             total_content += 1

#         # After processing all media, add the final summary for the last month
#         summary_data = {
#             "Total Likes": total_likes,
#             "Total Comments": total_comments,
#             "Total Views": total_view_counts,
#             "Total Content": total_content,
#             "Engagement Rate": ((total_likes + total_comments) / (user_info.follower_count * total_content) * 100) if total_content > 0 else 0,
#             "Followers": user_info.follower_count,
#             "Following": user_info.following_count,
#             "Month": datetime(previous_month[1], previous_month[0], 1).strftime("%B"),  # Month name
#             "Year": previous_month[1],
#             "Positive Comments": monthly_comment_sentiment['positive'],
#             "Neutral Comments": monthly_comment_sentiment['neutral'],
#             "Negative Comments": monthly_comment_sentiment['negative']
#         }
#         summary_data_list.append(summary_data)  # Add the last month's summary to the list

#         # Create a DataFrame from the summary data list
#         summary_df = pd.DataFrame(summary_data_list)

#         # Prepare the file name
#         summary_file_name = f"output/{username}_insta_summary.csv"

#         # Check if the file already exists
#         if os.path.exists(summary_file_name):
#             existing_summary_df = pd.read_csv(summary_file_name)

#             for index, row in summary_df.iterrows():
#                 month_year = (row["Month"], row["Year"])

#                 existing_row = existing_summary_df[
#                     (existing_summary_df["Month"] == row["Month"]) &
#                     (existing_summary_df["Year"] == row["Year"])
#                 ]

#                 if existing_row.empty:
#                     existing_summary_df = existing_summary_df.append(row, ignore_index=True)
#                 else:
#                     existing_row = existing_row.iloc[0]
#                     if (existing_row["Total Likes"] != row["Total Likes"] or
#                         existing_row["Total Comments"] != row["Total Comments"] or
#                         existing_row["Total Views"] != row["Total Views"] or
#                         existing_row["Total Content"] != row["Total Content"] or
#                         existing_row["Engagement Rate"] != row["Engagement Rate"]):
#                         existing_summary_df.loc[
#                             existing_summary_df.index[
#                                 (existing_summary_df["Month"] == row["Month"]) &
#                                 (existing_summary_df["Year"] == row["Year"])
#                             ][0]
#                         ] = row
#         else:
#             existing_summary_df = summary_df

#         existing_summary_df['YearMonth'] = existing_summary_df['Year'].astype(str) + '-' + existing_summary_df['Month']
#         existing_summary_df['YearMonth'] = pd.to_datetime(existing_summary_df['YearMonth'])
#         if existing_summary_df['YearMonth'].isnull().any():
#             pass
#         existing_summary_df = existing_summary_df.sort_values(by='YearMonth', ascending=False).drop(columns=['YearMonth'])
#         existing_summary_df.to_csv(summary_file_name, index=False)
#         print(f"Summary data saved to {summary_file_name}")

#     except Exception as e:
#         print(f"An error occurred: {e}")

# insights/fetcher.py