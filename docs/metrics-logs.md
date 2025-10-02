# Métricas e Logs

## Introdução

O framework implementa um sistema abrangente de métricas e logging para monitorar performance, diagnosticar problemas e manter auditoria completa das operações. Este documento detalha todos os aspectos do sistema de observabilidade.

## Sistema de Logging

### Estrutura Hierárquica de Logs

#### Organização por Componente
```
logs/
├── framework.log                    # Log principal do framework
├── security_incident_framework.log # Log da classe principal
├── plugin_manager.log              # Log do gerenciador de plugins
├── config_loader.log               # Log do carregador de configuração  
├── models/                         # Logs específicos de modelos
│   ├── openai_model.log
│   ├── ollama_model.log
│   └── huggingface_model.log
├── techniques/                     # Logs de técnicas de prompt
│   ├── progressive_hint.log
│   ├── self_hint.log
│   └── hypothesis_testing.log
├── utils/                          # Logs de utilitários
│   ├── file_handlers.log
│   ├── metrics.log
│   └── security_extractor.log
├── performance.log                 # Métricas de performance
├── security.log                   # Eventos de segurança
├── audit.log                      # Log de auditoria
└── errors.log                     # Consolidação de erros
```

### Configuração de Logging

#### Configuração Padrão
```python
# utils/logger.py
import logging
import logging.handlers
from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime

class SecurityFrameworkLogger:
    """Logger personalizado para o framework."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.log_dir = Path(config.get('log_dir', 'logs'))
        self.log_dir.mkdir(exist_ok=True)
        
        # Configuração de níveis
        self.log_level = getattr(logging, config.get('level', 'INFO').upper())
        
        # Inicializa loggers
        self._setup_loggers()
    
    def _setup_loggers(self) -> None:
        """Configura todos os loggers do sistema."""
        
        # Logger principal
        self.main_logger = self._create_logger(
            'framework',
            self.log_dir / 'framework.log'
        )
        
        # Loggers específicos
        self.plugin_logger = self._create_logger(
            'plugin_manager', 
            self.log_dir / 'plugin_manager.log'
        )
        
        self.performance_logger = self._create_logger(
            'performance',
            self.log_dir / 'performance.log',
            formatter=self._create_performance_formatter()
        )
        
        self.security_logger = self._create_logger(
            'security',
            self.log_dir / 'security.log',
            formatter=self._create_security_formatter()
        )
        
        self.audit_logger = self._create_logger(
            'audit',
            self.log_dir / 'audit.log',
            formatter=self._create_audit_formatter()
        )
    
    def _create_logger(
        self, 
        name: str, 
        log_file: Path,
        formatter: logging.Formatter = None
    ) -> logging.Logger:
        """Cria logger configurado."""
        
        logger = logging.getLogger(name)
        logger.setLevel(self.log_level)
        
        # Remove handlers existentes
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Handler para arquivo
        if self.config.get('enable_file', True):
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=self.config.get('max_file_size_mb', 10) * 1024 * 1024,
                backupCount=self.config.get('backup_count', 5),
                encoding='utf-8'
            )
            
            if formatter:
                file_handler.setFormatter(formatter)
            else:
                file_handler.setFormatter(self._create_default_formatter())
            
            logger.addHandler(file_handler)
        
        # Handler para console
        if self.config.get('enable_console', True):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(self._create_console_formatter())
            logger.addHandler(console_handler)
        
        return logger
    
    def _create_default_formatter(self) -> logging.Formatter:
        """Formatter padrão para logs."""
        format_string = self.config.get(
            'format',
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        date_format = self.config.get('date_format', '%Y-%m-%d %H:%M:%S')
        
        return logging.Formatter(format_string, date_format)
    
    def _create_performance_formatter(self) -> logging.Formatter:
        """Formatter especializado para métricas de performance."""
        return logging.Formatter(
            '%(asctime)s - PERF - %(message)s',
            '%Y-%m-%d %H:%M:%S'
        )
    
    def _create_security_formatter(self) -> logging.Formatter:
        """Formatter para eventos de segurança."""
        return logging.Formatter(
            '%(asctime)s - SECURITY - %(levelname)s - %(message)s',
            '%Y-%m-%d %H:%M:%S'
        )
    
    def _create_audit_formatter(self) -> logging.Formatter:
        """Formatter para auditoria."""
        return logging.Formatter(
            '%(asctime)s - AUDIT - %(message)s',
            '%Y-%m-%d %H:%M:%S'
        )
```

