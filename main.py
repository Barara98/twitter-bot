import os
import time
import logging

import dotenv
import tweepy
from openai import OpenAI

from celebs_fetcher import CelebrityArticleFetcher

# Load environment variables from .env file
dotenv.load_dotenv()


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()  # This will log to the console
    ]
)


def create_twitter_client():
    try:
        # Retrieve your credentials from environment variables
        bearer_token = os.getenv('BEARER_TOKEN')
        api_key = os.getenv('CONSUMER_KEY')
        api_secret = os.getenv('CONSUMER_SECRET')
        access_token = os.getenv('ACCESS_TOKEN')
        access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')

        # Create a client using your credentials
        client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )

        logging.info("Twitter client created successfully.")
        return client

    except Exception as e:
        logging.error(f"Failed to create Twitter client: {e}")
        return None


def logout_twitter_client(client):
    if client is not None:
        try:
            # Revoke the access token
            client.auth.revoke_token()
            logging.info("Access token revoked successfully.")
        except Exception as e:
            logging.error(f"Failed to revoke access token: {e}")
        finally:
            # Clear the client reference
            del client
            logging.info("Twitter client logged out.")


def get_twitter_names(celebs):
    # Initialize OpenAI client
    openai_key = os.getenv("OPENAI_KEY")
    client = OpenAI(api_key=openai_key)
    prompt = (
        "You are given a list of celebrities names. "
        "Return only the names and handles in the format 'name: @twitter_handle', one per line. "
        "If a Twitter account is not available, indicate it as 'name: None'. "
        "DO the best to find the handles for the celebrities.\n\n"
        "Do not include any additional text or explanations.\n"
        f"{', '.join(celebs)}"
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract only the celebrity names and Twitter accounts."},
            {"role": "user", "content": prompt}
        ]
    )

    response_content = completion.choices[0].message.content
    print(response_content)
    return [(name.strip(), handle.strip()) for name, handle in
            (line.split(': ') for line in response_content.splitlines() if ':' in line)]


def tweet_polls(client, celebs_list):
    for name, twitter_account in celebs_list:
        # Construct the poll question
        question = f"{name} FUCK or AWESOME? {twitter_account if twitter_account not in [None, 'None'] else ''}"
        options = ["FUCK", "AWESOME"]

        # Post the tweet with a poll
        try:
            response = client.create_tweet(
                text=question,
                poll_options=options,
                poll_duration_minutes=1440
            )
            logging.info(f"Poll tweeted for {name}: {response.data['id']}")
        except tweepy.TweepyException as e:
            logging.error(f"Error tweeting poll for {name}: {str(e)}")

        # Wait for one hour before the next tweet
        time.sleep(3600)  # 3600 seconds = 1 hour


def create_complete_list(fetcher, celebs_list):
    with_twitter = [celebrity for celebrity in celebs_list if celebrity[1] is not None]
    without_twitter = [name for name, twitter in celebs_list if twitter is None]

    # Step 2: Filter for celebrities
    if without_twitter:
        twitter_names_list = get_twitter_names(without_twitter)
        for name in twitter_names_list:
            fetcher.database.set_twitter_account(name[0], name[1])
            logging.info(f"Twitter account set for {name[0]}: {name[1]}")
        complete_list = twitter_names_list + with_twitter
    else:
        complete_list = celebs_list
    return complete_list


def daily_task():
    fetcher = CelebrityArticleFetcher()
    celebrities_list = fetcher.fetch_celebrities()
    complete_list = create_complete_list(fetcher, celebrities_list)
    logging.info(f"full celebrities list: {complete_list}")

    twitter_client = create_twitter_client()
    tweet_polls(twitter_client, complete_list)
    logout_twitter_client(twitter_client)


def main():
    while True:
        daily_task()
        time.sleep(60)
        logging.info("Starting a new Day!")


# Run the script
if __name__ == "__main__":
    main()
