import urllib.request
import json
from datetime import datetime
import wca_nominee_crawler
from pytz import timezone
import os

class CrawlVotes:
    def __init__(self):
        self.list_awards = []
        self.wca_data = {}
        self.load_wca_nominees()
        self.load_vote_histories()

    def load_wca_nominees(self):
        try:
            with open('wca_nominees.json', 'r', encoding='utf-8') as f:
                self.wca_data = json.load(f)
        except FileNotFoundError:
            self.wca_data = wca_nominee_crawler.CrawlNominees().crawl_nominees()

    def load_vote_histories(self):
        for award_id in self.wca_data:
            self.list_awards.append(award_id)

        for award_id in self.list_awards:
            try:
                with open(os.path.join('vote_histories', f'{award_id}.json'), 'r', encoding='utf-8') as f:
                    vote_histories = json.load(f)
            except FileNotFoundError:
                vote_histories = {}

            for nominee_id in self.wca_data[award_id]['nominees']:
                if nominee_id in vote_histories['nominees']:
                    self.wca_data[award_id]['nominees'][nominee_id]['vote_history'] = vote_histories['nominees'][nominee_id]['vote_history']
        
    def crawl_votes(self, list_awards=[]):
        vietnam_tz = timezone('Asia/Ho_Chi_Minh')
        current_time = datetime.now(vietnam_tz).strftime("%Y-%m-%d %H:%M:%S")

        if not list_awards:
            list_awards = self.list_awards

        lst_ids = [f"w{award_id}-{nominee_id}" for award_id in list_awards for nominee_id in self.wca_data[award_id]['nominees']]
        
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

        if 'Success' not in vote_data or vote_data['Success'] != True:
            return
        
        result = {}
        
        for item in vote_data.get('Data', []):
            award_id = str(item['a'])
            nominee_id = str(item['m'])
            vote_count = str(item['list'][0]['v']) if item.get('list') else '0'

            if 'vote_history' not in self.wca_data[award_id]['nominees'][nominee_id]:
                self.wca_data[award_id]['nominees'][nominee_id]['vote_history'] = []
            
            self.wca_data[award_id]['nominees'][nominee_id]['vote_history'].append({
                'timestamp': current_time,
                'count': vote_count
            })

            if not result.get(award_id):
                result[award_id] = {
                    'nominees': {}
                }

            result[award_id]['nominees'][nominee_id] = {
                'lastest_vote': {
                    'timestamp': current_time,
                    'count': vote_count
                }  
            }

        return result

    def crawl(self, list_awards=[]):
        try:
            self.crawl_votes(list_awards)
        except Exception as e:
            print(f"Error during crawl: {e}")

    def save(self, list_awards=[]):
        try:
            if not os.path.exists('vote_histories'):
                os.mkdir('vote_histories')

            if not list_awards:
                list_awards = self.list_awards
            
            for award_id in list_awards:
                vote_histories_award = {'nominees': {}}
                
                for member_id in self.wca_data[award_id]['nominees']:  
                    if 'vote_history' in self.wca_data[award_id]['nominees'][member_id]:
                        vote_histories_award['nominees'][member_id] = {
                            'vote_history': self.wca_data[award_id]['nominees'][member_id]['vote_history']
                        }
                
                with open(os.path.join('vote_histories', f'{award_id}.json'), 'w', encoding='utf-8') as f:
                    json.dump(vote_histories_award, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")

    def run(self):
        self.crawl()
        self.save()

if __name__ == "__main__":
    crawler = CrawlVotes()
    crawler.run()
