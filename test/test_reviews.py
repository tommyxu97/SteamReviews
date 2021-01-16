import unittest
import os

from steam_reviews import ReviewLoader


class Test(unittest.TestCase):

    def test_from_api(self):
        reviews = ReviewLoader().load_from_api(1091500, 1000)
        self.assertEqual(len(set([review['recommendationid'] for review in reviews.review_dict()])), 1000)

    def test_from_api_of_empty_reviews(self):
        reviews = ReviewLoader().load_from_api(123456789, 1000)
        self.assertEqual(len(set([review['recommendationid'] for review in reviews.review_dict()])), 0)

    def test_from_api_with_custom_parameters(self):
        reviews = ReviewLoader().set_filter('all') \
                                .set_language('english') \
                                .set_day_range(2) \
                                .set_review_type('positive') \
                                .set_purchase_type('steam') \
                                .set_num_per_page(50) \
                                .load_from_api(1091500, 1000)
        self.assertEqual(len(set([review['recommendationid'] for review in reviews.review_dict()])),
                         len([review['recommendationid'] for review in reviews.review_dict()]))

    def test_batch_load_from_api(self):
        reviews_list = ReviewLoader().load_batch_from_api([1091500, 1097150], 100)
        self.assertTrue((len(reviews_list[0]) > 0) & (len(reviews_list[1]) > 0))

    def test_reviews(self):
        reviews = ReviewLoader().load_from_api(1091500, 100)
        raw_dict, raw_json = reviews.raw_dict(), reviews.raw_json()
        review_dict, review_list = reviews.review_list(), reviews.review_dict()
        reviews.save_json()
        self.assertTrue(True)

    def test_load_from_local(self):
        file_path = os.getcwd() + '/' + 'reviews_1091500.json'
        reviews = ReviewLoader().load_from_local(file_path)
        self.assertGreater(len(reviews), 0)
