# Steam Reviews
A package of getting game reviews from steam easily, for further text analytics projects.

## Install
The package is available in PyPi.
```shell
pip install steam_reviews
```

## Use

### Basic usage
For example, we load the reviews of Cyberpunk 2077 from the api.
The function `load_from_api` takes two arguments.
- First is necessary, the appid. It can be find in the web page of the game in steam store.
  Like Cyberpunk 2077's page: https://store.steampowered.com/app/1091500/_2077/,
  the number **1091500** in the url is its appid.
- Second can be ignored, if you want to take all the reviews, it controls the number of reviews that
  the program will take from the web api.
```python
from steam_reviews import ReviewLoader
# AppId is 1091500, and we need 1000 reviews
reviews = ReviewLoader().load_from_api(1091500, 1000)
# Save the review text to a list
review_list = reviews.review_list()
print(review_list[0])
# Save the data as json file, provide the folder path as the argument
reviews.save_json('path/to/data/')
```

### With more parameters
You can add more parameters to get customized reviews.
More information can be found in the functions' documents in the source code.

`set_language()` is used  most frequently, it sets the language of the reviews that downloaded by the program.
All supported language can be found here: https://partner.steamgames.com/doc/store/localization.
```python
from steam_reviews import ReviewLoader
# Set the language of reviews to english
reviews_en = ReviewLoader().set_language('english') \
                        .load_from_api(1091500, 1000)
# Set the language of reviews to simplified chinese
reviews_zh = ReviewLoader().set_language('schinese') \
                        .load_from_api(1091500, 1000)
```

### Load reviews of several games
The funciton `load_batch_from_api()` can receive a list containing appids 
and request all the reviews for each of the game.
```python
from steam_reviews import ReviewLoader
appids = [1091500, 1097150]
reviews = ReviewLoader().set_language('english') \
                        .set_num_per_page(50) \
                        .load_batch_from_api(appids, 1000)
```

### Load from local json files
```python
from steam_reviews import ReviewLoader
# File path of the saved json data
file_path = 'path/to/data/reviews_1091500.json'
reviews = ReviewLoader().load_from_local(file_path)
```