#### Uso dos Loggers

```python
class SecurityIncidentFramework:
    """Classe principal com logging integrado."""
    
    def __init__(self, config_path: str = None):
        # Inicializa logging
        self.logger_manager = SecurityFrameworkLogger(config.get('logging', {}))
        self.logger = self.logger_manager.main_logger
        
        self.logger.info("Framework iniciado")
        self.logger.debug(f"Configuração carregada: {config_path}")
    
    def classify_incident(self, text: str, technique: str) -> dict:
        """Classifica incidente com logging detalhado."""
        
        start_time = time.time()
        session_id = str(uuid.uuid4())[:8]
        
        self.logger.info(
            f"[{session_id}] Iniciando classificação - Técnica: {technique}"
        )
        
        try:
            # Log de entrada (mascarado para privacidade)
            text_preview = text[:100] + "..." if len(text) > 100 else text
            self.logger.debug(f"[{session_id}] Texto de entrada: {text_preview}")
            
            # Execução da classificação
            result = self._execute_classification(text, technique, session_id)
            
            # Log de sucesso
            processing_time = time.time() - start_time
            self.logger.info(
                f"[{session_id}] Classificação concluída - "
                f"Categoria: {result.get('categoria')} - "
                f"Confiança: {result.get('confianca')} - "
                f"Tempo: {processing_time:.2f}s"
            )
            
            # Log de performance
            self._log_performance_metrics(session_id, processing_time, result)
            
            # Log de auditoria
            self._log_audit_event('classification', session_id, result)
            
            return result
            
        except Exception as e:
            # Log de erro
            processing_time = time.time() - start_time
            self.logger.error(
                f"[{session_id}] Erro na classificação: {str(e)} - "
                f"Tempo até erro: {processing_time:.2f}s",
                exc_info=True
            )
            
            # Log de segurança se necessário
            if isinstance(e, SecurityException):
                self._log_security_event('classification_error', session_id, str(e))
            
            raise
    
    def _log_performance_metrics(self, session_id: str, processing_time: float, result: dict):
        """Log de métricas de performance."""
        
        metrics = {
            'session_id': session_id,
            'processing_time_seconds': processing_time,
            'model_used': result.get('modelo'),
            'technique_used': result.get('tecnica'),
            'tokens_input': result.get('tokens_entrada', 0),
            'tokens_output': result.get('tokens_saida', 0),
            'api_calls': result.get('api_calls', 1),
            'cache_hit': result.get('cache_hit', False),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger_manager.performance_logger.info(json.dumps(metrics))
    
    def _log_audit_event(self, event_type: str, session_id: str, data: dict):
        """Log de evento de auditoria."""
        
        audit_entry = {
            'event_type': event_type,
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': getattr(self, 'current_user_id', 'system'),
            'data_hash': hashlib.sha256(str(data).encode()).hexdigest()[:16],
            'result_category': data.get('categoria'),
            'confidence': data.get('confianca'),
            'success': not data.get('erro', False)
        }
        
        self.logger_manager.audit_logger.info(json.dumps(audit_entry))
    
    def _log_security_event(self, event_type: str, session_id: str, details: str):
        """Log de evento de segurança."""
        
        security_entry = {
            'event_type': event_type,
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details,
            'source_ip': getattr(self, 'source_ip', 'localhost'),
            'severity': 'HIGH' if 'security' in event_type.lower() else 'MEDIUM'
        }
        
        self.logger_manager.security_logger.warning(json.dumps(security_entry))
```

## Sistema de Métricas

### Métricas de Performance

