from prometheus_client import Counter, Histogram, Gauge

# Метрики для браузера
BROWSER_OPERATIONS = Counter(
    'browser_operations_total',
    'Total number of browser operations',
    ['operation', 'status']
)

BROWSER_OPERATION_DURATION = Histogram(
    'browser_operation_duration_seconds',
    'Time spent on browser operations',
    ['operation']
)

# Метрики для проверки слотов
SLOT_CHECK_DURATION = Histogram(
    'slot_check_duration_seconds',
    'Time spent checking slots'
)

SLOTS_FOUND = Counter(
    'slots_found_total',
    'Number of times slots were found',
    ['location']
)

ACTIVE_CHECKS = Gauge(
    'active_slot_checks',
    'Number of active slot checking processes'
)

# Метрики для уведомлений
NOTIFICATION_COUNTER = Counter(
    'notifications_sent_total',
    'Total notifications sent',
    ['type', 'status']
)

NOTIFICATION_ERRORS = Counter(
    'notification_errors_total',
    'Total notification errors',
    ['error_type']
) 