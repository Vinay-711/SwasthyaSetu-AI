-- Delta Lake: Notifications table schema

CREATE TABLE IF NOT EXISTS swasthya.notifications (
    notification_id STRING     NOT NULL,
    patient_id      STRING     NOT NULL,
    message         STRING,
    channel         STRING     COMMENT 'sms | push | email',
    status          STRING     COMMENT 'sent | failed | pending',
    sent_at         TIMESTAMP  DEFAULT current_timestamp()
)
USING DELTA
COMMENT 'Notification history for SwasthyaSetu AI'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact'   = 'true'
);
