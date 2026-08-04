import sys
import requests
from feedgen.feed import FeedGenerator
import datetime
import re

# ＝＝＝＝＝＝ 設定 ＝＝＝＝＝＝
# ① RSSを取得したいFANBOXのクリエイターID
CREATOR_ID = "12372838" 

# ② クリエイター名（RSSリーダーに表示される名前）
CREATOR_NAME = "ilu"

# ③ 生成するXMLファイルの名前（バレないようにランダムな文字列にするのがおすすめ）
OUTPUT_FILENAME = "secret_feed_12345.xml"
# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝

def get_fanbox_posts(creator_id):
    api_url = f"https://api.fanbox.cc/post.listCreator?creatorId={creator_id}&limit=15"
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
        
        # タイトルの取得
        title = post.get('title', '無題')
        fe.title(title)
        
        # 日時の取得
        pub_date = post.get('publishedDatetime')
        if pub_date:
            dt = datetime.datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
            fe.published(dt)
            fe.updated(dt)

        # 本文の抜粋（ログインなしのため、有料投稿のbodyはNoneになります）
        body = post.get('body')
        fee = post.get('feeRequired', 0)
        content = ""

        if body:
            # 無料公開されている場合の処理
            if 'text' in body and body['text']:
                clean_text = re.sub(r'<.*?>', '', body['text'])
                content = clean_text[:150] + '...'
            elif 'images' in body and body['images']:
                content = f"画像が {len(body['images'])} 枚公開されています"
            elif 'files' in body and body['files']:
                content = "ファイルが公開されています"
        else:
            # 本文がない ＝ 有料限定投稿の場合の処理
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
