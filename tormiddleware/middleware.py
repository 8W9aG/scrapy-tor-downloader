"""The middleware for scrapy-tor-downloader."""
import http
import urllib

import scrapy
import tldextract
from torpy.http.requests import tor_requests_session

from .response import TORResponse


class TORDownloaderMiddleware:

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=scrapy.signals.spider_opened)
        return s

    def should_process_url(self, url: str) -> bool:
        """Whether we should process a URL."""
        extracted = tldextract.extract(url)
        return extracted.suffix == "onion"

    def should_process_request(self, request: scrapy.Request, spider: scrapy.Spider) -> bool:
        """Whether we should process a request."""
        tor_proxy_enabled = request.meta.get("tor_proxy_enabled", spider.settings.get("TOR_PROXY_ENABLED", False))
        if tor_proxy_enabled:
            return True
        return self.should_process_url(request.url)

    def perform_tor_request(self, request: scrapy.Request) -> scrapy.http.Response:
        """Perform a TOR request using a scrapy request."""
        with self.session as tor_session:
            method_function = getattr(tor_session, request.method.lower())
            body = request.body
            if isinstance(body, str):
                body = body.encode("utf8")
            response = method_function(
                request.url,
                headers={x.decode(): request.headers[x].decode() for x in request.headers},
                cookies=request.cookies,
                data=body)
            return TORResponse(
                request.url,
                status=response.status_code,
                headers=response.headers,
                body=response.content,
                request=request)

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        if self.should_process_request(request, spider):
            tor2web_proxy = request.meta.get("tor2web_proxy", spider.settings.get("TOR2WEB_PROXY", None))
            if tor2web_proxy is not None and self.should_process_url(request.url):
                proxy_parse = urllib.parse.urlparse(tor2web_proxy)
                parse = urllib.parse.urlparse(request.url)
                extracted = tldextract.extract(request.url)
                proxy_extracted = tldextract.extract(tor2web_proxy)
                return request.replace(url=urllib.parse.urlunparse(
                    (
                        proxy_parse[0],
                        ".".join([extracted.domain, proxy_extracted.domain, proxy_extracted.suffix]),
                        parse[2],
                        parse[3],
                        parse[4],
                        parse[5],
                    )
                ))
            return self.perform_tor_request(request)
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        if not isinstance(response, TORResponse) and response.status >= http.HTTPStatus.BAD_REQUEST:
            fallback_enabled = request.meta.get("tor_fallback_enabled", spider.settings.get("TOR_FALLBACK_ENABLED", True))
            if fallback_enabled:
                return self.perform_tor_request(request)
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
        self.session = tor_requests_session()
