import argparse
import json
import requests
import urllib.parse
import sys
from colorama import init, Fore, Style
import datetime
import re
from bs4 import BeautifulSoup
import html
import textwrap
import os

class SwaggerTester:
    def __init__(self):
        init()  # 初始化colorama
        self.sensitive_params = [
            'token', 'password', 'secret', 'api_key', 'apikey', 'access_token',
            'url', 'link', 'redirect', 'path', 'file', 'domain',
            'callback', 'forward', 'from', 'location', 'uri'
        ]
        self.results = {
            'unauthorized': [],
            'sensitive': [],
            'failed': []
        }
        self.param_name_hints = {
            'id': lambda: 123,
            'ids': lambda: [1, 2, 3],
            'name': lambda: 'test_name',
            'username': lambda: 'testuser',
            'email': lambda: 'test@example.com',
            'path': lambda: '/example/path',
            'category': lambda: 'default',
            'tag': lambda: 'example_tag',
            'description': lambda: 'test description',
            'phone': lambda: '123-456-7890',
            'address': lambda: '123 Main St',
            'city': lambda: 'Anytown',
            'country': lambda: 'USA',
            'code': lambda: 'ABC123XYZ',
            'status': lambda: 'active',
            'type': lambda: 'example_type',
            'value': lambda: 'test_value',
            'key': lambda: 'test_key',
            'date': lambda: datetime.datetime.now().strftime("%Y-%m-%d"),
            'time': lambda: datetime.datetime.now().strftime("%H:%M:%S"),
            'datetime': lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'timestamp': lambda: int(datetime.datetime.now().timestamp()),
            'flag': lambda: True,
            'count': lambda: 10,
            'page': lambda: 1,
            'size': lambda: 20,
            'sort': lambda: 'name',
            'order': lambda: 'asc',
            'filter': lambda: 'example_filter',
            'search': lambda: 'example_search',
            'keyword': lambda: 'example_keyword',
            'version': lambda: 'v1',
            'group': lambda: 'example_group',
            'role': lambda: 'user',
            'permission': lambda: 'read',
            'setting': lambda: 'default_setting',
            'config': lambda: {'key': 'value'},
            'data': lambda: {'item': 'value'},
            'info': lambda: 'example info',
            'message': lambda: 'test message',
            'content': lambda: 'example content',
            'text': lambda: 'example text',
            'title': lambda: 'Test Title',
            'subject': lambda: 'Test Subject',
            'body': lambda: 'example body',
            'comment': lambda: 'test comment',
            'note': lambda: 'example note',
            'reason': lambda: 'test reason',
            'token': lambda: 'test_token', # Although token is sensitive, for testing purpose we need a value
            'password': lambda: 'P@$$wOrd', # Although password is sensitive, for testing purpose we need a value
            'secret': lambda: 'secret_value', # Although secret is sensitive, for testing purpose we need a value
            'api_key': lambda: 'api_key_value', # Although api_key is sensitive, for testing purpose we need a value
            'apikey': lambda: 'apikey_value', # Although apikey is sensitive, for testing purpose we need a value
            'access_token': lambda: 'access_token_value', # Although access_token is sensitive, for testing purpose we need a value
            'url': lambda: 'http://example.com', # Although url is sensitive, for testing purpose we need a value
            'link': lambda: 'http://example.com/link', # Although link is sensitive, for testing purpose we need a value
            'redirect': lambda: 'http://example.com/redirect', # Although redirect is sensitive, for testing purpose we need a value
            'path_param': lambda: '/example/path_param', # Although path is sensitive, for testing purpose we need a value, and avoid conflict with 'path'
            'file': lambda: 'example.txt', # Although file is sensitive, for testing purpose we need a value
            'domain': lambda: 'example.com', # Although domain is sensitive, for testing purpose we need a value
            'callback': lambda: 'http://example.com/callback', # Although callback is sensitive, for testing purpose we need a value
            'forward': lambda: 'http://example.com/forward', # Although forward is sensitive, for testing purpose we need a value
            'from_param': lambda: 'example_from', # Although from is sensitive, for testing purpose we need a value, and avoid conflict with 'from' keyword
            'location': lambda: 'example_location', # Although location is sensitive, for testing purpose we need a value
            'uri': lambda: '/example/uri' # Although uri is sensitive, for testing purpose we need a value
        }

    def load_swagger_spec(self, source, is_url=False):
        try:
            if is_url:
                response = requests.get(source)
                return response.json()
            else:
                with open(source, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"{Fore.RED}Error loading Swagger specification: {str(e)}{Style.RESET_ALL}")
            sys.exit(1)

    def test_endpoint(self, base_url, path, method, operation, proxies=None):
        url = urllib.parse.urljoin(base_url, path)
        print(f"\n{Fore.CYAN}Testing {method.upper()} {url}{Style.RESET_ALL}")

        # 检查敏感参数
        sensitive_found = []
        parameters = operation.get('parameters', [])
        for param in parameters:
            param_name = param.get('name', '').lower()
            if any(s in param_name for s in self.sensitive_params):
                sensitive_found.append(param_name)

        if sensitive_found:
            print(f"{Fore.GREEN}Found sensitive parameters: {', '.join(sensitive_found)}{Style.RESET_ALL}")
            self.results['sensitive'].append({
                'method': method,
                'url': url,
                'sensitive_params': sensitive_found
            })

        # 测试端点
        try:
            headers = {'Content-Type': 'application/json'}
            data = self.generate_test_data(parameters)

            if method.lower() == 'get':
                response = requests.get(url, params=data, headers=headers, proxies=proxies, verify=False)
            elif method.lower() == 'post':
                response = requests.post(url, json=data, headers=headers, proxies=proxies, verify=False)
            elif method.lower() == 'put':
                response = requests.put(url, json=data, headers=headers, proxies=proxies, verify=False)
            elif method.lower() == 'delete':
                response = requests.delete(url, json=data, headers=headers, proxies=proxies, verify=False)
            else:
                print(f"{Fore.YELLOW}Unsupported method: {method}{Style.RESET_ALL}")
                return

            status_code = response.status_code
            if 200 <= status_code < 400:
                print(f"{Fore.RED}Possible unauthorized access: Status {status_code}{Style.RESET_ALL}")
                self.results['unauthorized'].append({
                    'method': method,
                    'url': url,
                    'status_code': status_code,
                    'request': data,
                    'response': self.get_response_content(response)
                })
            else:
                print(f"Status: {status_code}")

        except Exception as e:
            print(f"{Fore.RED}Error testing endpoint: {str(e)}{Style.RESET_ALL}")
            self.results['failed'].append({
                'method': method,
                'url': url,
                'error': str(e)
            })

    def generate_test_data(self, parameters):
        data = {}
        for param in parameters:
            param_name = param.get('name', '').lower()
            param_type = param.get('type', 'string')
            param_in = param.get('in')

            if param_in in ['query', 'body']:
                found_hint = False
                for hint_keyword, value_generator in self.param_name_hints.items():
                    if hint_keyword in param_name:
                        data[param['name']] = value_generator()
                        found_hint = True
                        break # Stop after finding the first hint match

                if not found_hint: # Fallback to type-based default if no hint is found
                    if param_type == 'string':
                        data[param['name']] = 'test'
                    elif param_type == 'integer':
                        data[param['name']] = 1
                    elif param_type == 'boolean':
                        data[param['name']] = True
                    elif param_type == 'number':
                        data[param['name']] = 1.0 # or other default number
                    elif param_type == 'array':
                        data[param['name']] = ['item1', 'item2'] # or other default array
                    elif param_type == 'object':
                        data[param['name']] = {'key': 'value'} # or other default object
                    else:
                        data[param['name']] = 'default_value' # Generic default for unknown types
        return data

    def get_response_content(self, response):
        try:
            return response.json()
        except:
            return response.text

    def wrap_text(self, text, width=100):
        """将长文本换行"""
        if isinstance(text, str):
            return '\n'.join(textwrap.wrap(text, width=width))
        elif isinstance(text, dict):
            return json.dumps(text, indent=2)
        return str(text)

    def format_json(self, data):
        """格式化JSON数据"""
        try:
            if isinstance(data, str):
                return json.dumps(json.loads(data), indent=2)
            return json.dumps(data, indent=2)
        except:
            return str(data)

    def generate_report(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"swagger_test_report_{timestamp}.html"

        css_style = """
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            .section {
                margin-bottom: 30px;
                background-color: white;
                padding: 15px;
                border-radius: 5px;
            }
            .endpoint {
                border: 1px solid #ddd;
                padding: 15px;
                margin: 10px 0;
                border-radius: 5px;
                word-wrap: break-word;
            }
            .unauthorized {
                background-color: #fff2f2;
                border-left: 5px solid #ff4444;
            }
            .sensitive {
                background-color: #f2fff2;
                border-left: 5px solid #44ff44;
            }
            .failed {
                background-color: #f2f2f2;
                border-left: 5px solid #888888;
            }
            pre {
                background-color: #f8f8f8;
                padding: 10px;
                border-radius: 3px;
                overflow-x: auto;
                white-space: pre-wrap;
                word-wrap: break-word;
            }
            .method {
                display: inline-block;
                padding: 3px 8px;
                border-radius: 3px;
                color: white;
                font-weight: bold;
            }
            .get { background-color: #61affe; }
            .post { background-color: #49cc90; }
            .put { background-color: #fca130; }
            .delete { background-color: #f93e3e; }
            .patch { background-color: #50e3c2; }
            .summary {
                margin-bottom: 20px;
                padding: 10px;
                background-color: #e8e8e8;
                border-radius: 5px;
            }
        </style>
        """

        html_content = f"""
        <html>
        <head>
            <title>Swagger Test Report</title>
            <meta charset="UTF-8">
            {css_style}
        </head>
        <body>
            <div class="container">
                <h1>Swagger Test Report</h1>
                <div class="summary">
                    <h3>Summary</h3>
                    <p>Unauthorized Endpoints: {len(self.results['unauthorized'])}</p>
                    <p>Sensitive Parameters: {len(self.results['sensitive'])}</p>
                    <p>Failed Requests: {len(self.results['failed'])}</p>
                    <p>Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>
                <div class="section">
                    <h2>Unauthorized Endpoints</h2>
                    {''.join([self.format_endpoint_html(endpoint, 'unauthorized') for endpoint in self.results['unauthorized']])}
                </div>
                <div class="section">
                    <h2>Sensitive Parameters</h2>
                    {''.join([self.format_endpoint_html(endpoint, 'sensitive') for endpoint in self.results['sensitive']])}
                </div>
                <div class="section">
                    <h2>Failed Requests</h2>
                    {''.join([self.format_endpoint_html(endpoint, 'failed') for endpoint in self.results['failed']])}
                </div>
            </div>
        </body>
        </html>
        """

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"\n{Fore.GREEN}Report generated: {os.path.abspath(report_file)}{Style.RESET_ALL}")

    def format_endpoint_html(self, endpoint, endpoint_type):
        method = endpoint.get('method', '').lower()
        method_class = f"method {method}"

        if endpoint_type == 'unauthorized':
            return f"""
            <div class="endpoint unauthorized">
                <span class="{method_class}">{endpoint['method'].upper()}</span>
                <h3>{endpoint['url']}</h3>
                <h4>Request:</h4>
                <pre>{html.escape(self.format_json(endpoint['request']))}</pre>
                <h4>Response:</h4>
                <pre>{html.escape(self.format_json(endpoint['response']))}</pre>
                <p>Status Code: {endpoint['status_code']}</p>
            </div>
            """
        elif endpoint_type == 'sensitive':
            return f"""
            <div class="endpoint sensitive">
                <span class="{method_class}">{endpoint['method'].upper()}</span>
                <h3>{endpoint['url']}</h3>
                <p>Sensitive Parameters: {', '.join(endpoint['sensitive_params'])}</p>
            </div>
            """
        else:
            return f"""
            <div class="endpoint failed">
                <span class="{method_class}">{endpoint['method'].upper()}</span>
                <h3>{endpoint['url']}</h3>
                <p>Error: {endpoint.get('error', 'Unknown error')}</p>
            </div>
            """

    def parse_arguments(self):
        parser = argparse.ArgumentParser(
            description='''
Swagger API Authorization Tester
--------------------------------
This tool helps to test Swagger/OpenAPI endpoints for:
- Unauthorized access vulnerabilities
- Sensitive parameters
- API endpoint accessibility

Examples:
    Test local swagger file:
        python3 swagger_tester.py -c swagger.json -x http://192.168.1.1

    Test remote swagger endpoint:
        python3 swagger_tester.py -u http://site.com/v2/api-docs

    Test with proxy:
        python3 swagger_tester.py -u http://site.com/v2/api-docs -p http://127.0.0.1:8080
            ''',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-c', '--config', help='Local swagger file path')
        group.add_argument('-u', '--url', help='Remote swagger URL')
        parser.add_argument('-x', '--host', help='Base host for testing')
        parser.add_argument('-p', '--proxy', help='HTTP proxy (e.g., http://127.0.0.1:8080)')
        return parser.parse_args()

    def confirm_delete_operations(self):
        while True:
            response = input(f"{Fore.YELLOW}Do you want to test DELETE operations? This might delete server data! (yes/no): {Style.RESET_ALL}").lower()
            if response in ['yes', 'no']:
                return response == 'yes'
            print("Please answer 'yes' or 'no'")

    def print_banner(self):
        banner = """
╔═══════════════════════════════════════════╗
║        Swagger API Security Tester        ║
║                           by@qishi        ║
║    Test your API endpoints for security   ║
║    vulnerabilities and access control     ║
╚═══════════════════════════════════════════╝
        """
        print(f"{Fore.CYAN}{banner}{Style.RESET_ALL}")

    def run(self):
        self.print_banner()
        args = self.parse_arguments()

        # 确认是否测试DELETE操作
        test_delete = self.confirm_delete_operations()

        # 设置代理
        proxies = {'http': args.proxy, 'https': args.proxy} if args.proxy else None

        # 加载Swagger规范
        if args.url:
            swagger_spec = self.load_swagger_spec(args.url, is_url=True)
            base_url = args.host or urllib.parse.urlparse(args.url).scheme + '://' + urllib.parse.urlparse(args.url).netloc
        else:
            swagger_spec = self.load_swagger_spec(args.config)
            base_url = args.host

        if not base_url:
            print(f"{Fore.RED}Error: Base URL is required when using local file{Style.RESET_ALL}")
            sys.exit(1)

        # 处理不同版本的Swagger规范
        paths = swagger_spec.get('paths', {})

        print(f"\n{Fore.CYAN}Starting API test...{Style.RESET_ALL}")

        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.upper() == 'DELETE' and not test_delete:
                    print(f"{Fore.YELLOW}Skipping DELETE operation: {path}{Style.RESET_ALL}")
                    continue
                self.test_endpoint(base_url, path, method, operation, proxies)

        self.generate_report()

if __name__ == "__main__":
    tester = SwaggerTester()
    tester.run()
