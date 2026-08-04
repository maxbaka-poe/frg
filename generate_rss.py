import sys
import requests
from feedgen.feed import FeedGenerator
import datetime
import re

# ＝＝＝＝＝＝ 設定 ＝＝＝＝＝＝
CREATOR_ID = "ilu" 
CREATOR_NAME = "イル"
OUTPUT_FILENAME = "secret_feed_12345.xml"
# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝

def get_fanbox_posts(creator_id):
    api_url = f"https://api.fanbox.cc/post.listCreator?creatorId={creator_id}&limit=15"
    
    headers = {
        'Origin': f'https://{creator_id}.fanbox.cc',
        'Referer': f'https://{creator_id}.fanbox.cc/',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    
    try:
        res = requests.get(api_url, headers=headers)
        res.raise_for_status()
        data = res.json()
        
        # bodyの中から 'items' または 'posts' のどちらか存在する方を取得する
        body_data = data.get('body', {})
        posts_list = body_data.get('items') or body_data.get('posts')
        
        if not posts_list:
            return []
            
        return posts_list
        
    except Exception as e:
        print(f"通信処理でエラーが発生しました: {e}")
        return []

def main():
    if CREATOR_ID == "YOUR_CREATOR_ID_HERE":
        print("エラー: クリエイターIDが設定されていません")
        sys.exit(1)

    posts = get_fanbox_posts(CREATOR_ID)
    if not posts:
        print("投稿が見つかりませんでした。")
        sys.exit(1)

    fg = FeedGenerator()
    fg.id(f'https://{CREATOR_ID}.fanbox.cc/')
    fg.title(f'{CREATOR_NAME} の FANBOX')
    fg.author({'name': CREATOR_NAME})
    fg.link(href=f'https://{CREATOR_ID}.fanbox.cc/', rel='alternate')
    fg.description(f'{CREATOR_NAME}のFANBOX更新情報')
    fg.language('ja')

    for post in posts:
        post_url = f"https://{CREATOR_ID}.fanbox.cc/posts/{post['id']}"
        fe = fg.add_entry()
        fe.id(post_url)
        fe.link(href=post_url, rel='alternate')
        
        # タイトルの取得
        title = post.get('title', '無題')
        fe.title(title)
        
        # 日時の取得
        pub_date = post.get('publishedDatetime')
        if pub_date:
            dt = datetime.datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
            fe.published(dt)
            fe.updated(dt)

        # 本文の処理
        body = post.get('body')
        fee = post.get('feeRequired', 0)
        content = ""

        if body:
            if 'text' in body and body['text']:
                clean_text = re.sub(r'<.*?>', '', body['text'])
                content = clean_text[:150] + '...'
            elif 'images' in body and body['images']:
                content = f"画像が {len(body['images'])} 枚公開されています"
            elif 'files' in body and body['files']:
                content = "ファイルが公開されています"
        else:
            if fee > 0:
                content = f"【{fee}円プラン以上の限定投稿です。本文はFANBOXで確認してください】"
            else:
                content = "本文はありません"

        fe.content(content, type='text')

    # ファイル出力
    fg.rss_file(OUTPUT_FILENAME, pretty=True)
    print(f"RSSを生成しました: {OUTPUT_FILENAME}")

if __name__ == "__main__":
    main()