#### Coleta Automática
```python
class PerformanceMetrics:
    """Coletor de métricas de performance."""
    
    def __init__(self):
        self.metrics_buffer = []
        self.buffer_size = 1000
        self.start_time = time.time()
        
        # Métricas do sistema
        self.system_metrics = {
            'cpu_percent': [],
            'memory_usage_mb': [],
            'disk_usage_mb': [],
            'network_io': []
        }
    
    def record_classification_metrics(
        self, 
        session_id: str,
        model: str,
        technique: str,
        processing_time: float,
        result: dict
    ):
        """Registra métricas de uma classificação."""
        
        metrics = {
            'timestamp': time.time(),
            'session_id': session_id,
            'operation': 'classification',
            'model': model,
            'technique': technique,
            'processing_time_seconds': processing_time,
            'tokens_input': result.get('tokens_entrada', 0),
            'tokens_output': result.get('tokens_saida', 0),
            'confidence': result.get('confianca', 0),
            'success': not result.get('erro', False),
            'error_type': result.get('error_type') if result.get('erro') else None,
            'cache_hit': result.get('cache_hit', False),
            'api_calls': result.get('api_calls', 1),
            'cost_usd': result.get('cost_estimate', 0)
        }
        
        # Métricas do sistema no momento
        metrics.update(self._get_system_metrics())
        
        self.metrics_buffer.append(metrics)
        
        # Flush do buffer se necessário
        if len(self.metrics_buffer) >= self.buffer_size:
            self._flush_metrics()
    
    def _get_system_metrics(self) -> dict:
        """Coleta métricas do sistema."""
        import psutil
        
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=None),
                'memory_usage_mb': psutil.virtual_memory().used / 1024 / 1024,
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage_percent': psutil.disk_usage('/').percent,
                'active_threads': threading.active_count(),
                'open_files': len(psutil.Process().open_files()) if hasattr(psutil.Process(), 'open_files') else 0
            }
        except Exception as e:
            return {'system_metrics_error': str(e)}
    
    def _flush_metrics(self):
        """Salva métricas em arquivo."""
        
        if not self.metrics_buffer:
            return
        
        metrics_file = Path('logs/metrics.jsonl')
        
        with open(metrics_file, 'a', encoding='utf-8') as f:
            for metric in self.metrics_buffer:
                f.write(json.dumps(metric) + '\n')
        
        self.metrics_buffer.clear()
    
    def get_summary_stats(self, hours: int = 24) -> dict:
        """Gera estatísticas resumidas."""
        
        cutoff_time = time.time() - (hours * 3600)
        recent_metrics = [
            m for m in self.metrics_buffer 
            if m['timestamp'] > cutoff_time
        ]
        
        if not recent_metrics:
            return {'message': 'Nenhuma métrica recente encontrada'}
        
        # Estatísticas de classificação
        classification_times = [
            m['processing_time_seconds'] 
            for m in recent_metrics 
            if m['operation'] == 'classification'
        ]
        
        successful_classifications = len([
            m for m in recent_metrics 
            if m['operation'] == 'classification' and m['success']
        ])
        
        total_classifications = len([
            m for m in recent_metrics 
            if m['operation'] == 'classification'
        ])
        
        # Estatísticas por modelo
        model_stats = {}
        for metric in recent_metrics:
            model = metric.get('model', 'unknown')
            if model not in model_stats:
                model_stats[model] = {
                    'count': 0,
                    'avg_time': 0,
                    'success_rate': 0,
                    'total_cost': 0
                }
            
            model_stats[model]['count'] += 1
            model_stats[model]['total_cost'] += metric.get('cost_usd', 0)
        
        return {
            'summary_period_hours': hours,
            'total_operations': len(recent_metrics),
            'classification_stats': {
                'total': total_classifications,
                'successful': successful_classifications,
                'success_rate': (successful_classifications / total_classifications) * 100 if total_classifications > 0 else 0,
                'avg_processing_time': sum(classification_times) / len(classification_times) if classification_times else 0,
                'min_processing_time': min(classification_times) if classification_times else 0,
                'max_processing_time': max(classification_times) if classification_times else 0
            },
            'model_breakdown': model_stats,
            'system_averages': self._calculate_system_averages(recent_metrics)
        }
    
    def _calculate_system_averages(self, metrics: List[dict]) -> dict:
        """Calcula médias das métricas de sistema."""
        
        cpu_values = [m.get('cpu_percent', 0) for m in metrics if 'cpu_percent' in m]
        memory_values = [m.get('memory_percent', 0) for m in metrics if 'memory_percent' in m]
        
        return {
            'avg_cpu_percent': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
            'avg_memory_percent': sum(memory_values) / len(memory_values) if memory_values else 0,
            'peak_cpu_percent': max(cpu_values) if cpu_values else 0,
            'peak_memory_percent': max(memory_values) if memory_values else 0
        }
```

