#Prometheus
#Mục lục
**Table of Contents**  *generated with [DocToc](http://doctoc.herokuapp.com/)*

- [1. Giới thiệu Prometheus](#gioithieu)
- [2. Kiến trúc](#kientruc)
- [3. Data model](#datamodel)
	- [3.1 Metrics](#metrics)
  - [3.2 Storage](#storage)
- [4. Scrape metrics](#scrape)
	- [4.1 Exporter](#exporter)
	- [4.2 Pushgateway](#pushgateway)
	- [4.3 Prometheus-server](#promethes-sv)
	- [4.4 Client libraries](#client)
- [5. Query Language và Visualization](#query-visualization)
	- [5.1 Query Language (PromQL)](#query)
	- [5.2 Visualization](#visualization)
- [6. Alert](#alert)
	- [6.1 Alert manager](#alertmanager)
	- [6.2 Alert rules](#alertrules)
- [7. Demo](#demo)
- [8. Tài liệu tham khảo](#thamkhao)

<a name="gioithieu"></a>
#1. Giới thiệu Prometheus
- Là giải pháp monitor open source.

![](http://image.prntscr.com/image/2f13b87ab33b468ab275b69467b91f7d.png)
- Được bắt đầu từ năm 2012, tại SoundCloud.
- Tháng 1/2015, Prometheus được public.
- Tháng 5/2016, Prometheus gia nhập CNCF. Cloud Native Computing Foundation (CNCF) là một tổ chức phi lợi nhuận mà cam kết sẽ thúc đẩy sự phát triển của công nghệ đám mây, hình thành dưới Linux Foundation.
CNCF còn có: Fluentd, Kubernetes, Linkerd, OpenTracing.
- Tháng 7/2016, Ra mắt phiên bản 1.0. Phiên bản mới nhật hiện tại là 1.5.2 / 2017-02-10.
- Tháng 8/2016, tổ chức sự kiện Prometheus conference, với mục tiêu là kết nối các users và developer trên toàn thế giới, trao đổi kiến thức, kinh nghiệm có được trong quá trình sử dụng promethes.

- Một vài thông số:
  - Hơn 350 người phát triển.
  - Hơn 50 phần mềm thứ 3 tích hợp.

- Một vài user nổi tiếng như:
  - SoundCloud
  - DigitalOcean
  - Ericsson
  - Docker
  - Weaveworks
  - Read hat
  - Core OS
  - Google

<a name="kientruc"></a>
#2. Kiến trúc

![](https://prometheus.io/assets/architecture.svg
)

- Prometheus server có nhiệm vụ: *scrapes* metrics và lưu trữ dữ liệu.
- Client libraries: Prometheus cung cấp các thư viện để áp dụng vào ứng dụng.
- Push gateway phù hợp với các công việc short-lived. Các short-lived là những công việc không tồn tại lâu để mà prometheus có thể **scraped** metrics. Vì vậy, các job này sẽ đẩy **push** các metrics này đến Pushgateway. Sau đó Prometheus sẽ **scrapes** Pushgateway để có được metrics.
- Giao diện web GUI.
- Các exporters có nhiệm vụ thu thập metrics.
- Hệ thống cảnh báo alertmanager.
- Giao diện dòng lệnh command-line querying.


Cách hoạt động:
- Các jobs được phân chia thành short-lived và long-lived jobs/Exporter.

Short-lived là những job sẽ tồn tại trong thời gian ngắn và prometheus-server sẽ không kịp scrapes metrics của các jobs này. Do đó, những short-lived jobs sẽ push (đẩy) các metrics đến một nơi gọi là Pushgateway. Pushgateway sẽ là nơi sẽ phơi bày metrics ra và prometheus-server sẽ lấy được metrics của short-lived thông qua Pushgateway.

Long-lived jobs/Exporter: Là những job sẽ tồn tại lâu dài. Các Exporter sẽ được chạy như dưới dạng 1 service. Exporter sẽ có nhiệm vụ thu thập metrics và phơi bày metrics đấy ra. Prometheus-server sẽ scrapes được metrics thông qua hành động pull (kéo).

- Prometheus-server **scrapes** metrics từ các jobs. Sau đó, nó sẽ lưu trữ các metrics này vào Database. (Lưu trữ trong thư mục data). Prometheus sử dụng kiểu time-series database (arrays of numbers indexed by time). Dựa vào các rules mà ta quy định, (ví dụ như khi cpu xử lý hơn 80%) thì prometheus-server sẽ push (đẩy) cảnh báo đến thành phần Alertmanager.

- PromDash, Grafana,.. dùng câu lệnh querying (PromQL - Prometheus Query Language) để lấy được thông tin metrics lưu trữ ở Prometheus-server và trình diễn.

- Alertmanager sẽ được cấu hình các thông tin cần thiết để có thể gửi cảnh bảo đến email, slack,.... Sau khi prometheus-server push alerts đến alertmanager, alertmanager sẽ gửi cảnh báo đến người dùng.

<a name="datamodel"></a>
#3. Data model
<a name="metrics"></a>
##3.1 Metrics
- Prometheus lưu trữ metrics dưới dạng time series (TSDB), và các cặp **key->values**.

|Metrics|Timestamp|Values|
|:-:|:-:|:-:|
|api_http_requests_total{method="GET", endpoint="/api/posts", status="200"}|@1464623917237|68856|

- Giải thích:
  - `api_http_requests_total`: là tên metrics.
  - `method="GET", endpoint="/api/posts", status="200"`: label - là các cặp key->values.
  - `@1464623917237`: Giá trị timestamp, chính là giá trị unix timestamp.
  - `68856`: Giá trị của metrics tại thời điểm timestamp.

- Có 4 loại metrics
  - Counter: Có giá trị là số, giá trị chỉ có thể được tăng lên chứ không thể giảm đi. Được sử dụng trong các trường hợp như đếm số request, task complete, errors occurred,..
  - Gauge: Tương tự như Counter. Tuy nhiên giá trị có thể lên hoặc xuống. Thường được sử dụng để đo các giá trị như giá trị nhiệt độ, hoặc giá trị bộ nhớ hiện tại đang sử dụng.
  - Histogram: Là metrics mà sẽ cung cấp nhiều time-series: 1 cho mỗi bucket, 1 cho tổng các giá trị và 1 cho đếm các events đã thấy. Ví dụ như thời gian response.
  - Summary: Cũng tương tự Histogram. Tuy nhiên nó có hỗ trợ thêm khả năng tính toán quantiles.

<a name="storage"></a>
##3.2 Storage
- Prometheus sử dụng storage backend dưới dạng custom.
- Để indexed, Prometheus sử dụng LevelDB.
- For the bulk sample data, it has its own custom storage layer.
- Write Performance - Single Node: 800k metrics/s.
- Lưu trữ tại thư mục /data.
- Ngôn ngữ truy vấn: PromQL.


<a name="scrape"></a>
#4. Scrape metrics
<a name="exporters"></a>
##4.1 Exporter
- Các phần mềm thứ 3 mà không hỗ trợ `Prometheus metrics natively` thì có thể được monitor bằng exporters.
- Exporter có thể thu thập số liệu thống kê và số liệu hiện có, và chuyển đổi chúng sang các số liệu Prometheus.
- Exporter giống như một dịch vụ instrumented, phơi bày những số liệu thông qua một thiết bị đầu cuối, và có thể được `scaped` bởi Prometheus
- Một số Exporter do Prometheus hỗ trợ như:
  - MySQL
  - Haproxy

<a name="pushgateway"></a>
##4.2 Pushgateway
- Pushgateway được sử dụng trong trường hợp mà Promethes server không thể scrape metrics một cách trực tiếp. Có thể là các job chỉ tồn tại trontg thời gian ngắn mà Promethes server chưa kịp scrape metrics.

- Để giải quyết vấn đề này, thì Pushgateway được ra đời. Pushgateway sẽ đóng vai trò trung gian giữa promethes server và targets
cần monitor.

- Trên targets sẽ được cấu hình để push metrics đến Pushgateway. Rồi từ đó, Prometheus server sẽ scrape (pull) metrics ở Pushgateway.

- All pushes are done via HTTP. The interface is vaguely REST-like.

- Để push metrics lên pushgateway, các bạn có thể sử dụng lệnh curl với các method sau:
  - URL: `http://ip:9091/metrics/job/<JOBNAME>{/<LABEL_NAME>/<LABEL_VALUE>}`
  - PUT method: Push metrics. All metrics with the grouping key specified in the URL are replaced by the metrics pushed with PUT.
  - POST method: POST works exactly like the PUT method but only metrics with the same name as the newly pushed metrics are replaced (among those with the same grouping key).
  - DELETE method: DELETE is used to delete metrics from the push gateway.

<a name="promethes-sv"></a>
##4.3 Prometheus-server
- Federation là tính năng cho phép một Prometheus-server **scrape** metrics từ các Prometheus-server khác.
- Cấu hình trên prometheus server scrape metrics từ các server khác.

```sh
- job_name: 'federate'
  scrape_interval: 15s

  honor_labels: true
  metrics_path: '/federate'

  params:
    'match[]':
      - '{job="prometheus"}'
      - '{__name__=~"job:.*"}'

  static_configs:
    - targets:
      - 'source-prometheus-1:9090'
      - 'source-prometheus-2:9090'
      - 'source-prometheus-3:9090'
```

Lưu ý là phần `{job="prometheus"}` thì tên job phải trùng với job trong các job đã cấu hình ở trên các promethes server khác.

- Sau khi cấu hình xong, các bạn có thể vào địa chỉ: `http://ip:9090/targets` để kiểm tra

<a name="client"></a>
##4.4 Client libraries
- Hiện tại Prometheus hỗ trợ nhiều ngôn ngữ khác nhau để các bạn có thể tích hợp ngay vào mã nguồn của mình, để từ đó xuất ra được metrics, và có thể monitor ngay ứng dụng của mình.
- Các ngôn ngữ hỗ trợ như: Go, Java, Python, Ruby,...

<a name="query-visualization"></a>
#5. Query Language và Visualization
<a name="query"></a>
##5.1 Query Language (PromQL)
- Là câu lệnh truy vấn cho phép ta lấy được thông tin của metrics, cho phép người dùng lựa chọn và tổng hợp dữ liệu chuỗi thời gian thèo thời gian thực.
- Lấy values của metrics: tênmetrics
```sh
http_requests_total
```
```sh
Element	| Value
http_requests_total{alias="hanoi-slave",code="200",handler="prometheus",instance="mysql",job="mysql",method="get"}	1
http_requests_total{alias="prometheus",code="200",handler="graph",instance="prometheus",job="prometheus",method="get"}	1
http_requests_total{alias="prometheus",code="200",handler="prometheus",instance="prometheus",job="prometheus",method="get"}	1
http_requests_total{alias="prometheus",code="200",handler="static",instance="prometheus",job="prometheus",method="get"}	1
http_requests_total{alias="prometheus",code="200",handler="label_values",instance="prometheus",job="prometheus",method="get"}	1
```
- Lọc filter với các label `{lablel="value"}`:
```sh
http_requests_total{code="200", job="mysql"}
```
```sh
Element |	Value
http_requests_total{alias="hanoi-slave",code="200",handler="prometheus",instance="mysql",job="mysql",method="get"}	21
```
- Lấy tất cả giá trị trong khoảng thời gian đến hiện tại `[time]`:
```sh
http_requests_total{job="mysql"}[5m]
```
```sh
Element	Value
http_requests_total{alias="hanoi-slave",code="200",handler="prometheus",instance="mysql",job="mysql",method="get"}	22 @1487121093.351
23 @1487121098.351
24 @1487121103.353
25 @1487121108.353
26 @1487121113.351
27 @1487121118.351
28 @1487121123.351
29 @1487121128.353
30 @1487121133.352
31 @1487121138.352
32 @1487121143.351
33 @1487121148.351
```
- Lấy giá trị vào thời điểm 5 phút trước:
```sh
http_requests_total{job="mysql"} offset 1m
```
```sh
http_requests_total{alias="hanoi-slave",code="200",handler="prometheus",instance="mysql",job="mysql",method="get"}	31
```

- PromQL có hỗ trợ các phép toán `+ - * / mod  % ^`
- Các phép so sánh: `= != > < >= <=`
- Các mệnh đề:
	- **and**: vector1 and vector2: Kết quả là tập chung có cả trong vector1 và vector2
	- **or**: vector1 or vector2: Kết quả là có trong vector1 hoặc vector2.
	- **unless**: vector1 unless vector2: Kết quả là có trong vector1 mà không có trong vector2.

- Hỗ trợ nhiều hàm:
	- **abs**: `abs(v instant-vector)`: Giá trị tuyệt đối.
	- **day_of_month**, **day_of_week**: Trả về giá trị ngày.
	- **rate** `rate(v range-vector)`: Trả về giá trị trung bình trong khoảng thời gian (range-vector).

<a name="visualization"></a>
##5.2 Visualization
- PromDash: Sản phẩm do chính Prometheus phát triển.
- Grafana: Đang được sử dụng nhiều hiện nay.
- Đặc điểm chung của 2 phần mềm trên là đều sử dụng PromQL, truy vấn vào Prometheus-server để lấy được thông tin metrics. Từ đó biểu diễn lên các biểu đồ.

<a name="alert"></a>
#6. Alert
<a name="alertmanager"></a>
##6.1 Alert manager
- Alertmanager có nhiệm vụ là gửi các cảnh báo đến nơi đã cấu hình.

![](http://image.prntscr.com/image/423fd44813fe49bab90857552a8d8673.png)

- Cách hoạt động như sau:
  - 1. Prometheus-server sẽ xử lý các alert-rules.
  - 2. Nếu rules được match, Prometheus-server sẽ gửi thông tin đến Alertmanager.
  - 3. Alertmanager sẽ bắn cảnh báo đến nơi đã cấu hình.
- Một số tính năng hay ho khi gửi cảnh bảo:
  - **Grouping:** Phân loại các cảnh báo theo group. Ví dụ ta cấu hình 100 server khi bị failed thì sẽ gửi cảnh báo đến sysadmin. Khi đó, sysadmin sẽ lập tức nhận 100 notification một lúc. Thay vì vậy, ta gom nhóm 100 server này vào 1 group, và sysadmin sẽ chỉ nhận được 1 notification mà thôi.
  - **Inhibiton:** Sẽ bỏ đi các cảnh báo nhất định nếu một số cảnh báo khác đã được bắn. Ví dự như ta có cụm 1 cụm cluster 100 server bị mất kết nối internet đột ngột. Trên các server này ta có đặt các báo về network, web-server, mysql,... Đo đó, khi mà mất kết nối internet thì tất các cách dịch vụ này đều gửi cảnh báo đến sysadmin. Sử dụng Inhibiton thì khi cảnh báo network được gửi đến sysadmin và các cảnh báo về web-server, mysql sẽ không gửi cần phải gửi đến sysadmin nữa vì sysadmin thừa hiểu là khi mất internet thì các service kia cũng bị failed.
  - **Silences:** Tắt cảnh báo trong một thời gian nhất định.
- Alertmanager được cấu hình với các thông tin như:
  - Routes: Định tuyến đường đi của notification. Có các route con với các match của nó. Nếu notification trùng với match của route nào đó, thì sẽ được gửi đi theo đường đó. Còn không match với route nào, nó sẽ được gửi theo đường đi mặc định.
  - Receivers: Cấu hình thông tin các nơi nhận. Ví dụ như tên đăng nhập, mật khẩu, tên mail sẽ gửi đến,....
- Ví dụ:

```sh
# The root route on which each incoming alert enters.
route:
  # The default receiver
  receiver: 'team-X'
  # The child route trees.
  routes:
  # This is a regular expressiong based route
  - match_re:
      service: ^(foo|bar)$
    receiver: team-foobar
    # Another child route
    routes:
    - match:
        severity: critical
      receiver: team-critical
receivers:
# Email receiver
- name: 'team-X'
  email_configs:
  - to: 'alerts@team-x.com'

# Slack receiver that sends alerts to the #general channel.
- name: 'team-foobar'
  slack_configs:
    api_url: 'https://foobar.slack.com/services/hooks/incoming-webhook?token=<token>'
    channel: 'general'

# Webhook receiver with a custom endpoint
- name: 'team-critical'
  webhook_configs:
    url: 'team.critical.com'
```

<a name="alertrules"></a>
##6.2 Alert rules
- Được cấu hình trên Prometheus-server
- Đặt ra các quy định, khi nào rules match thì sẽ gửi đến Alertmanager.
- Cấu hình:

```sh
ALERT <alert name>
  IF <expression>
  [ FOR <duration> ]
  [ LABELS <label set> ]
  [ ANNOTATIONS <label set> ]
```
- Trong đó:
  - alert name: là tên thông báo.
  - expression: điều kiện.
  - duration: khoảng thời gian.
Nếu điều kiện được match trong khoảng thời gian nào đó thì sẽ gửi cảnh bảo với nhãn và chú thích ở trên.

- Ví dụ:

```sh
# Alert for any instance that have a median request latency >1s.
ALERT APIHighRequestLatency
IF api_http_request_latencies_second{quantile="0.5"} > 1
FOR 1m
LABELS { severity="critical"}
ANNOTATIONS {
  summary = "High request latency on ",
  description = " has a median request latency above 1s (current value: s)",
}

ALERT CpuUsage
IF cpu_usage_total > 95
FOR 1m
LABELS { severity="critical"}
ANNOTATIONS {
  summary = "YOU MUST CONSTRUCT ADDITIONAL PYLONS"
  description = "CPU usage is above 95%"
}
```

<a name="demo"></a>
#7. Demo
- Monitoring mysql replication.
- link: https://github.com/linhlt247/networking-team/tree/master/LinhLT/Prometheus%2Bgrafana/demo

<a name="thamkhao"></a>
#8. Tham khảo
- https://promcon.io/2016-berlin/talks/welcome-and-introduction/
- http://www.slideshare.net/brianbrazil/an-introduction-to-prometheus-grafanacon-2016
- https://prometheus.io/docs/
- https://blog.dataloop.io/top10-open-source-time-series-databases
- https://docs.google.com/spreadsheets/d/1sMQe9oOKhMhIVw9WmuCEWdPtAoccJ4a-IuZv4fXDHxM/pubhtml#
