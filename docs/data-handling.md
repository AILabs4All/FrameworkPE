# Manipulação de Dados

## Introdução

Este documento detalha como o framework manipula dados de entrada e saída, incluindo formatos suportados, processamento, validação e transformações aplicadas durante o processo de classificação.

## Formatos de Entrada Suportados

### CSV (Comma-Separated Values)

#### Características
- **Encoding**: UTF-8 (padrão), também suporta ISO-8859-1, Windows-1252
- **Delimitadores**: `,` (padrão), `;`, `|`, `\t`
- **Aspas**: `"` (padrão), `'`
- **Escape**: `\"` ou `""`

#### Exemplo de Estrutura
```csv
id,title,description,severity,timestamp,source
INC001,"Malware Alert","Antivirus detected malware on workstation WS001",High,"2024-01-15 10:30:00","Security Team"
INC002,"Failed Logins","Multiple failed login attempts from IP 192.168.1.100",Medium,"2024-01-15 11:45:00","SIEM"
INC003,"Data Breach","Suspicious data access patterns detected",Critical,"2024-01-15 12:15:00","DLP System"
```

#### Configuração Avançada
```python
# Parâmetros de leitura CSV
csv_params = {
    'delimiter': ',',
    'quotechar': '"',
    'encoding': 'utf-8',
    'skiprows': 0,
    'nrows': None,
    'dtype': 'object',
    'na_values': ['', 'N/A', 'NULL', 'null', 'None'],
    'keep_default_na': True,
    'skip_blank_lines': True
}
```

### JSON (JavaScript Object Notation)

#### Estrutura de Array
```json
[
  {
    "id": "INC001",
    "title": "Malware Alert",
    "description": "Antivirus detected malware on workstation WS001",
    "severity": "High",
    "timestamp": "2024-01-15T10:30:00Z",
    "source": "Security Team",
    "metadata": {
      "system": "WS001",
      "antivirus": "Defender",
      "file_path": "C:\\Users\\user\\Downloads\\malware.exe"
    }
  },
  {
    "id": "INC002", 
    "title": "Failed Logins",
    "description": "Multiple failed login attempts from IP 192.168.1.100",
    "severity": "Medium",
    "timestamp": "2024-01-15T11:45:00Z",
    "source": "SIEM"
  }
]
```

#### Estrutura de Objeto com Chaves
```json
{
  "incidents": [
    {
      "id": "INC001",
      "data": {
        "title": "Security Alert",
        "description": "Suspicious activity detected"
      }
    }
  ],
  "metadata": {
    "total_count": 1,
    "export_date": "2024-01-15",
    "source_system": "Security Platform"
  }
}
```

### Excel (XLSX)

#### Características Suportadas
- **Múltiplas abas**: Processamento automático ou especificação de aba
- **Cabeçalhos**: Linha 1 como padrão
- **Tipos de dados**: Automático ou especificado por coluna
- **Células mescladas**: Tratamento especial
- **Fórmulas**: Valores calculados extraídos

#### Exemplo de Processamento
```python
# Leitura de arquivo Excel
excel_params = {
    'sheet_name': 'Incidents',  # ou None para todas as abas
    'header': 0,  # Linha de cabeçalho
    'index_col': None,
    'usecols': 'A:G',  # Colunas específicas
    'dtype': {
        'id': 'str',
        'severity': 'category',
        'timestamp': 'datetime64'
    },
    'parse_dates': ['timestamp'],
    'date_parser': pd.to_datetime
}
```

## Pipeline de Processamento

### 1. Detecção e Carregamento

