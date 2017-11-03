import requests
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv


def get_sheet():
    scope = ['https://spreadsheets.google.com/feeds']
    doc_id = os.environ.get('DOC_ID')
    json_path = os.path.expanduser(
        os.environ.get('GOOGLE_SERVICE_CLIENT_JSON'))

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


def insert_review_to_row(sheet, column, review_id, entry):
    author_uri = entry['author']['uri']['label']
    author_name = entry['author']['name']['label']

    app_version = entry['im:version']['label']

    rating = entry['im:rating']['label']
    review_text = '「' + entry['title']['label'] + '」\n\n'
    review_text += entry['content']['label']

    sheet.insert_row([
        review_id,
        author_name + '\n' + author_uri,
        rating_stars(int(rating)),
        review_text,
        app_version
    ], column)


def fetch_review_data(page, app_id):
    res = requests.get(
        'http://itunes.apple.com/jp/rss/customerreviews/page=' +
        str(page) +
        '/id=' +
        app_id +
        '/json')
    return res.json()


def insert_data_from_scratch(sheet, app_id):
    sheet.insert_row([
        'Review ID',
        'Reviewer',
        'Star',
        'Review',
        'Version'
    ], 1)

    page = 1
    while True:
        review_dict = fetch_review_data(page, app_id)
        if review_dict['feed'].get('entry') is None:
            break

        for i, entry in enumerate(review_dict['feed']['entry']):
            if i == 0:
                continue

            review_id = entry['id']['label']
            column = i + 1 + (page - 1) * 50
            insert_review_to_row(sheet, column, review_id, entry)

        page += 1


def insert_only_new_data(sheet, app_id):
    page = 1
    latest_review_id = sheet.acell('A2').input_value

    while True:
        review_dict = fetch_review_data(page, app_id)
        if review_dict['feed'].get('entry') is None:
            break

        for i, entry in enumerate(review_dict['feed']['entry']):
            if i == 0:
                continue

            review_id = entry['id']['label']
            if review_id <= latest_review_id:
                break

            column = i + 1 + (page - 1) * 50
            insert_review_to_row(sheet, column, review_id, entry)

        page += 1


def main(from_scratch):
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    try:
        sheet = get_sheet()
        app_id = os.environ.get('IOS_APP_ID')
        if from_scratch:
            insert_data_from_scratch(sheet, app_id)
        else:
            insert_only_new_data(sheet, app_id)
    except Exception as e:
        print("Error occurred: " + str(e))


def handler(event, context):
    main(False)


# 実行
if __name__ == '__main__':
    main(False)
