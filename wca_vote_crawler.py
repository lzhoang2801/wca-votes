import urllib.request
import json
from datetime import datetime
import wca_nominee_crawler

class CrawlVotes:
    def __init__(self):
        self.wca_votes = {}
        self.load_wca_votes()

    def load_wca_votes(self):
        try:
            with open('wca_votes.json', 'r', encoding='utf-8') as f:
                self.wca_votes = json.load(f)
        except FileNotFoundError:
            self.wca_votes = wca_nominee_crawler.CrawlNominees().crawl_nominees()

    def crawl_votes(self, wca_votes):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lst_ids = [f"w{award}-{member}" for award in wca_votes 
                for member in wca_votes[award]['nominees']]
        
        api_url = f"https://api2024.wechoice.vn/vote-token.htm?m=get-vote&lstId={''.join(lst_ids)}"
        headers = {
            "accept": "*/*",
            "accept-language": "vi,en-US;q=0.9,en;q=0.8",
            "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
            "referer": "https://wechoice.vn/"
        }
        request = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(request) as response:
            vote_data = json.loads(response.read().decode('utf-8'))

        for item in vote_data.get('Data', []):
            member_id = str(item['m'])
            vote_count = str(item['list'][0]['v']) if item.get('list') else '0'
            
            for award_id in wca_votes:
                if member_id in wca_votes[award_id]['nominees']:
                    wca_votes[award_id]['nominees'][member_id]['vote_history'].append({
                        'timestamp': current_time,
                        'count': vote_count
                    })

        return wca_votes

    def crawl(self):
        try:
            self.wca_votes.update(self.crawl_votes(self.wca_votes))
        except Exception as e:
            print(f"Error during crawl: {e}")

    def save(self):
        try:
            with open('wca_votes.json', 'w', encoding='utf-8') as f:
                json.dump(self.wca_votes, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")

    def run(self):
        self.crawl()
        self.save()

if __name__ == "__main__":
    crawler = CrawlVotes()
    crawler.run()
