#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import re
import uuid

import pytest
from selenium.webdriver.support.ui import WebDriverWait

from ... import BrowserID
from .. import restmail


@pytest.mark.nondestructive
class TestSignIn:

    def test_sign_in_helper(self, mozwebqa):
        browser_id = BrowserID(mozwebqa.selenium, mozwebqa.timeout)
        browser_id.sign_in(mozwebqa.email, mozwebqa.password)

        WebDriverWait(mozwebqa.selenium, mozwebqa.timeout).until(
            lambda s: s.find_element_by_id('loggedin').is_displayed())

    def test_sign_in(self, mozwebqa):
        from ...pages.webdriver.sign_in import SignIn
        signin = SignIn(mozwebqa.selenium, mozwebqa.timeout, expect='new')
        signin.email = mozwebqa.email
        signin.click_next(expect='password')
        signin.password = mozwebqa.password
        signin.click_sign_in()

        WebDriverWait(mozwebqa.selenium, mozwebqa.timeout).until(
            lambda s: s.find_element_by_id('loggedin').is_displayed())

    def test_sign_in_new_user_helper(self, mozwebqa):
        restmail_username = 'bidpom_%s' % uuid.uuid1()
        email = '%s@restmail.net' % restmail_username

        from ...pages.webdriver.sign_in import SignIn
        signin = SignIn(mozwebqa.selenium, mozwebqa.timeout, expect='new')
        print 'signing in as %s' % email
        signin.sign_in_new_user(email, 'password')
        mail = restmail.get_mail(restmail_username)
        assert 'Thanks for verifying' in mail[0]['text']

    def test_sign_in_new_user(self, mozwebqa):
        restmail_username = 'bidpom_%s' % uuid.uuid1()
        email = '%s@restmail.net' % restmail_username
        password = 'password'

        from ...pages.webdriver.sign_in import SignIn
        signin = SignIn(mozwebqa.selenium, mozwebqa.timeout, expect='new')
        print 'signing in as %s' % email
        signin.email = email
        signin.click_next(expect='verify')
        signin.password = password
        signin.verify_password = password
        signin.click_verify_email()
        signin.close_window()
        signin.switch_to_main_window()
        mail = restmail.get_mail(restmail_username)
        assert 'Thanks for verifying' in mail[0]['text']

    def test_sign_in_returning_user(self, mozwebqa):
        self.create_verified_user(mozwebqa.selenium, mozwebqa.timeout)
        mozwebqa.selenium.get('%s/' % mozwebqa.base_url)
        WebDriverWait(mozwebqa.selenium, mozwebqa.timeout).until(
            lambda s: s.find_element_by_id('loggedin').is_displayed())

    def create_verified_user(self, selenium, timeout):
        restmail_username = 'bidpom_%s' % uuid.uuid1()
        email = '%s@restmail.net' % restmail_username
        password = 'password'

        from ...pages.webdriver.sign_in import SignIn
        signin = SignIn(selenium, timeout, expect='new')
        signin.sign_in_new_user(email, password)
        mail = restmail.get_mail(restmail_username)
        verify_url = re.search(BrowserID.VERIFY_URL_REGEX,
                               mail[0]['text']).group(0)

        selenium.get(verify_url)
        from ...pages.webdriver.complete_registration import CompleteRegistration
        complete_registration = CompleteRegistration(selenium,
                                                     timeout,
                                                     expect='success')
        assert 'Thank you' in complete_registration.thank_you
        return (email, password)
