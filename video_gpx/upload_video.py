#!/usr/bin/python
import argparse
import shlex
import json
import os
import httplib
import httplib2
import random
import sys
import time

import logging

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
                        httplib.IncompleteRead, httplib.ImproperConnectionState,
                        httplib.CannotSendRequest, httplib.CannotSendHeader,
                        httplib.ResponseNotReady, httplib.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google Developers Console at
# https://console.developers.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = r"./client_secrets.json"

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the Developers Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def get_authenticated_service(args):
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                                   scope=YOUTUBE_UPLOAD_SCOPE,
                                   message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, args)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                 http=credentials.authorize(httplib2.Http()))


def initialize_upload(youtube, options):
    body = dict(
        snippet=dict(
            title=options.title,
            categoryId=options.category
        ),
        status=dict(
            privacyStatus=options.privacyStatus
        )
    )

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        # Setting "chunksize" equal to -1 in the code below means that the entire
        # file will be uploaded in a single HTTP request. (If the upload fails,
        # it will still be retried where it left off.) This is usually a best
        # practice, but if you're using Python older than 2.6 or if you're
        # running on App Engine, you should set the chunksize to something like
        # 1024 * 1024 (1 megabyte).
        media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
    )

    return resumable_upload(insert_request)


# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(insert_request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            status, response = insert_request.next_chunk()
            if 'id' in response:
                videoId = response['id']
                return {'videoId': videoId, 'uploaded': 'succeeded'}
            else:
                print ("The upload failed with an unexpected response: %s" % response)
                return {'uploaded': 'no video id', 'response': response}

        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                                     e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e

        if error is not None:
            print (error)
            retry += 1
            if retry > MAX_RETRIES:
                exit("No longer attempting to retry.")

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print ("Sleeping %f seconds and then retrying...", sleep_seconds)
            time.sleep(sleep_seconds)


def parse_args(cmd=None):
    if isinstance(cmd, (str, unicode)):
        cmd = shlex.split(cmd)
    try:
        argparser.add_argument("--file", required=True, help="Video file to upload")
        argparser.add_argument("--title", help="Video title", default="Test Title")
        argparser.add_argument("--category", default="28")
        argparser.add_argument("--privacyStatus", choices=VALID_PRIVACY_STATUSES,
                               default=VALID_PRIVACY_STATUSES[0], help="Video privacy status. Default 0: public")

        # argument for output
        argparser.add_argument("--upload-logger", help="the file path to store upload result", default='upload_result.log')
        argparser.add_argument("--verbose", action='store_true', help="verbose on output")
    except argparse.ArgumentError as e:
        pass

    args = argparser.parse_args(cmd) if cmd is not None else argparser.parse_args()
    return args


def log_msg(logger, args, upload_result):
    upload_result['title'] = args.title
    upload_result['clip_name'] = args.file
    msg = json.dumps(upload_result)
    logger.info(msg)


def set_Logger(args):
    logger = logging.getLogger(args.upload_logger)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(args.upload_logger)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s\t%(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


class Upload:
    def __init__(self, cmd=None):
        self.args = parse_args(cmd)

    def upload(self):
        if not os.path.exists(self.args.file):
            return {'uploaded': 'no clip file'}
        yt = get_authenticated_service(self.args)
        try:
            return initialize_upload(yt, self.args)
        except HttpError as e:
            return {'upload': 'http error', 'error': 'http status: {}, content: {}'.format(e.resp.status, e.content)}

    def get_args(self):
        return self.args


if __name__ == '__main__':

    upload = Upload()
    upload_result = upload.upload()
    args = upload.get_args()
    logger = set_Logger(args)
    log_msg(logger, args, upload_result)
