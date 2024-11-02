import pandas as pd
import numpy as np
import json
from datetime import datetime
import re
from typing import Dict, List, Any

class DataQualityAnalyzer:
    def __init__(self, file_path: str):
        """Initialize the analyzer with a file path."""
        self.file_path = file_path
        # Read file based on extension
        if file_path.endswith('.csv'):
            try:
                self.df = pd.read_csv(file_path)
            except:
                self.df = pd.read_csv(file_path, encoding="latin-1")
            
        elif file_path.endswith(('.xlsx', '.xls')):
            try:
                self.df = pd.read_excel(file_path)
            except:
                self.df = pd.read_excel(file_path, encoding="latin-1")
        else:
            raise ValueError("Unsupported file format. Please use CSV or Excel files.")
        
        self.total_rows = len(self.df)
        self.total_columns = len(self.df.columns)
        self.columns = list(self.df.columns)

    def analyze_completeness(self) -> Dict[str, Any]:
        """Analyze data completeness."""
        total_cells = self.total_rows * self.total_columns
        total_null_cells = self.df.isna().sum().sum()
        null_counts = self.df.isna().sum().to_dict()
        
        completeness_ratio = 1 - (total_null_cells / total_cells)
        
        validations = {}
        for col in self.columns:
            unexpected_count = self.df[col].isna().sum()
            unexpected_percent = (unexpected_count / self.total_rows) * 100
            validations[col] = {
                "success": unexpected_count == 0,
                "unexpected_count": int(unexpected_count),
                "unexpected_percent": round(unexpected_percent, 3)
            }
        
        return {
            "metrics": {
                "total_rows": self.total_rows,
                "total_cells": total_cells,
                "total_null_cells": int(total_null_cells),
                "completeness_ratio": round(completeness_ratio, 3),
                "null_counts_by_column": null_counts
            },
            "validations": validations,
            "grade": self._calculate_grade(completeness_ratio)
        }

    def analyze_accuracy(self) -> Dict[str, Any]:
        """Analyze data accuracy."""
        metrics = {}
        for col in self.columns:
            col_metrics = {}
            col_metrics["data_type"] = str(self.df[col].dtype)
            col_metrics["unique_values_count"] = self.df[col].nunique()
            
            if pd.api.types.is_numeric_dtype(self.df[col]):
                col_metrics.update({
                    "min": float(self.df[col].min()),
                    "max": float(self.df[col].max()),
                    "mean": round(float(self.df[col].mean()), 3),
                    "std": round(float(self.df[col].std()), 3)
                })
            elif pd.api.types.is_string_dtype(self.df[col]):
                if "email" in col.lower():
                    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
                    pattern_matches = self.df[col].str.match(email_pattern, na=False)
                    col_metrics["pattern_match_rate"] = round(pattern_matches.mean(), 3)
            
            metrics[col] = col_metrics
        
        # Simplified accuracy score based on data type consistency
        accuracy_score = 1.0
        for col in self.columns:
            if self.df[col].dtype == 'object':
                # Penalize for mixed data types in string columns
                unique_types = self.df[col].apply(type).nunique()
                if unique_types > 1:
                    accuracy_score -= 0.05
        
        return {
            "metrics": metrics,
            "validations": {
                "data_type_check": {
                    "success": accuracy_score > 0.95,
                    "unexpected_count": int((1 - accuracy_score) * self.total_rows)
                }
            },
            "grade": self._calculate_grade(accuracy_score)
        }

    def analyze_consistency(self) -> Dict[str, Any]:
        """Analyze data consistency."""
        metrics = {}
        for col in self.columns:
            if pd.api.types.is_string_dtype(self.df[col]):
                value_counts = self.df[col].value_counts()
                metrics[col] = {
                    "unique_values_count": len(value_counts),
                    "most_common_value": value_counts.index[0],
                    "most_common_value_frequency": int(value_counts.iloc[0]),
                    "value_distribution": value_counts.to_dict(),
                    "length_stats": {
                        "min_length": int(self.df[col].str.len().min()),
                        "max_length": int(self.df[col].str.len().max()),
                        "mean_length": round(float(self.df[col].str.len().mean()), 1)
                    }
                }
        
        # Calculate consistency score based on value distributions
        consistency_score = 1.0
        for col in metrics:
            unique_ratio = metrics[col]["unique_values_count"] / self.total_rows
            if unique_ratio > 0.9 and "id" not in col.lower() and "email" not in col.lower():
                consistency_score -= 0.1
        
        return {
            "metrics": metrics,
            "validations": {
                "value_set_check": {
                    "success": consistency_score > 0.9,
                    "unexpected_count": int((1 - consistency_score) * self.total_rows)
                }
            },
            "grade": self._calculate_grade(consistency_score)
        }

    def analyze_uniqueness(self) -> Dict[str, Any]:
        """Analyze data uniqueness."""
        metrics = {}
        for col in self.columns:
            duplicate_counts = self.df[col].value_counts()
            duplicates = duplicate_counts[duplicate_counts > 1].to_dict()
            metrics[col] = {
                "unique_count": self.df[col].nunique(),
                "duplicate_count": len(duplicates),
                "duplication_ratio": round(len(duplicates) / self.total_rows, 3),
                "duplicate_values": duplicates
            }
        
        return {
            "metrics": metrics,
            "validations": {
                f"{col}_uniqueness": {
                    "success": metrics[col]["duplicate_count"] == 0,
                    "unexpected_count": metrics[col]["duplicate_count"],
                    "unexpected_percent": round(metrics[col]["duplication_ratio"] * 100, 3)
                } for col in self.columns
            },
            "grade": self._calculate_grade(1 - max(m["duplication_ratio"] for m in metrics.values()))
        }

    def _calculate_grade(self, score: float) -> Dict[str, Any]:
        """Calculate grade based on score."""
        score = round(score, 3)
        if score >= 0.95:
            interpretation = "Excellent"
        elif score >= 0.90:
            interpretation = "Good"
        elif score >= 0.85:
            interpretation = "Fair"
        elif score >= 0.80:
            interpretation = "Poor"
        else:
            interpretation = "Failed"
        
        return {
            "score": score,
            "interpretation": interpretation,
            "threshold_met": score >= 0.85
        }

    def generate_report(self) -> Dict[str, Any]:
        """Generate complete data quality report."""
        completeness = self.analyze_completeness()
        accuracy = self.analyze_accuracy()
        consistency = self.analyze_consistency()
        uniqueness = self.analyze_uniqueness()
        
        category_scores = {
            "completeness": completeness["grade"]["score"],
            "accuracy": accuracy["grade"]["score"],
            "consistency": consistency["grade"]["score"],
            "uniqueness": uniqueness["grade"]["score"]
        }
        
        overall_score = round(np.mean(list(category_scores.values())), 3)
        
        recommendations = []
        if completeness["grade"]["score"] < 0.98:
            recommendations.append({
                "category": "completeness",
                "issue": "Missing values detected",
                "impact": "Medium",
                "suggestion": "Review and fill in missing data where possible"
            })
        
        if uniqueness["grade"]["score"] < 0.98:
            recommendations.append({
                "category": "uniqueness",
                "issue": "Duplicate values found",
                "impact": "High",
                "suggestion": "Investigate and resolve duplicate records"
            })
        
        return {
            "metadata": {
                "filename": self.file_path,
                "timestamp": datetime.now().isoformat(),
                "total_rows": self.total_rows,
                "total_columns": self.total_columns,
                "columns": self.columns,
                "analysis_version": "1.0"
            },
            "quality_checks": {
                "completeness": completeness,
                "accuracy": accuracy,
                "consistency": consistency,
                "uniqueness": uniqueness
            },
            "overall_quality": {
                "score": overall_score,
                "grade": self._calculate_grade(overall_score)["interpretation"],
                "interpretation": self._calculate_grade(overall_score)["interpretation"],
                "category_scores": category_scores,
                "recommendations": recommendations
            },
            "thresholds": {
                "grades": {
                    "A": {"min": 0.95, "interpretation": "Excellent"},
                    "B": {"min": 0.90, "interpretation": "Good"},
                    "C": {"min": 0.85, "interpretation": "Fair"},
                    "D": {"min": 0.80, "interpretation": "Poor"},
                    "F": {"min": 0.00, "interpretation": "Failed"}
                },
                "critical_checks": {
                    "null_tolerance": ["id", "email"],
                    "uniqueness_required": ["id", "email"],
                    "format_validation": ["email", "signup_date"]
                }
            }
        }

def evaluate(data_path):
    # Initialize analyzer with your data file
    analyzer = DataQualityAnalyzer(data_path)

    # Generate report
    report = analyzer.generate_report()
    
    return report