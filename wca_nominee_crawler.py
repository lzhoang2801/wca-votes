import urllib.request
import json
import re
import gzip

class CrawlNominees:
    def __init__(self):
        self.urls = [
            'https://wechoice.vn/nhan-vat-truyen-cam-hung.htm',
            'https://wechoice.vn/bff-best-fandom-forever-1955/bff-best-fandom-forever-18.htm',
            'https://wechoice.vn/hang-muc-chinh/du-an-vi-viet-nam-toi-1951.htm',
            'https://wechoice.vn/hang-muc-chinh/don-vi-vung-manh-viet-nam-1952.htm',
            'https://wechoice.vn/hang-muc-chinh/giai-tri-38.htm',
            'https://wechoice.vn/hang-muc-chinh/genz-area-45.htm',
            'https://wechoice.vn/hang-muc-chinh/weyoung-1953.htm'
        ]

    def get_content_between(self, text, start, end):
        pattern = f'{start}(.*?){end}'
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1) if match else ''
    
    def parse_blocks(self, content, start_pattern, tag_type):
        blocks = []
        current_block = ""
        in_block = False
        tag_count = 0

        for line in content.splitlines():
            if start_pattern in line:
                in_block = True
                tag_count = 1
                current_block = line
            elif in_block:
                current_block += "\n" + line
                if f'<{tag_type}' in line:
                    tag_count += 1
                if f'</{tag_type}>' in line:
                    tag_count -= 1
                    if tag_count == 0:
                        blocks.append(current_block)
                        current_block = ""
                        in_block = False

        return blocks

    def get_award_blocks(self, html_content):
        return self.parse_blocks(
            html_content,
            '<div class="main-voting-category category-top10" id="block-award',
            'div'
        )
    
    def get_nominees(self, award_block):
        return self.parse_blocks(
            award_block,
            '<li class="nominee-li js-vote-wrapt"',
            'li'
        )

    def crawl_nominees(self):
        wca_nominees = {}

        for url in self.urls:
            print(f"Crawling nominees from {url}")
            req = urllib.request.Request(url, headers={'Accept-Encoding': 'gzip'})
            with urllib.request.urlopen(req) as response:
                if response.info().get('Content-Encoding') == 'gzip':
                    html = gzip.decompress(response.read()).decode('utf-8')
                else:
                    html = response.read().decode('utf-8')

            award_blocks = self.get_award_blocks(html)
            for award_block in award_blocks:
                award_id = self.get_content_between(award_block, '<div class="main-voting-category category-top10" id="block-award-', '"')
                award_name = self.get_content_between(award_block, '<h3 class="category-name">', '</h3>').strip()
                nominees = self.get_nominees(award_block)
                
                wca_nominees[award_id] = {
                    'award_name': award_name,
                    'nominees': {}
                }
                
                for nominee in nominees:
                    data_member = re.search(r'data-member="(\d+)"', nominee).group(1)
                    ava_link = re.search(r'<img src="([^"]+)"', nominee).group(1)
                    nominee_name = self.get_content_between(nominee, '<h3 class="nominee-name">', '</h3>').strip()
                    nominee_vote_url = 'https://wechoice.vn' + self.get_content_between(nominee_name, '<a href="', '"').strip()
                    nominee_name = re.sub(r'<[^>]+>', '', nominee_name).strip()
                    nominee_des = self.get_content_between(nominee, '<div class="nominee-des">', '</div>').strip()
                    
                    wca_nominees[award_id]['nominees'][data_member] = {
                        'ava_link': ava_link,
                        'nominee_name': nominee_name,
                        'nominee_vote_url': nominee_vote_url,
                        'nominee_des': nominee_des,
                        'vote_history': []
                    }

        return wca_nominees

    def crawl(self):
        try:
            self.wca_nominees = self.crawl_nominees()
        except Exception as e:
            print(f"Error during crawl: {e}")

    def save(self):
        try:
            with open('wca_nominees.json', 'w', encoding='utf-8') as f:
                json.dump(self.wca_nominees, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")

    def run(self):
        self.crawl()
        self.save()

if __name__ == "__main__":
    crawler = CrawlNominees()
    crawler.run()
