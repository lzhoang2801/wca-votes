from flask import Flask, jsonify
import wca_vote_crawler
from flask_cors import CORS
import threading
import time

class WCAVotesAPI:

    def __init__(self):
        self.app = Flask(__name__)
        self.cached_vote_data = {}
        self._register_routes()
        CORS(self.app, resources={r"/*": {"origins": ["https://lzhoang2801.github.io", "http://127.0.0.1:5500"]}})

        self.crawl_votes = wca_vote_crawler.CrawlVotes()
        
        self.update_thread = threading.Thread(target=self._update_votes_periodically, daemon=True)
        self.update_thread.start()

    def _update_votes_periodically(self):
        while True:
            try:
                self.cached_vote_data = self.crawl_votes.crawl_votes()

                current_time = time.localtime()
                if current_time.tm_min % 5 == 0 and current_time.tm_sec == 30:
                    print("Saving vote data at", time.strftime("%Y-%m-%d %H:%M:%S", current_time))
                    #self.crawl_votes.save()

                time.sleep(1)
            except Exception as e:
                print(f"Update Error: {e}")

    def _register_routes(self):
        self.app.route('/get_votes')(self.api_get_votes)

    def api_get_votes(self):
        try:
            if self.cached_vote_data:
                return jsonify(self.cached_vote_data), 200
            return jsonify({"error": "No vote data available"}), 500
        except Exception as e:
            print(f"API Error: {e}")
            return jsonify({"error": "An unexpected error occurred"}), 500

    def run(self, debug=True):
        self.app.run(port=5001)

if __name__ == '__main__':
    wca_votes = WCAVotesAPI()
    wca_votes.run()
