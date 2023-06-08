import httpx
import json
import sys
from bs4 import BeautifulSoup as bs
from time import sleep
from tqdm import tqdm

def get_page_num(soup):
    pagination = soup.find_all('a', class_='article-above-pagination__item')
    return len(pagination)

def get_article(url, texts, firts_page=False):
    with httpx.Client() as client:
        response = client.get(url)
    soup = bs(response.text, 'html.parser')
    if firts_page:
        texts.append(soup.find('h1').text)
        page_num = get_page_num(soup)
    else:
        page_num = 0
    conts = soup.find_all('p')
    for cont in conts[:-1]: # 最後は「© 2008-2023 PRESIDENT Inc. すべての画像・データについて無断転用・無断転載を禁じます。」
        texts.append(cont.text)
    
    return page_num

if __name__ == '__main__':
    args = sys.argv
    if len(args)==2:
        b = args[1]
    else:
        b = 0

    for i in range(1,8) if b==0 else range(b, b+1):
        print(f'\n{i*10000+1}to{(i+1)*10000}\n')
        for j in tqdm(range(i*10000+1, (i+1)*10000)):
            url_base = f'https://president.jp/articles/-/{j}'
            texts = []
            try:
                page_num = get_article(url_base, texts, firts_page=True)
            except:
                continue

            for n_page in range(2, page_num):
                try:
                    url = url_base + f'?page={n_page}'
                    _ = get_article(url, texts)
                except: # 有料記事の場合はエラーになる（e.g. https://president.jp/articles/-/3902）
                    print(f'{url} でエラー')
                    break
            
            output = {'text': ''.join(texts), 'url': url_base}
            with open(f'president{i}.jsonl', 'a', encoding='utf-8') as file:
                json.dump(output, file, ensure_ascii=False)
                file.write('\n')
            sleep(0.1)



'''
print(soup.prettify())
print(soup.find('h1')) # タイトル
print(soup.find('h4')) # 小見出し。今回は省略
print(soup.find('div', class_='article-lead')) # リード文
print(soup.find_all('p')) # 本文
'''
