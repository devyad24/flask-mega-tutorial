from flask import current_app
from google.oauth2 import service_account
import os
from google.cloud import translate_v2 as translate
from app.utils import googleSignup


def get_google_credentials():
    try:
        credentials = service_account.Credentials.from_service_account_file(current_app.config['GOOGLE_APPLICATION_CREDENTIALS'])
        return credentials
    except Exception as e:
        raise e 

def translate_text(target: str, text: str) -> dict:
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    translate_client = translate.Client(credentials=googleSignup.get_google_credentials())

    if isinstance(text, bytes):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target)

    print("Text: {}".format(result["input"]))
    print("Translation: {}".format(result["translatedText"]))
    print("Detected source language: {}".format(result["detectedSourceLanguage"]))

    return result
