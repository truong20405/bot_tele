import google.generativeai as genai
import requests
from bs4 import BeautifulSoup


def get_link_bao():
    req = requests.get('https://baomoi.com/khoa-hoc-cong-nghe.epi')
    soup = BeautifulSoup(req.text, 'html.parser')
    data = soup.find('h3',{'class':'font-semibold block'})
    link = data.find('a')['href']
    return link

def tom_tat_bao(link):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'vi,vi-VN;q=0.9',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    }
    genai.configure(api_key="AIzaSyAl4dwf__CM2Z82zj_rS2BcoKim62cYKJc")
    model = genai.GenerativeModel("gemini-2.0-flash-exp")

    try:
        bao =requests.get(f'https://baomoi.com/{link}',headers=headers,timeout=10)
        data_bao= BeautifulSoup(bao.text,'html.parser')
        p_tag= data_bao.find_all('p')
        content = "\n".join([p.text for p in p_tag])
        response = model.generate_content(f"Tóm tắt bài viết sau:{content}")
        return response.text
    except Exception:
        return Exception
    
def tro_chuyen(text):
    
    genai.configure(api_key="AIzaSyAl4dwf__CM2Z82zj_rS2BcoKim62cYKJc")
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    try:
        response = model.generate_content(f"{text}")
        return response.text
    except Exception:
        return Exception