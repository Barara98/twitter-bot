import json
import os


class CelebrityDatabase:
    def __init__(self, db_file='celebrity_db.json'):
        self.db_file = db_file
        self.load_database()

    def load_database(self):
        """Load the JSON database into memory as an array."""
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r') as f:
                self.db = json.load(f)
        else:
            self.db = []  # Initialize as an empty list

    def save_database(self):
        """Save the current state of the database to the JSON file."""
        with open(self.db_file, 'w') as f:
            json.dump(self.db, f, indent=4)

    def get_wikidata_id(self, title):
        """Return the Wikidata ID if the article exists in the database."""
        for celeb in self.db:
            if celeb['article'] == title:
                return celeb['wiki_id']
        return None

    def is_celeb(self, title):
        for celeb in self.db:
            if celeb['article'] == title:
                return celeb['is_celebrity']
        return False

    def exists(self, title):
        """Check if the article exists in the database."""
        for celeb in self.db:
            if celeb['article'] == title:
                return [celeb['wiki_id'], celeb['is_celebrity']]
        return False

    def add_to_database(self, article, wiki_id, celeb):
        """Add a new celebrity entry to the database."""
        self.db.append({
            'article': article,
            'wiki_id': wiki_id,
            'fixed_name': self.format_title(article),
            'twitter_account': None,
            'is_celebrity': celeb
        })
        self.save_database()  # Save changes to the JSON file

    def get_twitter_account(self, title):
        for celeb in self.db:
            if celeb['article'] == title:
                return celeb['twitter_account']

    def set_twitter_account(self, name, twitter_account):
        for celeb in self.db:
            if celeb['fixed_name'] == name:
                celeb['twitter_account'] = twitter_account
                self.save_database()

    def format_title(self, title):
        """Format the title by replacing underscores with spaces and removing parentheses."""
        title = title.replace('_', ' ')
        title = title.split('(')[0].strip()
        return title