### Métricas de Qualidade

```python
class QualityMetrics:
    """Métricas de qualidade das classificações."""
    
    def __init__(self):
        self.quality_buffer = []
        self.confidence_thresholds = [0.5, 0.7, 0.8, 0.9, 0.95]
    
    def record_quality_metrics(self, result: dict, ground_truth: str = None):
        """Registra métricas de qualidade."""
        
        quality_data = {
            'timestamp': time.time(),
            'confidence': result.get('confianca', 0),
            'category': result.get('categoria'),
            'technique': result.get('tecnica'),
            'model': result.get('modelo'),
            'explanation_length': len(result.get('explicacao', '')),
            'processing_successful': not result.get('erro', False)
        }
        
        # Se temos ground truth, calcular precisão
        if ground_truth:
            quality_data['ground_truth'] = ground_truth
            quality_data['correct_classification'] = (
                result.get('categoria') == ground_truth
            )
        
        self.quality_buffer.append(quality_data)
    
    def get_quality_report(self, days: int = 7) -> dict:
        """Gera relatório de qualidade."""
        
        cutoff_time = time.time() - (days * 24 * 3600)
        recent_data = [
            q for q in self.quality_buffer 
            if q['timestamp'] > cutoff_time
        ]
        
        if not recent_data:
            return {'message': 'Dados insuficientes para relatório'}
        
        report = {
            'period_days': days,
            'total_classifications': len(recent_data),
            'confidence_distribution': self._analyze_confidence_distribution(recent_data),
            'technique_performance': self._analyze_technique_performance(recent_data),
            'model_performance': self._analyze_model_performance(recent_data)
        }
        
        # Adiciona análise de precisão se temos ground truth
        ground_truth_data = [q for q in recent_data if 'ground_truth' in q]
        if ground_truth_data:
            report['accuracy_analysis'] = self._analyze_accuracy(ground_truth_data)
        
        return report
    
    def _analyze_confidence_distribution(self, data: List[dict]) -> dict:
        """Analisa distribuição de confiança."""
        
        confidences = [q['confidence'] for q in data if q['processing_successful']]
        
        distribution = {}
        for threshold in self.confidence_thresholds:
            above_threshold = len([c for c in confidences if c >= threshold])
            distribution[f'above_{threshold}'] = {
                'count': above_threshold,
                'percentage': (above_threshold / len(confidences)) * 100 if confidences else 0
            }
        
        return {
            'total_successful': len(confidences),
            'average_confidence': sum(confidences) / len(confidences) if confidences else 0,
            'median_confidence': sorted(confidences)[len(confidences)//2] if confidences else 0,
            'distribution': distribution
        }
    
    def _analyze_accuracy(self, data: List[dict]) -> dict:
        """Analisa precisão das classificações."""
        
        correct = len([q for q in data if q.get('correct_classification', False)])
        total = len(data)
        
        # Precisão por nível de confiança
        accuracy_by_confidence = {}
        for threshold in self.confidence_thresholds:
            high_conf_data = [q for q in data if q['confidence'] >= threshold]
            if high_conf_data:
                high_conf_correct = len([q for q in high_conf_data if q.get('correct_classification', False)])
                accuracy_by_confidence[f'confidence_above_{threshold}'] = {
                    'total': len(high_conf_data),
                    'correct': high_conf_correct,
                    'accuracy': (high_conf_correct / len(high_conf_data)) * 100
                }
        
        return {
            'overall_accuracy': (correct / total) * 100 if total > 0 else 0,
            'total_evaluated': total,
            'correct_classifications': correct,
            'accuracy_by_confidence': accuracy_by_confidence
        }
```