```python
class DataLoader:
    """Carregador de dados com detecção automática de formato."""
    
    def __init__(self):
        self.supported_formats = ['.csv', '.json', '.xlsx', '.xls']
        self.encoding_detectors = ['utf-8', 'iso-8859-1', 'windows-1252']
    
    def load_file(self, file_path: Path) -> pd.DataFrame:
        """Carrega arquivo com detecção automática de formato."""
        
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        # Detecta formato pelo sufixo
        suffix = file_path.suffix.lower()
        
        if suffix == '.csv':
            return self._load_csv(file_path)
        elif suffix == '.json':
            return self._load_json(file_path)
        elif suffix in ['.xlsx', '.xls']:
            return self._load_excel(file_path)
        else:
            raise ValueError(f"Formato não suportado: {suffix}")
    
    def _load_csv(self, file_path: Path) -> pd.DataFrame:
        """Carrega arquivo CSV com detecção de encoding."""
        
        # Detecta encoding
        encoding = self._detect_encoding(file_path)
        
        # Detecta delimitador
        delimiter = self._detect_delimiter(file_path, encoding)
        
        try:
            df = pd.read_csv(
                file_path,
                encoding=encoding,
                delimiter=delimiter,
                quotechar='"',
                na_values=['', 'N/A', 'NULL', 'null', 'None'],
                keep_default_na=True,
                skip_blank_lines=True
            )
            
            self._log_load_info(file_path, df, encoding, delimiter)
            return df
            
        except Exception as e:
            raise ValueError(f"Erro ao carregar CSV {file_path}: {e}")
    
    def _detect_encoding(self, file_path: Path) -> str:
        """Detecta encoding do arquivo."""
        import chardet
        
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)  # Primeiros 10KB
            result = chardet.detect(raw_data)
            
            confidence = result.get('confidence', 0)
            detected_encoding = result.get('encoding', 'utf-8')
            
            # Fallback para encodings conhecidos se confiança baixa
            if confidence < 0.7:
                for encoding in self.encoding_detectors:
                    try:
                        raw_data.decode(encoding)
                        return encoding
                    except UnicodeDecodeError:
                        continue
            
            return detected_encoding
    
    def _detect_delimiter(self, file_path: Path, encoding: str) -> str:
        """Detecta delimitador CSV."""
        import csv
        
        with open(file_path, 'r', encoding=encoding) as f:
            # Lê primeiras linhas para detectar delimitador
            sample = f.read(1024)
            sniffer = csv.Sniffer()
            
            try:
                delimiter = sniffer.sniff(sample, delimiters=',;\t|').delimiter
                return delimiter
            except csv.Error:
                return ','  # Fallback para vírgula
```

### 2. Validação de Dados

