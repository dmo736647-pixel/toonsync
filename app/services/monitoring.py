"""监控和告警服务"""
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from enum import Enum


class MetricType(Enum):
    """指标类型"""
    COUNTER = "counter"  # 计数器
    GAUGE = "gauge"      # 仪表
    HISTOGRAM = "histogram"  # 直方图


class AlertLevel(Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Metric:
    """指标"""
    
    def __init__(self, name: str, metric_type: MetricType, description: str = ""):
        self.name = name
        self.metric_type = metric_type
        self.description = description
        self.value = 0.0
        self.labels: Dict[str, str] = {}
        self.samples: List[float] = []
        self.last_updated = time.time()
    
    def inc(self, amount: float = 1.0, labels: Optional[Dict[str, str]] = None):
        """增加计数器"""
        if self.metric_type == MetricType.COUNTER:
            self.value += amount
            self.last_updated = time.time()
            if labels:
                self.labels.update(labels)
    
    def set(self, value: float, labels: Optional[Dict[str, str]] = None):
        """设置仪表值"""
        if self.metric_type == MetricType.GAUGE:
            self.value = value
            self.last_updated = time.time()
            if labels:
                self.labels.update(labels)
    
    def observe(self, value: float, labels: Optional[Dict[str, str]] = None):
        """观察直方图值"""
        if self.metric_type == MetricType.HISTOGRAM:
            self.samples.append(value)
            # 只保留最近1000个样本
            if len(self.samples) > 1000:
                self.samples = self.samples[-1000:]
            self.last_updated = time.time()
            if labels:
                self.labels.update(labels)
    
    def get_value(self) -> float:
        """获取当前值"""
        if self.metric_type == MetricType.HISTOGRAM:
            return sum(self.samples) / len(self.samples) if self.samples else 0.0
        return self.value
    
    def get_percentile(self, percentile: float) -> float:
        """获取百分位数（仅用于直方图）"""
        if self.metric_type != MetricType.HISTOGRAM or not self.samples:
            return 0.0
        
        sorted_samples = sorted(self.samples)
        index = int(len(sorted_samples) * percentile / 100)
        return sorted_samples[min(index, len(sorted_samples) - 1)]


class Alert:
    """告警"""
    
    def __init__(
        self,
        name: str,
        level: AlertLevel,
        message: str,
        metric_name: str,
        threshold: float,
        comparison: str = ">"
    ):
        self.name = name
        self.level = level
        self.message = message
        self.metric_name = metric_name
        self.threshold = threshold
        self.comparison = comparison
        self.triggered = False
        self.triggered_at: Optional[datetime] = None
        self.trigger_count = 0
    
    def check(self, metric_value: float) -> bool:
        """检查是否触发告警"""
        triggered = False
        
        if self.comparison == ">":
            triggered = metric_value > self.threshold
        elif self.comparison == "<":
            triggered = metric_value < self.threshold
        elif self.comparison == ">=":
            triggered = metric_value >= self.threshold
        elif self.comparison == "<=":
            triggered = metric_value <= self.threshold
        elif self.comparison == "==":
            triggered = metric_value == self.threshold
        
        if triggered and not self.triggered:
            self.triggered = True
            self.triggered_at = datetime.utcnow()
            self.trigger_count += 1
        elif not triggered and self.triggered:
            self.triggered = False
        
        return triggered
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "name": self.name,
            "level": self.level.value,
            "message": self.message,
            "metric_name": self.metric_name,
            "threshold": self.threshold,
            "triggered": self.triggered,
            "triggered_at": self.triggered_at.isoformat() if self.triggered_at else None,
            "trigger_count": self.trigger_count
        }


