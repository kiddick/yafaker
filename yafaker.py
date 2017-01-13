"""ez reg"""

import requests
import lxml.html
import webbrowser

import random
import string

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 MeeGo; NokiaN9 AppleWebKit/534.13 KHTML, like Gecko NokiaBrowser/8.5.0 Mobile Safari/534.13',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
    'Upgrade-Insecure-Requests': '1',
    'Connection': 'keep-alive',
    'Host': 'passport.yandex.com',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache'
}

FIDDLER = {
    "http": "127.0.0.1:8888",
    "https": "127.0.0.1:8888"
}

REG_URL = ('https://passport.yandex.com/registration?'
           'from=mail&require_hint=1&origin=hostroot_com_nol_mobile_left')


def get_nick(length):
    return random.choice(string.ascii_lowercase) + ''.join(
        random.choice(string.ascii_lowercase + string.digits)
        for _ in range(length - 1)
    )


def parse_params(content):
    doc = lxml.html.fromstring(content)
    return (
        doc.xpath('//input[@id="track_id"]')[0].get('value'),
        doc.xpath('//input[@class="captcha_key"]')[0].get('value'),
        doc.xpath('//img[@class="captcha__captcha__text"]')[0].get('src')
    )


def cspreport(session, headers, prx):
    json_data = {
        "csp-report": {
            "document-uri": REG_URL,
            "referrer": "",
            "violated-directive": "style-src 'self' yastatic.net yandex.st",
            "effective-directive": "style-src",
            "original-policy": (
                "default-src 'self'; "
                "img-src 'self' data: "
                "passport.yandex.ru yastatic.net "
                "*.captcha.yandex.net "
                "mc.yandex.ru "
                "yandex.st "
                "avatars.yandex.net; "
                "script-src 'self' "
                "'unsafe-eval' "
                "'unsafe-inline' "
                "yastatic.net "
                "yandex.st "
                "mc.yandex.ru "
                "pass.yandex.ru "
                "pass.yandex.com.tr "
                "pass.yandex.com; "
                "connect-src 'self' "
                "yastatic.net "
                "yandex.st "
                "*.captcha.yandex.net "
                "mc.yandex.ru; "
                "frame-src "
                "legal.yandex.ru "
                "legal.yandex.com.tr "
                "legal.yandex.com "
                "legal.yandex.ua; "
                "style-src 'self' "
                "yastatic.net "
                "yandex.st; "
                "object-src 'self' "
                "yastatic.net "
                "*.captcha.yandex.net; "
                "font-src 'self' "
                "yastatic.net; "
                "report-uri /cspreport"),
            "blocked-uri": "",
            "status-code": 0
        }
    }

    session.post(
        'https://passport.yandex.com/cspreport',
        headers=headers,
        json=json_data,
        proxies=prx,
        verify=False
    )


def main():
    s = requests.Session()
    r = s.get(REG_URL, headers=HEADERS, proxies={}, verify=False)
    cspreport(s, HEADERS, {})

    HEADERS['Origin'] = 'https://passport.yandex.com'
    HEADERS['Referer'] = REG_URL
    HEADERS['Cache-Control'] = 'max-age=0'

    nickname = get_nick(7)

    track_id, captcha_key, captcha_src = parse_params(r.content)
    webbrowser.open(captcha_src)
    print 'enter captcha:'
    canswer = raw_input()
    print 'enter password:'
    password = raw_input()

    mail_data = {
        'track_id': track_id,
        'language': 'en',
        'firstname': nickname,
        'lastname': nickname,
        'login': nickname,
        'password': password,
        'password_confirm': password,
        'human-confirmation': 'captcha',
        'phone-confirm-state': '',
        'phone_number_confirmed': '',
        'phone_number': '',
        'phone-confirm-password': '',
        'hint_question_id': '12',
        'hint_question': '',
        'hint_answer': 'lector',
        'answer': canswer,
        'key': captcha_key,
        'captcha_mode': 'text',
        'eula_accepted': 'on'
    }

    s.post(REG_URL, headers=HEADERS, data=mail_data, proxies={}, verify=False)

    HEADERS.pop('Host', None)
    s.post(
        'https://passport.yandex.ru/auth?twoweeks=yes', headers=HEADERS,
        data={
            'login': nickname,
            'passwd': password,
            'retpath': 'https://tech.yandex.ru/keys/get/?service=dict'
        },
        proxies={},
        verify=False
    )

    print 'login: {}@yandex.ru'.format(nickname)
    print 'password: {}'.format(password)


if __name__ == '__main__':
    main()