```python
class DataValidator:
    """Validador de dados de entrada."""
    
    def __init__(self):
        self.required_types = {
            'text_columns': str,
            'numeric_columns': (int, float),
            'datetime_columns': (str, pd.Timestamp)
        }
    
    def validate_dataframe(self, df: pd.DataFrame, config: dict) -> Dict[str, Any]:
        """Valida DataFrame carregado."""
        
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {}
        }
        
        # 1. Verificações básicas
        if df.empty:
            validation_results['valid'] = False
            validation_results['errors'].append("DataFrame está vazio")
            return validation_results
        
        # 2. Verificar colunas obrigatórias
        required_columns = config.get('required_columns', [])
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            validation_results['errors'].append(
                f"Colunas obrigatórias ausentes: {missing_columns}"
            )
        
        # 3. Verificar tipos de dados
        for column in df.columns:
            self._validate_column_type(df[column], column, validation_results)
        
        # 4. Verificar valores nulos
        null_stats = self._analyze_null_values(df)
        validation_results['statistics']['null_values'] = null_stats
        
        # 5. Verificar duplicatas
        duplicate_stats = self._analyze_duplicates(df)
        validation_results['statistics']['duplicates'] = duplicate_stats
        
        # 6. Verificar qualidade do texto
        text_columns = self._identify_text_columns(df)
        text_quality = self._analyze_text_quality(df, text_columns)
        validation_results['statistics']['text_quality'] = text_quality
        
        return validation_results
    
    def _validate_column_type(self, series: pd.Series, column_name: str, results: dict):
        """Valida tipo de dados de uma coluna."""
        
        # Identifica tipo predominante
        non_null_values = series.dropna()
        if non_null_values.empty:
            results['warnings'].append(f"Coluna '{column_name}' está completamente vazia")
            return
        
        # Análise de tipos
        type_counts = {}
        for value in non_null_values.head(100):  # Amostra dos primeiros 100
            value_type = type(value).__name__
            type_counts[value_type] = type_counts.get(value_type, 0) + 1
        
        # Verifica consistência de tipos
        if len(type_counts) > 2:  # Muitos tipos diferentes
            results['warnings'].append(
                f"Coluna '{column_name}' tem tipos inconsistentes: {type_counts}"
            )
    
    def _analyze_null_values(self, df: pd.DataFrame) -> dict:
        """Analisa valores nulos no DataFrame."""
        
        null_stats = {}
        total_rows = len(df)
        
        for column in df.columns:
            null_count = df[column].isnull().sum()
            null_percentage = (null_count / total_rows) * 100
            
            null_stats[column] = {
                'count': null_count,
                'percentage': round(null_percentage, 2)
            }
        
        return null_stats
    
    def _analyze_text_quality(self, df: pd.DataFrame, text_columns: List[str]) -> dict:
        """Analisa qualidade das colunas de texto."""
        
        quality_stats = {}
        
        for column in text_columns:
            if column not in df.columns:
                continue
                
            text_series = df[column].dropna().astype(str)
            
            quality_stats[column] = {
                'total_entries': len(text_series),
                'avg_length': round(text_series.str.len().mean(), 2),
                'min_length': text_series.str.len().min(),
                'max_length': text_series.str.len().max(),
                'empty_strings': (text_series == '').sum(),
                'very_short': (text_series.str.len() < 10).sum(),
                'very_long': (text_series.str.len() > 1000).sum(),
                'encoding_issues': self._detect_encoding_issues(text_series)
            }
        
        return quality_stats
    
    def _detect_encoding_issues(self, text_series: pd.Series) -> int:
        """Detecta problemas de encoding no texto."""
        
        encoding_issues = 0
        problematic_chars = ['�', '\\x', '\\u']
        
        for text in text_series.head(100):  # Amostra
            if any(char in str(text) for char in problematic_chars):
                encoding_issues += 1
        
        return encoding_issues
```

### 3. Pré-processamento

