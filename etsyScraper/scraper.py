import pandas as pd
import requests
import json
import os
import time
from etsyTypes import EtsyShop

class InvalidEtsyAPIKeyError(Exception):

  def __init__(self, value: str, message: str):
    self.value = value
    self.message = message
    super().__init__(message)

class EtsyShopScraper:

  def __init__(self, shop_name: str):
    self.api_url = "https://openapi.etsy.com/v3/application/{}"
    self.endpoints = {
      "getShopId": "shops",
      "getReviewsByShop": "shops/{shop_id}/reviews"
    }
    self.shop_name = shop_name
    self.etsy_shop: EtsyShop = None
    env_api_key = os.environ.get('ETSY_KEY_STRING')
    if env_api_key is not None or len(env_api_key) > 0:
      self.etsy_header = {'x-api-key': env_api_key}
    else:
      raise InvalidEtsyAPIKeyError(value=env_api_key, message="Either the key does not exist in the .envrc file or the key is 0 characters long.")

  @staticmethod
  def is_200_code(response: requests.Response):
    if response.status_code == 200:
      return True
    else:
      return False

  def ping_api(self):
    success = False
    response = requests.get(f"{self.api_url}openapi-ping", headers=self.etsy_header)
    if self.is_200_code(response=response):
      success = True
      return success
    else:
      return success

  def get_etsy_shop(self):
    endpoint_key = "getShopId"
    response = requests.get(f"{self.api_url}{self.endpoints[endpoint_key]}", headers=self.etsy_header)
    data = response.json()








def add(x, y):
  return x + y