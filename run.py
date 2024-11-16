# from insights.fetcher import fetch_instagram_insights

# if __name__ == '__main__':
#     # Replace with your Instagram credentials
#     username = "your_username"
#     password = "your_password"

#     try:
#         csv_file_path = fetch_instagram_insights(username, password, save_csv=True)
#         print(f"Insights saved to {csv_file_path}")
#     except Exception as e:
#         print(f"Error: {e}")
# run.py
from insights.fetcher import fetch_instagram_insights

# Run the Instagram insights fetcher
fetch_instagram_insights()