```python
class DataPreprocessor:
    """Pré-processador de dados."""
    
    def __init__(self, config: dict):
        self.config = config
        self.text_cleaners = {
            'remove_html': self._remove_html_tags,
            'normalize_whitespace': self._normalize_whitespace,
            'remove_special_chars': self._remove_special_chars,
            'standardize_encoding': self._standardize_encoding
        }
    
    def preprocess_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica pré-processamento ao DataFrame."""
        
        df_processed = df.copy()
        
        # 1. Limpeza de colunas de texto
        text_columns = self._identify_text_columns(df_processed)
        for column in text_columns:
            df_processed[column] = self._clean_text_column(df_processed[column])
        
        # 2. Padronização de timestamps
        datetime_columns = self._identify_datetime_columns(df_processed)
        for column in datetime_columns:
            df_processed[column] = self._standardize_datetime(df_processed[column])
        
        # 3. Normalização de categóricas
        categorical_columns = self._identify_categorical_columns(df_processed)
        for column in categorical_columns:
            df_processed[column] = self._normalize_categorical(df_processed[column])
        
        # 4. Tratamento de valores ausentes
        df_processed = self._handle_missing_values(df_processed)
        
        return df_processed
    
    def _clean_text_column(self, series: pd.Series) -> pd.Series:
        """Limpa coluna de texto."""
        
        # Aplica limpezas configuradas
        cleaned_series = series.copy()
        
        for cleaner_name in self.config.get('text_cleaning', []):
            if cleaner_name in self.text_cleaners:
                cleaner_func = self.text_cleaners[cleaner_name] 
                cleaned_series = cleaned_series.apply(cleaner_func)
        
        return cleaned_series
    
    def _remove_html_tags(self, text: str) -> str:
        """Remove tags HTML do texto."""
        import re
        
        if pd.isna(text):
            return text
        
        # Remove tags HTML
        text = re.sub(r'<[^>]+>', '', str(text))
        
        # Decodifica entidades HTML
        import html
        text = html.unescape(text)
        
        return text
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normaliza espaços em branco."""
        if pd.isna(text):
            return text
        
        # Remove espaços múltiplos, tabs, quebras de linha
        import re
        text = re.sub(r'\s+', ' ', str(text))
        
        return text.strip()
    
    def _standardize_encoding(self, text: str) -> str:
        """Padroniza encoding do texto."""
        if pd.isna(text):
            return text
        
        text = str(text)
        
        # Correções comuns de encoding
        replacements = {
            'â€™': "'",
            'â€œ': '"',
            'â€': '"',
            'â€¦': '...',
            'Ã ': 'à',
            'Ã¡': 'á',
            'Ã©': 'é',
            'Ã³': 'ó'
        }
        
        for wrong, correct in replacements.items():
            text = text.replace(wrong, correct)
        
        return text
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Trata valores ausentes."""
        
        strategy = self.config.get('missing_value_strategy', 'keep')
        
        if strategy == 'drop_rows':
            # Remove linhas com qualquer valor ausente
            return df.dropna()
        
        elif strategy == 'drop_columns':
            # Remove colunas com muitos valores ausentes
            threshold = self.config.get('missing_threshold', 0.5)
            return df.dropna(axis=1, thresh=int(len(df) * (1 - threshold)))
        
        elif strategy == 'fill_text':
            # Preenche valores ausentes em colunas de texto
            text_columns = self._identify_text_columns(df)
            fill_value = self.config.get('text_fill_value', '')
            
            for column in text_columns:
                df[column] = df[column].fillna(fill_value)
        
        return df
```

## Formatos de Saída

### CSV Otimizado

```python
def export_to_csv(results: List[dict], output_path: Path, config: dict) -> None:
    """Exporta resultados para CSV otimizado."""
    
    df = pd.DataFrame(results)
    
    csv_config = config.get('csv', {})
    
    # Configurações de escrita
    write_params = {
        'index': False,
        'encoding': csv_config.get('encoding', 'utf-8'),
        'sep': csv_config.get('delimiter', ','),
        'quotechar': csv_config.get('quotechar', '"'),
        'quoting': csv.QUOTE_MINIMAL,
        'date_format': csv_config.get('date_format', '%Y-%m-%d %H:%M:%S'),
        'float_format': csv_config.get('float_format', '%.3f')
    }
    
    # Otimizações para arquivos grandes
    if len(df) > 100000:
        # Escreve em chunks para economizar memória
        chunk_size = 10000
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i:i+chunk_size]
            mode = 'w' if i == 0 else 'a'
            header = i == 0
            
            chunk.to_csv(
                output_path,
                mode=mode, 
                header=header,
                **write_params
            )
    else:
        df.to_csv(output_path, **write_params)
```

### JSON Estruturado

```python
def export_to_json(results: List[dict], output_path: Path, config: dict) -> None:
    """Exporta resultados para JSON estruturado."""
    
    json_config = config.get('json', {})
    
    # Estrutura de saída
    output_data = {
        'metadata': {
            'export_timestamp': datetime.utcnow().isoformat(),
            'total_incidents': len(results),
            'framework_version': config.get('framework', {}).get('version', '2.0.0'),
            'classification_model': config.get('model_used'),
            'technique': config.get('technique_used')
        },
        'results': results
    }
    
    # Adiciona estatísticas se solicitado
    if json_config.get('include_statistics', False):
        output_data['statistics'] = _calculate_statistics(results)
    
    # Serializa com configurações
    json_params = {
        'indent': json_config.get('indent', 2),
        'ensure_ascii': json_config.get('ensure_ascii', False),
        'sort_keys': json_config.get('sort_keys', False),
        'separators': tuple(json_config.get('separators', [',', ':']))
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, **json_params, cls=CustomJSONEncoder)
```

