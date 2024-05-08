"""Configuration file for pytest tests."""

import pytest


@pytest.fixture
def firefox_options(firefox_options):
    firefox_options.add_argument("-headless")
    return firefox_options


@pytest.fixture
def chrome_options(chrome_options):
    chrome_options.add_argument("-headless")
    return chrome_options


@pytest.fixture
def selenium(selenium):
    selenium.set_window_size(1024, 600)
    selenium.maximize_window()
    return selenium
