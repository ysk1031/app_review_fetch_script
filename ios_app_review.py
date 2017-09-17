import requests
import os


def rating_stars(score):
    if score == 1:
        return "★☆☆☆☆"
    elif score == 2:
        return "★★☆☆☆"
    elif score == 3:
        return "★★★☆☆"
    elif score == 4:
        return "★★★★☆"
    elif score == 5:
        return "★★★★★"
    else:
        return ""


def main():
    app_id = os.getenv("APP_ID", "")

    try:
        res = requests.get(
            'http://itunes.apple.com/jp/rss/customerreviews/page=1/id=' + app_id + '/json')
        review_dict = res.json()

        for i, entry in enumerate(review_dict['feed']['entry']):
            if i == 0:
                continue

            # review_id = entry['id']['label']

            author_uri = entry['author']['uri']['label']
            author_name = entry['author']['name']['label']

            app_version = entry['im:version']['label']

            rating = entry['im:rating']['label']
            review_title = entry['title']['label']
            review_content = entry['content']['label']

            text = ''
            text += '「' + review_title + '」\n'
            text += rating_stars(int(rating)) + ' by ' + \
                author_name + ' (' + author_uri + ')\n'
            text += review_content + '\n\n'
            text += '(iOS版 v' + app_version + ')'

            print('\nレビュー:')
            print(text)
    except:
        print("Error occurred.")


# 実行
if __name__ == '__main__':
    main()