### Excel com Formatação

```python
def export_to_excel(results: List[dict], output_path: Path, config: dict) -> None:
    """Exporta resultados para Excel com formatação."""
    
    df = pd.DataFrame(results)
    excel_config = config.get('xlsx', {})
    
    with pd.ExcelWriter(
        output_path, 
        engine='xlsxwriter',
        options={'strings_to_formulas': False}
    ) as writer:
        
        # Aba principal com resultados
        sheet_name = excel_config.get('sheet_name', 'Classification Results')
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Formatação
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        
        # Formatos
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        
        confidence_format = workbook.add_format({
            'num_format': '0.000',
            'align': 'center'
        })
        
        category_format = workbook.add_format({
            'align': 'center',
            'bold': True
        })
        
        # Aplica formatação
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            
            # Ajusta largura das colunas
            column_width = max(
                df[value].astype(str).apply(len).max(),
                len(value)
            ) + 2
            worksheet.set_column(col_num, col_num, min(column_width, 50))
        
        # Formatação condicional para confiança
        if 'confianca' in df.columns:
            confidence_col = df.columns.get_loc('confianca')
            worksheet.conditional_format(
                1, confidence_col, len(df), confidence_col,
                {
                    'type': '3_color_scale',
                    'min_color': '#F8696B',
                    'mid_color': '#FFEB84', 
                    'max_color': '#63BE7B'
                }
            )
        
        # Adiciona filtros automáticos
        if excel_config.get('auto_filter', True):
            worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)
        
        # Congela primeira linha
        if excel_config.get('freeze_header', True):
            worksheet.freeze_panes(1, 0)
```

## Qualidade e Monitoramento

### Métricas de Qualidade de Dados

```python
class DataQualityMonitor:
    """Monitor de qualidade de dados."""
    
    def generate_quality_report(self, df: pd.DataFrame) -> dict:
        """Gera relatório de qualidade dos dados."""
        
        report = {
            'overview': {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
            },
            'completeness': self._analyze_completeness(df),
            'consistency': self._analyze_consistency(df),
            'validity': self._analyze_validity(df),
            'accuracy': self._analyze_accuracy(df),
            'recommendations': []
        }
        
        # Gera recomendações baseadas na análise
        report['recommendations'] = self._generate_recommendations(report)
        
        return report
    
    def _analyze_completeness(self, df: pd.DataFrame) -> dict:
        """Analisa completude dos dados."""
        
        completeness = {}
        
        for column in df.columns:
            non_null_count = df[column].count()
            total_count = len(df)
            completeness_pct = (non_null_count / total_count) * 100
            
            completeness[column] = {
                'non_null_count': non_null_count,
                'null_count': total_count - non_null_count,
                'completeness_percentage': round(completeness_pct, 2)
            }
        
        return completeness
    
    def _generate_recommendations(self, report: dict) -> List[str]:
        """Gera recomendações baseadas no relatório."""
        
        recommendations = []
        
        # Recomendações de completude
        for column, stats in report['completeness'].items():
            if stats['completeness_percentage'] < 80:
                recommendations.append(
                    f"Coluna '{column}' tem baixa completude ({stats['completeness_percentage']:.1f}%). "
                    f"Considere investigar a fonte dos dados ou aplicar estratégias de preenchimento."
                )
        
        # Recomendações de consistência
        for column, stats in report['consistency'].items():
            if stats.get('type_inconsistency', 0) > 0.1:
                recommendations.append(
                    f"Coluna '{column}' tem inconsistências de tipo. "
                    f"Padronize o formato dos dados na fonte."
                )
        
        return recommendations
```

Este sistema robusto de manipulação de dados garante que o framework possa processar eficientemente dados de diferentes fontes e formatos, mantendo alta qualidade e rastreabilidade durante todo o pipeline.