## Dashboards e Visualização

### Dashboard Web Simples

```python
from flask import Flask, render_template, jsonify
import plotly.graph_objs as go
import plotly.utils

class MetricsDashboard:
    """Dashboard web para visualização de métricas."""
    
    def __init__(self, metrics_collector: PerformanceMetrics):
        self.app = Flask(__name__)
        self.metrics = metrics_collector
        self._setup_routes()
    
    def _setup_routes(self):
        """Configura rotas do dashboard."""
        
        @self.app.route('/')
        def dashboard():
            return render_template('dashboard.html')
        
        @self.app.route('/api/metrics/summary')
        def metrics_summary():
            return jsonify(self.metrics.get_summary_stats())
        
        @self.app.route('/api/metrics/performance_chart')
        def performance_chart():
            """Gera gráfico de performance ao longo do tempo."""
            
            recent_metrics = self.metrics.metrics_buffer[-100:]  # Últimas 100
            
            timestamps = [m['timestamp'] for m in recent_metrics]
            processing_times = [m.get('processing_time_seconds', 0) for m in recent_metrics]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=processing_times,
                mode='lines+markers',
                name='Tempo de Processamento',
                line=dict(color='blue')
            ))
            
            fig.update_layout(
                title='Performance ao Longo do Tempo',
                xaxis_title='Timestamp',
                yaxis_title='Tempo (segundos)',
                hovermode='x'
            )
            
            return jsonify(plotly.utils.PlotlyJSONEncoder().encode(fig))
        
        @self.app.route('/api/metrics/confidence_distribution')
        def confidence_distribution():
            """Gera gráfico de distribuição de confiança."""
            
            recent_metrics = [
                m for m in self.metrics.metrics_buffer[-1000:] 
                if m.get('confidence', 0) > 0
            ]
            
            confidences = [m['confidence'] for m in recent_metrics]
            
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=confidences,
                nbinsx=20,
                name='Distribuição de Confiança',
                marker_color='green'
            ))
            
            fig.update_layout(
                title='Distribuição de Níveis de Confiança',
                xaxis_title='Nível de Confiança',
                yaxis_title='Frequência'
            )
            
            return jsonify(plotly.utils.PlotlyJSONEncoder().encode(fig))
    
    def run(self, host='localhost', port=5000, debug=False):
        """Executa o dashboard."""
        self.app.run(host=host, port=port, debug=debug)
```

### Template HTML para Dashboard

```html
<!-- templates/dashboard.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Security Framework - Métricas</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .metric-card { 
            border: 1px solid #ddd; 
            padding: 15px; 
            margin: 10px; 
            border-radius: 5px; 
            display: inline-block;
            min-width: 200px;
        }
        .metric-value { font-size: 2em; font-weight: bold; color: #2e7d32; }
        .metric-label { color: #666; }
        .chart-container { margin: 20px 0; }
    </style>
</head>
<body>
    <h1>Security Incident Framework - Dashboard</h1>
    
    <div id="summary-cards">
        <!-- Cards de resumo serão carregados aqui -->
    </div>
    
    <div class="chart-container">
        <div id="performance-chart"></div>
    </div>
    
    <div class="chart-container">
        <div id="confidence-chart"></div>
    </div>
    
    <script>
        // Carrega dados de resumo
        fetch('/api/metrics/summary')
            .then(response => response.json())
            .then(data => {
                const summaryDiv = document.getElementById('summary-cards');
                
                if (data.classification_stats) {
                    const stats = data.classification_stats;
                    summaryDiv.innerHTML = `
                        <div class="metric-card">
                            <div class="metric-value">${stats.total}</div>
                            <div class="metric-label">Total de Classificações</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${stats.success_rate.toFixed(1)}%</div>
                            <div class="metric-label">Taxa de Sucesso</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${stats.avg_processing_time.toFixed(2)}s</div>
                            <div class="metric-label">Tempo Médio</div>
                        </div>
                    `;
                }
            });
        
        // Carrega gráfico de performance
        fetch('/api/metrics/performance_chart')
            .then(response => response.json())
            .then(data => {
                Plotly.newPlot('performance-chart', data.data, data.layout);
            });
        
        // Carrega gráfico de confiança
        fetch('/api/metrics/confidence_distribution')
            .then(response => response.json())
            .then(data => {
                Plotly.newPlot('confidence-chart', data.data, data.layout);
            });
        
        // Atualiza dados a cada 30 segundos
        setInterval(() => {
            location.reload();
        }, 30000);
    </script>
</body>
</html>
```

