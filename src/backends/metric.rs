use std::vec::IntoIter;

#[derive(Debug, Clone)]
pub struct Metric {
    pub job_id: i32,
    pub hostname: String,
    pub timestamp: i32,
    pub backend_name: String,
    pub metric_names: IntoIter<String>,
    pub metric_values: Option<IntoIter<String>>,
}