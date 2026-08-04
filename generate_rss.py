import requests
from feedgen.feed import FeedGenerator
import datetime
import re
import sys

# ＝＝＝＝＝＝ 設定 ＝＝＝＝＝＝
# ① RSSを取得したいFANBOXのクリエイターID
CREATOR_ID = "12372838" 

# ② クリエイター名（RSSリーダーに表示される名前）
CREATOR_NAME = "ilu"

# ③ 生成するXMLファイルの名前（バレないようにランダムな文字列にするのがおすすめ）
# 例: "feed_7a8b9c.xml"
OUTPUT_FILENAME = "secret_feed_12345.xml"
# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝

def get_fanbox_posts(creator_id):
    api_url = f"https://api.fanbox.cc/post.listCreator?creatorId={12372838}&limit=15"
    headers = {'Origin': 'https://www.fanbox.cc'}
    try:
        res = requests.get(api_url, headers=headers)
        res.raise_for_status()
        return res.json().get('body', {}).get('items', [])
    except Exception as e:
        print(f"取得エラー: {e}")
        return []

def main():
    if CREATOR_ID == "YOUR_CREATOR_ID_HERE":
        print("エラー: クリエイターIDが設定されていません")
        sys.exit(1)

    posts = get_fanbox_posts(CREATOR_ID)
    if not posts:
        print("投稿が見つかりませんでした")
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
        fe.title(post.get('title', '無題'))
        
        pub_date = post.get('publishedDatetime')
        if pub_date:
            dt = datetime.datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
            fe.published(dt)
            fe.updated(dt)

        # 本文の抜粋
        body = post.get('body', {})
        content = ""
        if 'text' in body and body['text']:
            clean_text = re.sub(r'<.*?>', '', body['text'])
            content = clean_text[:150] + '...'
        elif 'images' in body and body['images']:
            content = f"画像が {len(body['images'])} 枚投稿されました"
        elif 'files' in body and body['files']:
            content = "ファイルが投稿されました"

        fe.content(content, type='text')

    # ファイル出力
    fg.rss_file(OUTPUT_FILENAME, pretty=True)
    print(f"RSSを生成しました: {OUTPUT_FILENAME}")

if __name__ == "__main__":
    main()