## Análise e Alertas

### Sistema de Alertas

```python
class AlertSystem:
    """Sistema de alertas baseado em métricas."""
    
    def __init__(self, config: dict):
        self.config = config
        self.alert_handlers = {
            'email': self._send_email_alert,
            'webhook': self._send_webhook_alert,
            'log': self._log_alert
        }
        
        # Thresholds configuráveis
        self.thresholds = config.get('alert_thresholds', {
            'error_rate_percent': 10.0,
            'avg_processing_time_seconds': 30.0,
            'low_confidence_rate_percent': 20.0,
            'cpu_usage_percent': 80.0,
            'memory_usage_percent': 85.0
        })
    
    def check_alerts(self, metrics_summary: dict):
        """Verifica se algum alerta deve ser disparado."""
        
        alerts = []
        
        # Verifica taxa de erro
        if metrics_summary.get('classification_stats', {}).get('success_rate', 100) < (100 - self.thresholds['error_rate_percent']):
            alerts.append({
                'type': 'high_error_rate',
                'severity': 'high',
                'message': f"Taxa de erro alta: {100 - metrics_summary['classification_stats']['success_rate']:.1f}%",
                'value': 100 - metrics_summary['classification_stats']['success_rate'],
                'threshold': self.thresholds['error_rate_percent']
            })
        
        # Verifica tempo de processamento
        avg_time = metrics_summary.get('classification_stats', {}).get('avg_processing_time', 0)
        if avg_time > self.thresholds['avg_processing_time_seconds']:
            alerts.append({
                'type': 'slow_processing',
                'severity': 'medium',
                'message': f"Processamento lento: {avg_time:.2f}s",
                'value': avg_time,
                'threshold': self.thresholds['avg_processing_time_seconds']
            })
        
        # Verifica uso de CPU
        cpu_usage = metrics_summary.get('system_averages', {}).get('avg_cpu_percent', 0)
        if cpu_usage > self.thresholds['cpu_usage_percent']:
            alerts.append({
                'type': 'high_cpu_usage',
                'severity': 'medium',
                'message': f"Uso alto de CPU: {cpu_usage:.1f}%",
                'value': cpu_usage,
                'threshold': self.thresholds['cpu_usage_percent']
            })
        
        # Envia alertas
        for alert in alerts:
            self._send_alert(alert)
        
        return alerts
    
    def _send_alert(self, alert: dict):
        """Envia alerta usando handlers configurados."""
        
        handlers = self.config.get('alert_handlers', ['log'])
        
        for handler_name in handlers:
            if handler_name in self.alert_handlers:
                try:
                    self.alert_handlers[handler_name](alert)
                except Exception as e:
                    logging.error(f"Erro ao enviar alerta via {handler_name}: {e}")
    
    def _log_alert(self, alert: dict):
        """Handler para log de alertas."""
        
        alert_logger = logging.getLogger('alerts')
        severity_map = {'low': logging.INFO, 'medium': logging.WARNING, 'high': logging.ERROR}
        
        alert_logger.log(
            severity_map.get(alert['severity'], logging.WARNING),
            f"ALERT [{alert['type']}]: {alert['message']} "
            f"(valor: {alert['value']}, limite: {alert['threshold']})"
        )
```

## Ferramentas de Análise

### Script de Análise de Logs