class MonitoringService:
    """监控服务"""
    
    def __init__(self):
        self.metrics: Dict[str, Metric] = {}
        self.alerts: Dict[str, Alert] = {}
        self.alert_history: List[Dict] = []
    
    def register_metric(
        self,
        name: str,
        metric_type: MetricType,
        description: str = ""
    ) -> Metric:
        """注册指标"""
        if name not in self.metrics:
            self.metrics[name] = Metric(name, metric_type, description)
        return self.metrics[name]
    
    def get_metric(self, name: str) -> Optional[Metric]:
        """获取指标"""
        return self.metrics.get(name)
    
    def register_alert(
        self,
        name: str,
        level: AlertLevel,
        message: str,
        metric_name: str,
        threshold: float,
        comparison: str = ">"
    ) -> Alert:
        """注册告警规则"""
        alert = Alert(name, level, message, metric_name, threshold, comparison)
        self.alerts[name] = alert
        return alert
    
    def check_alerts(self) -> List[Dict]:
        """检查所有告警"""
        triggered_alerts = []
        
        for alert_name, alert in self.alerts.items():
            metric = self.get_metric(alert.metric_name)
            if metric:
                metric_value = metric.get_value()
                if alert.check(metric_value):
                    alert_dict = alert.to_dict()
                    alert_dict["metric_value"] = metric_value
                    triggered_alerts.append(alert_dict)
                    
                    # 记录到历史
                    self.alert_history.append({
                        **alert_dict,
                        "timestamp": datetime.utcnow().isoformat()
                    })
        
        # 只保留最近100条告警历史
        if len(self.alert_history) > 100:
            self.alert_history = self.alert_history[-100:]
        
        return triggered_alerts
    
    def get_all_metrics(self) -> Dict[str, Dict]:
        """获取所有指标"""
        result = {}
        for name, metric in self.metrics.items():
            result[name] = {
                "name": name,
                "type": metric.metric_type.value,
                "description": metric.description,
                "value": metric.get_value(),
                "labels": metric.labels,
                "last_updated": metric.last_updated
            }
            
            # 如果是直方图，添加百分位数
            if metric.metric_type == MetricType.HISTOGRAM:
                result[name]["p50"] = metric.get_percentile(50)
                result[name]["p95"] = metric.get_percentile(95)
                result[name]["p99"] = metric.get_percentile(99)
        
        return result
    
    def get_alert_history(self, limit: int = 50) -> List[Dict]:
        """获取告警历史"""
        return self.alert_history[-limit:]
    
    def export_prometheus_format(self) -> str:
        """导出Prometheus格式的指标"""
        lines = []
        
        for name, metric in self.metrics.items():
            # 添加HELP和TYPE注释
            lines.append(f"# HELP {name} {metric.description}")
            lines.append(f"# TYPE {name} {metric.metric_type.value}")
            
            # 添加指标值
            labels_str = ""
            if metric.labels:
                labels_list = [f'{k}="{v}"' for k, v in metric.labels.items()]
                labels_str = "{" + ",".join(labels_list) + "}"
            
            if metric.metric_type == MetricType.HISTOGRAM:
                # 直方图需要导出多个值
                lines.append(f"{name}_sum{labels_str} {sum(metric.samples)}")
                lines.append(f"{name}_count{labels_str} {len(metric.samples)}")
                
                # 添加百分位数
                for p in [50, 95, 99]:
                    value = metric.get_percentile(p)
                    lines.append(f'{name}{{quantile="0.{p}"{labels_str[1:] if labels_str else ""} {value}')
            else:
                lines.append(f"{name}{labels_str} {metric.value}")
        
        return "\n".join(lines)


# 全局监控服务实例
monitoring_service = MonitoringService()


def setup_default_metrics():
    """设置默认指标"""
    # API指标
    monitoring_service.register_metric(
        "api_requests_total",
        MetricType.COUNTER,
        "API请求总数"
    )
    
    monitoring_service.register_metric(
        "api_errors_total",
        MetricType.COUNTER,
        "API错误总数"
    )
    
    monitoring_service.register_metric(
        "api_response_time_seconds",
        MetricType.HISTOGRAM,
        "API响应时间（秒）"
    )
    
    # 数据库指标
    monitoring_service.register_metric(
        "db_connections_active",
        MetricType.GAUGE,
        "活跃数据库连接数"
    )
    
    monitoring_service.register_metric(
        "db_query_duration_seconds",
        MetricType.HISTOGRAM,
        "数据库查询时间（秒）"
    )
    
    # 缓存指标
    monitoring_service.register_metric(
        "cache_hits_total",
        MetricType.COUNTER,
        "缓存命中总数"
    )
    
    monitoring_service.register_metric(
        "cache_misses_total",
        MetricType.COUNTER,
        "缓存未命中总数"
    )
    
    # AI模型指标
    monitoring_service.register_metric(
        "ai_model_requests_total",
        MetricType.COUNTER,
        "AI模型请求总数"
    )
    
    monitoring_service.register_metric(
        "ai_model_errors_total",
        MetricType.COUNTER,
        "AI模型错误总数"
    )
    
    monitoring_service.register_metric(
        "ai_model_processing_time_seconds",
        MetricType.HISTOGRAM,
        "AI模型处理时间（秒）"
    )
    
    # 用户指标
    monitoring_service.register_metric(
        "active_users",
        MetricType.GAUGE,
        "活跃用户数"
    )
    
    monitoring_service.register_metric(
        "rate_limit_exceeded_total",
        MetricType.COUNTER,
        "速率限制超出总数"
    )


def setup_default_alerts():
    """设置默认告警规则"""
    # 错误率告警
    monitoring_service.register_alert(
        "high_error_rate",
        AlertLevel.WARNING,
        "API错误率超过5%",
        "api_errors_total",
        threshold=0.05,
        comparison=">"
    )
    
    monitoring_service.register_alert(
        "critical_error_rate",
        AlertLevel.CRITICAL,
        "API错误率超过10%",
        "api_errors_total",
        threshold=0.10,
        comparison=">"
    )
    
    # 响应时间告警
    monitoring_service.register_alert(
        "slow_api_response",
        AlertLevel.WARNING,
        "API P95响应时间超过5秒",
        "api_response_time_seconds",
        threshold=5.0,
        comparison=">"
    )
    
    # AI模型告警
    monitoring_service.register_alert(
        "ai_model_low_success_rate",
        AlertLevel.WARNING,
        "AI模型成功率低于90%",
        "ai_model_errors_total",
        threshold=0.10,
        comparison=">"
    )
    
    # 数据库连接告警
    monitoring_service.register_alert(
        "high_db_connections",
        AlertLevel.WARNING,
        "数据库连接数过高",
        "db_connections_active",
        threshold=50,
        comparison=">"
    )


# 初始化默认指标和告警
setup_default_metrics()
setup_default_alerts()
