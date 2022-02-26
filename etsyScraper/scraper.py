import pandas as pd
import requests
import json
import os
import time
from etsyTypes import EtsyShop, Review
from typing import Tuple

class InvalidEtsyAPIKeyError(Exception):

  def __init__(self, value: str, message: str):
    self.value = value
    self.message = message
    super().__init__(message)

class EtsyAPIResponseError(Exception):

  def __init__(self, response: requests.Response):
    self.response_status = response.status_code
    self.message = response['error']
    super().__init__(self.message)

class EtsyShopScraper:

  def __init__(self, shop_name: str):
    self.api_url = "https://openapi.etsy.com/v3/application/"
    self.endpoints = {
      "getShopId": "shops",
      "getReviewsByShop": "shops/{}/reviews"
    }
    self.shop_name = shop_name
    self.etsy_shop: EtsyShop = None
    env_api_key = os.environ.get('ETSY_KEY_STRING')
    if env_api_key is not None or len(env_api_key) > 0:
      self.etsy_header = {'x-api-key': env_api_key}
    else:
      raise InvalidEtsyAPIKeyError(value=env_api_key, message="Either the key does not exist in the .envrc file or the key is 0 characters long.")

  @staticmethod
  def is_200_code(response: requests.Response) -> bool:
    if response.status_code == 200:
      return True
    else:
      return False

  def ping_api(self) -> bool:
    success = False
    response = requests.get(f"{self.api_url}openapi-ping", headers=self.etsy_header)
    if self.is_200_code(response=response):
      success = True
      return success
    else:
      return success

  def get_etsy_shop(self):
    endpoint_key = "getShopId"
    query_header = self.etsy_header
    query_header['shop_name'] = self.shop_name
    query_header['limit'] = 1
    response = requests.get(f"{self.api_url}{self.endpoints[endpoint_key]}", headers=query_header)
    data = response.json()

    self.etsy_shop = self.set_etsy_shop(data=data)

  def set_etsy_shop(self, data) -> EtsyShop:

    data = data["results"][0]
    assert data["shop_name"] == self.shop_name, "Returned Etsy Shop name {} does not equal inputted shop name {}.".format(data["shop_id"], self.shop_name)

    etsy_shop = EtsyShop(
      shop_id=data['shop_id'],
      shop_name=data['shop_name'],
      url=data['url'],
      review_count=data['review_count'],
      review_average=data['review_average'],
      num_favorites=data['num_favorers'])

    return etsy_shop

  @staticmethod
  def parse_reviews(response) -> Tuple[list[Review], int]:

    review_count = response["count"]
    reviews = [
      Review(**review) for review in response["results"]
      ]

    return reviews, review_count

  def get_shop_reviews(self, offset: int) -> Tuple[list[Review], int]:

    reviews: list[Review] = []

    endpoint_key = "getReviewsByShop"
    query_header = self.etsy_header
    query_header['offset'] = offset
    query_header['limit'] = 100

    response = requests.get(f"{self.api_url}{self.endpoints[endpoint_key].format(self.etsy_shop.shop_id)}", headers=query_header)
    if self.is_200_code(response=response):
      reviews, review_count = self.parse_reviews(response=response)
    else:
      raise EtsyAPIResponseError(response=response)

    return reviews, review_count

  def get_all_shop_reviews(self) -> list[Review]:

    all_reviews: list[Review] = []
    review_count: int = 101
    offset: int = 0
    limit: int = 100

    while len(all_reviews) % limit == 0 or review_count > limit:
      reviews = self.get_shop_reviews(offset=offset)
      all_reviews.extend(reviews)
      offset = len(all_reviews)
      if len(all_reviews) == self.etsy_shop.review_count:
        break

    return all_reviews

  @staticmethod
  def convert_Review_to_DataFrame(review: Review) -> pd.DataFrame:

    df = pd.DataFrame(review).T
    df.columns = df.iloc[0, :]
    df = pd.DataFrame(df.iloc[1, :]).T

    return df

  def save_all_data(self, all_reviews: list[Review]):

    data: pd.DataFrame = None

    for review in all_reviews:
      df = self.convert_Review_to_DataFrame(review=review)
      try:
        data = pd.concat([data, df], ignore_index=True)
      except ValueError:
        data = df

    data.to_csv(os.path.join("data", f"{self.shop_name}_etsy_reviews.csv"))


def add(x, y):
  return x + y