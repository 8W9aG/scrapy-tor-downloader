# scrapy-tor-downloader

<a href="https://pypi.org/project/scrapy-tor-downloader/">
    <img alt="PyPi" src="https://img.shields.io/pypi/v/scrapy-tor-downloader">
</a>

Scrapy middleware with TOR support for more robust scrapers or anonymous scraping.

## Dependencies :globe_with_meridians:

* [Python 3.7](https://www.python.org/downloads/release/python-370/)
* [Scrapy 2.4.0](https://scrapy.org/)
* [torpy 1.1.6](https://github.com/torpyorg/torpy)

## Installation :inbox_tray:

This is a python package hosted on pypi, so to install simply run the following command:

`pip install scrapy-tor-downloader`

## Settings

### TOR_PROXY_ENABLED

Whether TOR is used to proxy any request (defaults to false).

Meta field to enable/disable this per request is: `tor_proxy_enabled`

### TOR_FALLBACK_ENABLED

Whether TOR is used when a request fails as a fallback (defaults to true).

Meta field to enable/disable this per request is: `tor_fallback_enabled`

### TOR2WEB_PROXY

Whether a [tor2web](https://www.tor2web.org/) proxy is used for onion address. The value of this setting is the domain for the proxy.

Meta field to add this per request is: `tor2web_proxy`

### tor_reset_session

Whether to reset the TOR session before processing the request. This field only exists in the meta on the request as `tor_reset_session` and is a boolean.

## Usage example :eyes:

In order to use this plugin simply add the following settings and substitute your variables:

```py
DOWNLOADER_MIDDLEWARES = {
    "tormiddleware.middleware.TORDownloaderMiddleware": 631
}
```

This will immediately allow you begin using TOR as a fallback when one of your requests fail. In order to use it as a proxy you can add the following to your settings:

```py
TOR_PROXY_ENABLED = True
```

This will make every request hit TOR for a response. If you have turned the proxy on the TOR fallback is ignored, however if it is off the fallback is still on by default, which means if a request returns an error it will be tried again on TOR. In order to turn this off add the following to your settings:

```py
TOR_FALLBACK_ENABLED = False
```

If you want to make use of [tor2web](https://www.tor2web.org/) proxies for onion addresses, you can add it to the settings like so:

```py
TOR2WEB_PROXY = "https://onion.moe"
```

## License :memo:

The project is available under the [MIT License](LICENSE).
