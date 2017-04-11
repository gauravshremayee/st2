# Licensed to the StackStorm, Inc ('StackStorm') under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from oslo_config import cfg
from webob.headers import ResponseHeaders

from st2common.constants.api import REQUEST_ID_HEADER
from st2common.constants.auth import HEADER_ATTRIBUTE_NAME
from st2common.constants.auth import HEADER_API_KEY_ATTRIBUTE_NAME
from st2common.router import Request, Response


class CorsMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = Request(environ)

        def custom_start_response(status, headers, exc_info=None):
            headers = ResponseHeaders(headers)

            origin = request.headers.get('Origin')
            origins = set(cfg.CONF.api.allow_origin)

            # Build a list of the default allowed origins
            public_api_url = cfg.CONF.auth.api_url

            # Default gulp development server WebUI URL
            origins.add('http://127.0.0.1:3000')

            # By default WebUI simple http server listens on 8080
            origins.add('http://localhost:8080')
            origins.add('http://127.0.0.1:8080')

            if public_api_url:
                # Public API URL
                origins.add(public_api_url)

            if origin:
                if '*' in origins:
                    origin_allowed = '*'
                else:
                    # See http://www.w3.org/TR/cors/#access-control-allow-origin-response-header
                    origin_allowed = origin if origin in origins else 'null'
            else:
                origin_allowed = list(origins)[0]

            methods_allowed = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
            request_headers_allowed = ['Content-Type', 'Authorization', HEADER_ATTRIBUTE_NAME,
                                       HEADER_API_KEY_ATTRIBUTE_NAME, REQUEST_ID_HEADER]
            response_headers_allowed = ['Content-Type', 'X-Limit', 'X-Total-Count',
                                        REQUEST_ID_HEADER]

            headers['Access-Control-Allow-Origin'] = origin_allowed
            headers['Access-Control-Allow-Methods'] = ','.join(methods_allowed)
            headers['Access-Control-Allow-Headers'] = ','.join(request_headers_allowed)
            headers['Access-Control-Expose-Headers'] = ','.join(response_headers_allowed)

            return start_response(status, headers._items, exc_info)

        if request.method == 'OPTIONS':
            return Response()(environ, custom_start_response)
        else:
            return self.app(environ, custom_start_response)
