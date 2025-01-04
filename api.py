from flask import Flask, jsonify
import urllib.request
import json
import wca_vote_crawler
from flask_cors import CORS

class VoteAPI:

    def __init__(self):
        self.base_url = "https://api2024.wechoice.vn/vote-token.htm"
        self.headers = {
            "accept": "*/*",
            "accept-language": "vi,en-US;q=0.9,en;q=0.8",
            "sec-ch-ua":
            '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent":
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
            "referer": "https://wechoice.vn/"
        }
        self.crawl_votes = wca_vote_crawler.CrawlVotes()

    def get_votes(self):
        nominee_ids = [f"w{award}-{member}" for award in self.crawl_votes.wca_votes for member in self.crawl_votes.wca_votes[award]['nominees']]

        if not nominee_ids:
            return {}

        api_url = f"{self.base_url}?m=get-vote&lstId={''.join(nominee_ids)}"

        try:
            request = urllib.request.Request(api_url, headers=self.headers)
            with urllib.request.urlopen(request) as response:
                vote_data = json.loads(response.read().decode('utf-8'))

            return vote_data
        except (urllib.error.URLError, json.JSONDecodeError) as e:
            print(f"Error fetching votes: {e}")
            return {}

class FlaskApp:

    def __init__(self):
        self.app = Flask(__name__)
        self.vote_api = VoteAPI()
        self._register_routes()
        CORS(self.app, resources={r"/*": {"origins": ["https://lzhoang2801.github.io/", "http://127.0.0.1:5500"]}})

    def _register_routes(self):
        self.app.route('/get_votes')(self.api_get_votes)

    def api_get_votes(self):
        try:
            vote_data = self.vote_api.get_votes()

            if vote_data:
                return jsonify(vote_data), 200
            return jsonify({"error": "Could not retrieve vote data"}), 500
        except Exception as e:
            print(f"API Error: {e}")
            return jsonify({"error": "An unexpected error occurred"}), 500

    def run(self, debug=True):
        self.app.run(debug=debug, port=5001)

if __name__ == '__main__':
    flask_app = FlaskApp()
    flask_app.run()
