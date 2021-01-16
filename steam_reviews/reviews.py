import json
import os


class Reviews:
    """
    The class hold the reviews data of a certain game.
    """

    appid = None
    data = None

    def __init__(self, appid: int, data: dict):
        self.appid = appid
        self.data = data

    def __len__(self):
        return len(self.data['reviews'])

    def save_json(self, file_path: str = ''):
        if (file_path == '') | (not os.path.exists(file_path)):
            print('File path not exists, save at default folder.')
            file_path = os.getcwd() + '/'
        file_name = 'reviews_' + str(self.appid) + '.json'
        open(file_path + file_name, 'w').write(json.dumps(self.data))
        print('File saved at {}.'.format(file_path + file_name))

    def get_appid(self):
        return self.appid

    def raw_dict(self):
        return self.data

    def raw_json(self):
        return self.data

    def review_dict(self):
        return self.data['reviews']

    def review_list(self):
        reviews = []
        for review in self.data['reviews']:
            reviews.append(review['review'])
        return reviews
