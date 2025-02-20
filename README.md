# Swagger API Security Tester

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Swagger API Security Tester** 是一款用于自动化测试 Swagger/OpenAPI 规范定义的 API 端点的安全工具。它可以帮助开发者和安全测试人员快速检测 API 是否存在潜在的未授权访问和敏感参数泄露等安全问题。

## 功能特性

* **支持多种 Swagger 规范版本**:  工具设计具有强大的兼容性，能够解析各种版本的 Swagger/OpenAPI 接口文档。
* **本地文件解析**: 支持解析本地 Swagger JSON 文件，方便在本地开发和测试环境中使用。使用本地文件时，需要手动指定域名进行接口拼接测试。
    ```bash
    python3 swagger-api-scan.py -c swagger.json -x http://192.168.1.1
```
* **远程 URL 解析**: 支持直接解析远程 Swagger JSON 文件 URL，包括常见的 Swagger 接口文档路径格式。
    ```bash
    python3 swagger-api-scan.py -u http://XXX.com/v2/api-docs
    python3 swagger-api-scan.py -u http://XXXX:18080/swagger/v1/swagger.json
    python3 swagger-api-scan.py -u http://XXX.com/swagger-resources/
    ```
    如果未指定域名 (`-x` 参数)，工具默认使用 `-u` 参数提供的 URL 中的域名进行接口拼接。
* **智能参数填充**:  遍历 Swagger 文档中的所有 API 接口，并尝试自动填充参数值。工具能够根据参数名称进行智能判断，例如：
  
    * `id` 类参数填充数字 (例如: `123`)
    * `path` 类参数填充通用路径 (例如: `/example/path`)
    * `name` 类参数填充姓名 (例如: `test_name`)
    * 其他常见参数类型也会根据预设的规则进行填充，以提高测试的有效性。
* **敏感参数检测**:  自动分析 API 接口的参数，检测是否存在潜在的敏感参数，例如 `url`, `path`, `redirect`, `token`, `password` 等。这有助于发现可能引入 SSRF 等漏洞的接口。
* **HTTP 代理支持**:  支持通过 `-p` 参数配置 HTTP 代理，方便在需要通过代理访问 API 的场景下使用。
    ```bash
    python3 swagger-api-scan.py -u http://xxxx.com/v2/api-docs -p http://127.0.0.1:8080
    ```
* **请求头自定义**:  允许通过 `-header` 参数添加自定义 HTTP 请求头，例如添加 Cookie 或 Authorization 信息。
    ```bash
    python3 swagger-api-scan.py -u http://xxxx.com/v2/api-docs -header "Cookie: your_cookie_value"
    ```
* **DELETE 请求确认**:  在执行扫描前，工具会提示用户确认是否要扫描 `DELETE` 请求，以防止误操作导致服务器数据被删除。
* **并发控制**:  支持通过 `-t` 参数控制并发请求数量 ( *注意：代码中未找到 `-t` 参数的实现，如果需要并发控制，请根据需求自行添加* )。
* **详细的 HTML 报告**:  测试完成后，工具会自动生成 HTML 格式的报告，详细记录每个接口的请求和响应内容。报告以美观的方式展示，方便用户查看和分析测试结果。报告内容包括：
  
    * 请求包和响应包的详细信息 (长文本自动换行)
    * 漏洞详细信息 (例如未授权访问、敏感参数)
    * 使用图标增强报告的可读性
* **控制台彩色输出**:  在控制台输出测试进度和结果，使用颜色标记不同类型的接口：
    * **红色**: 疑似未授权访问的接口
    * **绿色**: 存在敏感参数的接口
    * 其他信息以普通颜色输出
* **结果分类输出**:  扫描完成后，测试结果会分类输出到 HTML 报告中，方便用户快速定位不同类型的安全问题。

## 使用方法

### 1. 环境准备

确保你的系统已安装 Python 3.6 或更高版本，并安装以下依赖库：

```bash
pip install -r 
```

### 2. 运行工具

根据你的 Swagger 文档来源选择相应的命令运行工具。

**解析本地 Swagger 文件:**

```bash
python3 swagger-api-scan.py -c <本地swagger文件路径> -x <API域名>
```

例如:

```bash
python3 swagger-api-scan.py -c swagger.json -x http://192.168.1.1
```

**解析远程 Swagger URL:**

```bash
python3 swagger-api-scan.py -u <远程swagger文档URL>
```

例如:

```bash
python3 swagger-api-scan.py -u http://xxxx.com/v2/api-docs
```

**使用 HTTP 代理:**

```bash
python3 swagger-api-scan.py -u <远程swagger文档URL> -p <代理地址>
```

例如:

```bash
python3 swagger-api-scan.py -u http://xxxx.com/v2/api-docs -p http://127.0.0.1:8080
```

**添加自定义请求头:**

```bash
python3 swagger-api-scan.py -u <远程swagger文档URL> -header "<Header名称>:<Header值>"
```

例如，添加 Cookie:

```bash
python3 swagger-api-scan.py -u http://xxxx.com/v2/api-docs -header "Cookie: your_cookie_value"
```

### 3. 参数说明

| 参数       | 简写      | 描述                                | 是否必须          | 示例                          |
| ---------- | --------- | ----------------------------------- | ----------------- | ----------------------------- |
| `--config` | `-c`      | 本地 Swagger 文件路径               | 是 (与 `-u` 互斥) | `swagger.json`                |
| `--url`    | `-u`      | 远程 Swagger 文档 URL               | 是 (与 `-c` 互斥) | `http://site.com/v2/api-docs` |
| `--host`   | `-x`      | API 域名 (当使用本地文件时必须指定) | 当使用 `-c` 时是  | `http://192.168.1.1`          |
| `--proxy`  | `-p`      | HTTP 代理地址                       | 否                | `http://127.0.0.1:8080`       |
| `--header` | `-header` | 自定义 HTTP 请求头                  | 否                | `"Cookie: your_cookie_value"` |
| `--help`   | `-h`      | 显示帮助信息                        | 否                |                               |

### 4. 查看报告

测试完成后，会在当前目录下生成一个 HTML 报告文件，文件名格式为 `swagger_test_report_YYYYMMDD_HHMMSS.html`。使用浏览器打开该文件即可查看详细的测试报告。



### 5.截图示例

![image](https://github.com/user-attachments/assets/7fd95421-a842-4bdb-8344-9d87433a6217)
![image](https://github.com/user-attachments/assets/f4376548-fc7e-4bda-afa3-f18fd81f6940)


 ## 注意事项

* **DELETE 请求风险**:  工具在默认情况下会询问是否测试 `DELETE` 请求。请谨慎操作，避免误删服务器数据。
* **测试环境**:  建议在测试环境或预发布环境中使用本工具进行安全测试，避免对生产环境造成不必要的影响。
* **参数填充**:  智能参数填充功能旨在提高测试效率，但并不能保证完全覆盖所有场景。对于关键业务 API，建议结合人工测试进行更全面的安全评估。
* **并发控制**:  代码中未实现 `-t` 并发控制参数。如果需要进行并发测试，请自行修改代码添加相关功能。

## 作者

[@qishi](https://github.com/qishi717)  
