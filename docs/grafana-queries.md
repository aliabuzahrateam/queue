# Grafana Queries for Queue Management System

This document provides sample queries for creating Grafana dashboards to monitor the Queue Management System.

## Prometheus Metrics

The system exposes the following metrics:

- `queue_users_released_total` - Counter of users released from queues
- `queue_users_expired_total` - Counter of expired users
- `callback_success_total` - Counter of successful callbacks
- `callback_failure_total` - Counter of failed callbacks
- `queue_size` - Gauge of current queue size per queue
- `callback_duration_seconds` - Histogram of callback durations

## Sample Queries

### 1. Queue Size Over Time

**Query:**
```
queue_size
```

**Description:** Shows current queue size for all queues over time.

### 2. Users Released Rate

**Query:**
```
rate(queue_users_released_total[5m])
```

**Description:** Rate of users being released from queues over 5-minute windows.

### 3. Callback Success Rate

**Query:**
```
rate(callback_success_total[5m]) / (rate(callback_success_total[5m]) + rate(callback_failure_total[5m])) * 100
```

**Description:** Percentage of successful callbacks over 5-minute windows.

### 4. Average Callback Duration

**Query:**
```
histogram_quantile(0.95, rate(callback_duration_seconds_bucket[5m]))
```

**Description:** 95th percentile of callback duration over 5-minute windows.

### 5. Total Users by Status

**Query:**
```
# For waiting users
sum(queue_size) by (queue_id)

# For expired users
increase(queue_users_expired_total[1h])

# For rejected users (if tracked)
increase(queue_users_rejected_total[1h])
```

### 6. Queue Performance by Application

**Query:**
```
# Users released per queue
increase(queue_users_released_total[1h]) by (queue_id)

# Callback failures per queue
increase(callback_failure_total[1h]) by (queue_id)
```

### 7. System Health Dashboard

**Queries:**

1. **Active Queues:**
   ```
   count(queue_size > 0)
   ```

2. **Total Users in System:**
   ```
   sum(queue_size)
   ```

3. **Callback Error Rate:**
   ```
   rate(callback_failure_total[5m]) / rate(callback_success_total[5m] + callback_failure_total[5m]) * 100
   ```

4. **Average Wait Time (if available):**
   ```
   # This would require custom metrics
   avg_over_time(wait_time_seconds[5m])
   ```

## Dashboard Panels

### 1. Overview Panel
- **Title:** Queue System Overview
- **Type:** Stat
- **Query:** `sum(queue_size)`
- **Description:** Total users currently in queues

### 2. Queue Size Panel
- **Title:** Queue Sizes
- **Type:** Time Series
- **Query:** `queue_size`
- **Description:** Queue sizes over time

### 3. Release Rate Panel
- **Title:** User Release Rate
- **Type:** Time Series
- **Query:** `rate(queue_users_released_total[5m])`
- **Description:** Rate of users being released

### 4. Callback Success Panel
- **Title:** Callback Success Rate
- **Type:** Gauge
- **Query:** `rate(callback_success_total[5m]) / (rate(callback_success_total[5m]) + rate(callback_failure_total[5m])) * 100`
- **Description:** Percentage of successful callbacks

### 5. Error Rate Panel
- **Title:** Callback Error Rate
- **Type:** Time Series
- **Query:** `rate(callback_failure_total[5m])`
- **Description:** Rate of callback failures

## Alerting Rules

### 1. High Queue Size Alert
```yaml
groups:
  - name: queue_alerts
    rules:
      - alert: HighQueueSize
        expr: queue_size > 100
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Queue size is high"
          description: "Queue {{ $labels.queue_id }} has {{ $value }} users waiting"
```

### 2. Callback Failure Alert
```yaml
      - alert: HighCallbackFailureRate
        expr: rate(callback_failure_total[5m]) / rate(callback_success_total[5m] + callback_failure_total[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High callback failure rate"
          description: "Callback failure rate is {{ $value | humanizePercentage }}"
```

### 3. No Users Released Alert
```yaml
      - alert: NoUsersReleased
        expr: rate(queue_users_released_total[10m]) == 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "No users released from queues"
          description: "No users have been released in the last 10 minutes"
```

## Custom Metrics (Optional)

You can add custom metrics for more detailed monitoring:

### 1. Wait Time Metrics
```python
# In your worker
WAIT_TIME = Histogram('queue_wait_time_seconds', 'Time users wait in queue', ['queue_id'])
```

### 2. Queue Position Metrics
```python
# In your API
QUEUE_POSITION = Gauge('queue_position', 'User position in queue', ['queue_id', 'visitor_id'])
```

### 3. Application-specific Metrics
```python
# In your application
APP_QUEUE_SIZE = Gauge('app_queue_size', 'Queue size per application', ['app_id', 'queue_name'])
```

## Dashboard Variables

Create these variables for dynamic dashboards:

1. **Queue ID Variable:**
   - Name: `queue_id`
   - Type: Query
   - Query: `label_values(queue_size, queue_id)`

2. **Application Variable:**
   - Name: `app_id`
   - Type: Query
   - Query: `label_values(queue_size, app_id)`

3. **Time Range Variable:**
   - Name: `time_range`
   - Type: Custom
   - Values: `1h, 6h, 24h, 7d`

## Import Dashboard

You can import a complete dashboard JSON file that includes all these panels and queries. The dashboard will provide:

- Real-time queue monitoring
- Performance metrics
- Error tracking
- Alert notifications
- Historical data analysis

This monitoring setup will help you maintain optimal queue performance and quickly identify and resolve issues. 