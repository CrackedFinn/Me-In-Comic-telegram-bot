import io

from qqddm import AnimeConverter, InvalidQQDDMApiResponseException, IllegalPictureQQDDMApiResponseException
from PIL import Image
from io import BytesIO
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

API_VERSION = 2
USERAGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0"
PROXY = os.getenv('PROXY')


def GetImage(picture_bytes, width, height):
    if width >= height:
        image_is_wide = True  # image is wide / square
    else:
        image_is_wide = False  # image is vertical

    converter = AnimeConverter(generate_api_version=API_VERSION, global_useragents=[USERAGENT], global_proxy=PROXY)

    try:
        result = converter.convert(picture_bytes)
        url = [str(url) for url in result.pictures_urls][2]
        in_memory = BytesIO(requests.get(url).content)
        im = Image.open(in_memory)
        if image_is_wide:
            cropped = im.crop((19, 19, 1097, 737))  # (left, top, right, bottom)
        else:
            cropped = im.crop((29, 31, 797, 1184))  # (left, top, right, bottom)
        in_memory.seek(0)
        in_memory.truncate(0)
        im.close()

        return cropped
    except IllegalPictureQQDDMApiResponseException:
        return "❌ The image provided is forbidden, try with another picture"
    except InvalidQQDDMApiResponseException as ex:
        if json.loads(ex.response_body)["code"] == 1001:
            return "❌ It looks like there is no human face at the image. *Try uploading a photo of a person.*"
        else:
            return "❌ Oups... An error occurred while processing your photo. Please contact support with the following information:\n\n_" + f"API returned error ({ex}); response body: {ex.response_body}" + "_"
