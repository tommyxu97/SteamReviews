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
```python
from steam_reviews import ReviewLoader
reviews = ReviewLoader().load_from_api(1091500, 1000)
review_list = reviews.review_list()
print(review_list[0])
reviews.save_json('path_to/data/')
```

### With more parameters
You can add more parameters to get customized reviews.
More information can be found in the functions' documents.
```python
from steam_reviews import ReviewLoader
reviews = ReviewLoader().set_language('english') \
                        .set_num_per_page(50) \
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
file_path = 'path/to/data/reviews_1091500.json'
reviews = ReviewLoader().load_from_local(file_path)
```