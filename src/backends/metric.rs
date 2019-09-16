
#[derive(Debug, Clone)]
pub struct Metric {
    pub job_id: i32,
    pub hostname: String,
    pub timestamp: i32,
    pub backend_name: String,
    pub metric_names: Vec<String>,
    pub metric_values: Option<Vec<i64>>,
}