```bash
#!/bin/bash
# scripts/analyze_logs.sh

set -euo pipefail

LOG_DIR=${1:-"logs"}
DAYS=${2:-7}
OUTPUT_DIR="analysis_$(date +%Y%m%d_%H%M%S)"

mkdir -p "${OUTPUT_DIR}"

echo "=== Análise de Logs - Últimos ${DAYS} dias ==="

# Encontra arquivos de log recentes
find "${LOG_DIR}" -name "*.log" -mtime -${DAYS} -type f > "${OUTPUT_DIR}/log_files.txt"

echo "Arquivos de log encontrados:"
cat "${OUTPUT_DIR}/log_files.txt"

# Análise de níveis de log
echo -e "\n=== Níveis de Log ===" > "${OUTPUT_DIR}/log_levels.txt"
grep -h "INFO\|WARNING\|ERROR\|DEBUG" "${LOG_DIR}"/*.log | \
  sed 's/.*- \([A-Z]*\) -.*/\1/' | \
  sort | uniq -c | sort -nr >> "${OUTPUT_DIR}/log_levels.txt"

# Erros mais frequentes
echo -e "\n=== Erros Mais Frequentes ===" > "${OUTPUT_DIR}/frequent_errors.txt"
grep -h "ERROR" "${LOG_DIR}"/*.log | \
  sed 's/.*ERROR - //' | \
  sort | uniq -c | sort -nr | head -20 >> "${OUTPUT_DIR}/frequent_errors.txt"

# Atividade por hora
echo -e "\n=== Atividade por Hora ===" > "${OUTPUT_DIR}/hourly_activity.txt"
grep -h "2024-" "${LOG_DIR}"/*.log | \
  sed 's/^\([0-9-]* [0-9]*\):.*/\1/' | \
  sort | uniq -c | sort -k2 >> "${OUTPUT_DIR}/hourly_activity.txt"

# Métricas de performance (se disponível)
if [[ -f "${LOG_DIR}/performance.log" ]]; then
  echo -e "\n=== Métricas de Performance ===" > "${OUTPUT_DIR}/performance_stats.txt"
  
  # Tempo médio de processamento
  grep "processing_time_seconds" "${LOG_DIR}/performance.log" | \
    sed 's/.*"processing_time_seconds": *\([0-9.]*\).*/\1/' | \
    awk '{sum+=$1; count++} END {print "Tempo médio: " sum/count " segundos"}' >> "${OUTPUT_DIR}/performance_stats.txt"
  
  # Modelos mais usados
  grep "model" "${LOG_DIR}/performance.log" | \
    sed 's/.*"model": *"\([^"]*\)".*/\1/' | \
    sort | uniq -c | sort -nr | head -10 >> "${OUTPUT_DIR}/performance_stats.txt"
fi

# Gera relatório HTML
python3 << EOF > "${OUTPUT_DIR}/report.html"
import json
from datetime import datetime

html = """
<!DOCTYPE html>
<html>
<head>
    <title>Relatório de Análise de Logs</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
        pre { background: #f5f5f5; padding: 10px; overflow-x: auto; }
        h2 { color: #2e7d32; }
    </style>
</head>
<body>
    <h1>Relatório de Análise de Logs</h1>
    <p>Gerado em: ${datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="section">
        <h2>Níveis de Log</h2>
        <pre>$(cat ${OUTPUT_DIR}/log_levels.txt)</pre>
    </div>
    
    <div class="section">
        <h2>Erros Mais Frequentes</h2>
        <pre>$(cat ${OUTPUT_DIR}/frequent_errors.txt)</pre>
    </div>
    
    <div class="section">
        <h2>Atividade por Hora</h2>
        <pre>$(cat ${OUTPUT_DIR}/hourly_activity.txt)</pre>
    </div>
</body>
</html>
"""

print(html)
EOF

echo "Análise concluída! Relatório disponível em: ${OUTPUT_DIR}/report.html"
```

Este sistema completo de métricas e logs fornece observabilidade total do framework, permitindo monitoramento proativo, diagnóstico eficiente de problemas e otimização contínua da performance.