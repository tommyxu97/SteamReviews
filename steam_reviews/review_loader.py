import requests
import json
import random
import time
import os
import re
from tqdm import tqdm

from .reviews import Reviews


def _get_api_url():
    return 'https://store.steampowered.com/appreviews/'


def _get_user_agent():
    user_agents = [
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50"
        "(KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 "
        "(KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0);",
        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
        "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
        "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 "
        "(KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; "
        "SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
        "Mozilla/5.0 (X11; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0"
    ]
    return user_agents[random.randint(0, len(user_agents) - 1)]


def _get_dummy_data_dict():
    return {'success': 0, 'query_summary': {'num_reviews': 0}, 'reviews': [], 'cursor': None}


class ReviewLoader:
    """
    Review Loader: Load steam game reviews from web api or local saved files.

    The detailed data api from steam can be found here:
    https://partner.steamgames.com/doc/store/getreviews
    """

    # Default get all reviews
    DEFAULT_NUM_OF_REVIEWS = 300000

    def __init__(self):
        # Parameters of requesting the data
        self.parameters = {
            'json': '1',
            'filter': 'recent',
            'language': 'all',
            'cursor': '*',
            'review_type': 'all',
            'purchase_type': 'all',
            'num_per_page': '100'
        }

        # Default passe at every 100 request counts
        self.request_pause_count = 100

        # The default sleeping time of the thread after every 100 request, set to zero will not pause
        self.request_pause_time = random.randint(10, 60)

        # The default sleeping time of the thread after the request is blocked
        self.request_block_time = 60

        # Need more information of the output
        self.print_more_info = False

        # Fake headers
        self.user_agent = _get_user_agent()

    def set_filter(self, review_filter: str):
        """
        Set filter on the reviews

        :param review_filter: can be set as following values:

            recent – sorted by creation time
            updated – sorted by last updated time
            all – (default) sorted by helpfulness, with sliding windows based on day_range parameter,
                will always find results to return.

        :return: ReviewLoader object
        """
        self.parameters['filter'] = review_filter
        return self

    def set_language(self, language: str):
        """
        Set the language of the reviews

        :param language: language names, all values can be found at
            https://partner.steamgames.com/documentation/languages

        :return: ReviewLoader object
        """
        self.parameters['language'] = language
        return self

    def set_day_range(self, day_range: int):
        """
        Set day range from today

        :param day_range: range from now to n days ago to look for helpful reviews. Only applicable for the “all” filter

        :return: ReviewLoader object
        """
        self.parameters['day_range'] = str(day_range)
        return self

    def set_cursor(self, cursor: str):
        """
        Reviews are returned in batches of 20, so pass "*" for the first set, then the value of "cursor" that was
            returned in the response for the next set, etc.

        :param cursor: cursor string, don't need to set this at most times

        :return: ReviewLoader object
        """
        self.parameters['cursor'] = cursor
        return self

    def set_review_type(self, review_type: str):
        """
        Set the type of reviews

        :param review_type: can be set as following values:
            all – all reviews (default)
            positive – only positive reviews
            negative – only negative reviews

        :return: ReviewLoader object
        """
        self.parameters['review_type'] = review_type
        return self

    def set_purchase_type(self, purchase_type: str):
        """
        Set the type of purchase type of the reviews

        :param purchase_type: can be set as following values:
            all – all reviews
            non_steam_purchase – reviews written by users who did not pay for the product on Steam
            steam – reviews written by users who paid for the product on Steam (default)

        :return: ReviewLoader object
        """
        self.parameters['purchase_type'] = purchase_type
        return self

    def set_num_per_page(self, num_per_page: int):
        """
        Set how many reviews will be returned after one request

        :param num_per_page: int, number of reviews per request

        :return: ReviewLoader object
        """
        self.parameters['num_per_page'] = str(num_per_page)
        return self

    def set_pause_count(self, pause_count: int):
        """
        After every certain `pause_count` request, the thread will sleep `pause_time` seconds

        :param pause_count: numbers of requests

        :return: ReviewLoader object
        """
        self.request_pause_count = pause_count
        return self

    def set_pause_time(self, pause_time: int):
        """
        After every certain n request, the thread will sleep `pause_count` seconds

        :param pause_time: seconds that the thread sleeps

        :return: ReviewLoader object
        """
        self.request_pause_time = pause_time
        return self

    def set_block_time(self, block_time: int):
        """
        If the program encounters unsuccessful response status, the time it will wait before next request

        :param block_time: seconds that the thread sleeps

        :return: ReviewLoader object
        """
        self.request_block_time = block_time
        return self

    def update_params(self, new_params: dict):
        """
        Update the request parameters by the given dictionary

        :param new_params: dict contains the user's customized parameters
            Example: new_params = {
                'language': 'all',
                'num_per_page': '50
            }

        :return:
        """
        for k, v in new_params:
            if k in self.parameters:
                self.parameters[k] = v

    def print_request_parameters(self):
        """
        Print the request parameters

        :return: None
        """
        print("Steam review api requests will use the following parameters:")
        print(self.parameters)

    def load_from_api(self, appid: int or str, num: int = DEFAULT_NUM_OF_REVIEWS):
        """
        Load review data from steam web api

        :param appid: the appid of the game, can be found in the url link of the game web page
        :param num: the number of reviews the program will get

        :return: Reviews object
        """
        request_count = 0
        response_code = 200
        reviews_num = 0
        expected_total = 0

        # If review_type set to positive or negative, there will be no expected number of reviews
        has_expected_total = self.parameters['review_type'] == 'all'

        # Use tqdm to show a progress bar
        progress_bar = None

        # After apply the filter to all and the day range, there will be duplicated reviews
        reviews_ids = None

        session = requests.session()
        session.headers['User-Agent'] = _get_user_agent()

        # Initial request
        if self.print_more_info:
            self.print_request_parameters()
        response = session.get(_get_api_url() + str(appid), params=self.parameters)
        response_code = response.status_code
        request_count += 1
        if response_code == 200:
            data = response.json()
            new_reviews_num = data['query_summary']['num_reviews']
            if new_reviews_num == 0:
                print("Stop the request, due to having no reviews.")
                session.close()
                return Reviews(int(appid), _get_dummy_data_dict())
            reviews_num += new_reviews_num
            reviews_ids = set([review['recommendationid'] for review in data['reviews']])
            if has_expected_total:
                expected_total = data['query_summary']['total_reviews']
            else:
                expected_total = self.DEFAULT_NUM_OF_REVIEWS
            self.parameters['cursor'] = data['cursor']
            # Set progress bar to show the process of getting the data
            progress_bar = tqdm(total=min(expected_total, num))
            progress_bar.update(new_reviews_num)
            if num >= expected_total:
                print("Start the request. The game has total {} reviews.".format(expected_total))
            else:
                print("Start the request. The game has total {} reviews, and will only get {} reviews."
                      .format(expected_total, num))
        else:
            print("Can't complete the request now. Response status is {}.".format(response_code))
            session.close()
            return Reviews(int(appid), _get_dummy_data_dict())

        # Requests
        try:
            while reviews_num < num:
                if response_code >= 400:
                    print("Can't complete the request now. Wait for {} seconds.".format(self.request_block_time))
                    time.sleep(self.request_block_time)
                if (self.request_pause_time is not 0) & (request_count % 100 == 0):
                    print("Requests count is {}, will wait for {} seconds."
                          .format(request_count, self.request_pause_time))
                    time.sleep(self.request_pause_time)
                response = session.get(_get_api_url() + str(appid), params=self.parameters)
                response_code = response.status_code
                request_count += 1
                new_data = response.json()
                success_flag = new_data['success'] == 1
                if new_reviews_num == 0 or not success_flag:
                    # if there is no data or the successful flag is False, then break the loop
                    break
                # Update cursor to get the next batch of data
                self.parameters['cursor'] = new_data['cursor']
                new_reviews_num = new_data['query_summary']['num_reviews']
                new_reviews_ids = set([review['recommendationid'] for review in new_data['reviews']])
                if reviews_ids.issuperset(new_reviews_ids):
                    print('Stop request due to getting all duplicated review in a batch. There are only '
                          '{} reviews after applying the filter.'.format(reviews_num))
                    break
                actual_new_review_num = 0
                for review in new_data['reviews']:
                    review_id = review['recommendationid']
                    if review_id not in reviews_ids:
                        data['reviews'].append(review)
                        actual_new_review_num += 1
                data['query_summary']['num_reviews'] += actual_new_review_num
                reviews_num += actual_new_review_num
                progress_bar.update(actual_new_review_num)
                reviews_ids.update(new_reviews_ids)
        except KeyboardInterrupt:
            # Handle user's cancel
            print("\nStop requests now. Get {} reviews and expected total is {}.".format(reviews_num, expected_total))
            print("If you want to continue the request, please set cursor as {}.".format(self.parameters['cursor']))
            session.close()
            return Reviews(int(appid), data)

        # Remove the reviews where index > num
        if len(data['reviews']) > num:
            data['reviews'] = data['reviews'][:num]
        session.close()
        return Reviews(int(appid), data)

    def load_batch_from_api(self, appids: list, num: int = DEFAULT_NUM_OF_REVIEWS):
        """
        Load reviews of several games

        :param appids: a list contrains all the appids
        :param num: number of review the program will get

        :return: Reviews object
        """
        reviews = []
        for appid in appids:
            self.parameters['cursor'] = '*'
            reviews.append(self.load_from_api(appid, num))
        return reviews

    def load_from_local(self, file_path: str):
        """
        Load reviews data from local file system

        :param file_path: the json file path

        :return: Reviews object
        """
        if not os.path.exists(file_path):
            print("File path: {} not exists!".format(file_path))
            return
        res = re.match(r'reviews_\d+.json', file_path)
        if res is not None:
            appid = res.group()
        else:
            appid = -1
        data = json.load(open(file_path, 'r'))
        return Reviews(appid, data)
