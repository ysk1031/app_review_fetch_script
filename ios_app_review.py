import requests
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv


def get_sheet():
    scope = ['https://spreadsheets.google.com/feeds']
    doc_id = os.environ.get('DOC_ID')
    json_path = os.path.expanduser(
        './google_service_client_json/' + os.environ.get('GOOGLE_SERVICE_CLIENT_JSON'))

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        json_path, scope)
    client = gspread.authorize(credentials)
    gfile = client.open_by_key(doc_id)
    return gfile.sheet1


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
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    app_id = os.environ.get('IOS_APP_ID')

    try:
        sheet = get_sheet()
        sheet.update_acell('A1', 'Review ID')
        sheet.update_acell('B1', 'Reviewer')
        sheet.update_acell('C1', 'Star')
        sheet.update_acell('D1', 'Review')
        sheet.update_acell('E1', 'Version')

        page = 1
        while True:
            res = requests.get(
                'http://itunes.apple.com/jp/rss/customerreviews/page=' + str(page) + '/id=' + app_id + '/json')
            review_dict = res.json()

            if review_dict['feed'].get('entry') is None:
                break

            for i, entry in enumerate(review_dict['feed']['entry']):
                if i == 0:
                    continue

                review_id = entry['id']['label']

                author_uri = entry['author']['uri']['label']
                author_name = entry['author']['name']['label']

                app_version = entry['im:version']['label']

                rating = entry['im:rating']['label']
                review_text = '「' + entry['title']['label'] + '」\n\n'
                review_text += entry['content']['label']

                column_str = str(i + 1 + (page - 1) * 50)
                sheet.update_acell('A' + column_str, review_id)
                sheet.update_acell(
                    'B' + column_str, author_name + '\n' + author_uri)
                sheet.update_acell('C' + column_str, rating_stars(int(rating)))
                sheet.update_acell('D' + column_str, review_text)
                sheet.update_acell('E' + column_str, app_version)

            page += 1
    except Exception as e:
        print("Error occurred: " + str(e))


# 実行
if __name__ == '__main__':
    main()
