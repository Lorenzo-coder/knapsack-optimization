"""
Analysis and comparison report generation for optimization results.
Parses output files from all 4 tasks and generates comparison metrics.
"""

import re
import csv
import os
import logging
from typing import Dict, Optional, Any, List

logger = logging.getLogger(__name__)


def parse_results_file(filepath: str) -> Dict[str, Dict[str, Any]]:
    """
    Parse results from a task output file.
    
    Args:
        filepath: Path to results file
        
    Returns:
        Dictionary mapping instance names to their results
    """
    results = {}
    
    if not os.path.exists(filepath):
        logger.warning(f"Results file not found: {filepath}")
        return results

    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Error reading {filepath}: {e}")
        return results
    
    if not content.strip():
        logger.warning(f"Empty results file: {filepath}")
        return results
    
    # Split by instance blocks
    blocks = content.split("FILE: ")[1:]
    
    if not blocks:
        logger.warning(f"No result blocks found in {filepath}")
        return results
    
    for block in blocks:
        lines = block.strip().split('\n')
        filename = lines[0].strip() if lines else "UNKNOWN"
        
        # Extract total value
        val_match = re.search(r"Valore Totale:\s*([\d\.]+)", block)
        # Extract total weight
        weight_match = re.search(r"Peso Totale:\s*(\d+)\s*/\s*(\d+)", block)
        # Extract unique solutions (only for Task 4)
        unique_match = re.search(r"Soluzioni uniche trovate su 10 run:\s*(\d+)", block)
        
        results[filename] = {
            "value": float(val_match.group(1)) if val_match else 0,
            "weight": int(weight_match.group(1)) if weight_match else 0,
            "capacity": int(weight_match.group(2)) if weight_match else 0,
            "unique_runs": int(unique_match.group(1)) if unique_match else "N/A"
        }
    
    return results


def generate_comparison_report(output_dir: Optional[str] = None) -> None:
    """
    Generate comparative report of all optimization approaches.
    
    Args:
        output_dir: Directory containing results. If None, uses current directory.
    """
    if output_dir is None:
        output_dir = "."
    
    # Map output files with full paths
    files = {
        "Task 1 (Exact)": os.path.join(output_dir, "risultati_task1.txt"),
        "Task 2 (QUBO)": os.path.join(output_dir, "risultati_task2_qubo.txt"),
        "Task 3 (Qiskit)": os.path.join(output_dir, "risultati_task3_qiskit.txt"),
        "Task 4 (Dimod)": os.path.join(output_dir, "risultati_task4_dimod.txt")
    }
    
    all_data = {name: parse_results_file(path) for name, path in files.items()}
    
    # Get list of all JSON instance names found
    all_jsons = sorted(list(set([f for task in all_data.values() for f in task.keys()])))
    
    header = ["Instance", "T1_Exact", "T2_QUBO", "T3_Qiskit", "T4_Dimod", "Gap_T1_T4_(%)", "Status"]
    
    report_rows = []
    
    # Print formatted table
    print(f"\n{'='*120}")
    print(f"{'Instance':<30} | {'T1 (Exact)':<14} | {'T2 (QUBO)':<14} | {'T3 (Qiskit)':<14} | {'T4 (Dimod)':<14} | {'Gap %':<10} | {'Status':<10}")
    print(f"{'='*120}")

    for json_name in all_jsons:
        t1 = all_data["Task 1 (Exact)"].get(json_name, {}).get("value", 0)
        t2 = all_data["Task 2 (QUBO)"].get(json_name, {}).get("value", 0)
        t3 = all_data["Task 3 (Qiskit)"].get(json_name, {}).get("value", 0)
        t4 = all_data["Task 4 (Dimod)"].get(json_name, {}).get("value", 0)
        
        gap = 0
        status = "OK"
        
        if t1 > 0:
            gap = round(((t1 - t4) / t1) * 100, 2)
            if gap <= 5:
                status = "✅ Optimal"
            elif gap <= 20:
                status = "⚠️  Good"
            else:
                status = "❌ Poor"
        else:
            status = "⏭️  Skipped"
        
        # Format for display
        t1_str = f"{t1:.0f}" if t1 > 0 else "---"
        t2_str = f"{t2:.0f}" if t2 > 0 else "Skipped"
        t3_str = f"{t3:.0f}" if t3 > 0 else "Skipped"
        t4_str = f"{t4:.0f}" if t4 > 0 else "---"
        gap_str = f"{gap}%" if t1 > 0 else "N/A"
            
        report_rows.append([json_name, t1, t2, t3, t4, gap, status])
        print(f"{json_name:<30} | {t1_str:>14} | {t2_str:>14} | {t3_str:>14} | {t4_str:>14} | {gap_str:>10} | {status:<10}")
    
    print(f"{'='*120}\n")

    # Save to CSV in output folder
    report_path = os.path.join(output_dir, "final_comparison_report.csv")
    with open(report_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(report_rows)
    
    print(f"✅ CSV Report saved to: {report_path}")
    
    # Generate HTML report
    generate_html_report(output_dir, all_jsons, report_rows)

def generate_html_report(output_dir: str, all_jsons: List, report_rows: List) -> None:
    """Generate a beautiful HTML report."""
    
    # Calculate statistics
    total_instances = len(all_jsons)
    t1_success = sum(1 for r in report_rows if r[1] > 0)
    avg_gap = sum(r[5] for r in report_rows if r[1] > 0) / max(1, t1_success)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Knapsack Optimization Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .stat-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        
        .stat-card .label {{
            font-size: 0.95em;
            opacity: 0.9;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        
        th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        tr:hover {{
            background: #f5f5f5;
        }}
        
        .status-optimal {{ color: #4caf50; font-weight: bold; }}
        .status-good {{ color: #ff9800; font-weight: bold; }}
        .status-poor {{ color: #f44336; font-weight: bold; }}
        .status-skipped {{ color: #999; font-style: italic; }}
        
        .footer {{
            background: #f5f5f5;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Knapsack Optimization Report</h1>
            <p>Comprehensive Comparison of 4 Optimization Approaches</p>
        </div>
        
        <div class="content">
            <div class="stats">
                <div class="stat-card">
                    <div class="label">Total Instances</div>
                    <div class="value">{total_instances}</div>
                </div>
                <div class="stat-card">
                    <div class="label">T1 Success</div>
                    <div class="value">{t1_success}/{total_instances}</div>
                </div>
                <div class="stat-card">
                    <div class="label">Average Gap</div>
                    <div class="value">{avg_gap:.1f}%</div>
                </div>
            </div>
            
            <h2 style="margin-bottom: 20px;">Detailed Results</h2>
            <table>
                <thead>
                    <tr>
                        <th>Instance</th>
                        <th>T1 (Exact)</th>
                        <th>T2 (QUBO)</th>
                        <th>T3 (Qiskit)</th>
                        <th>T4 (Dimod)</th>
                        <th>Gap (%)</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    for row in report_rows:
        json_name, t1, t2, t3, t4, gap, status = row
        
        # Determine status class
        if "Optimal" in status:
            status_class = "status-optimal"
        elif "Good" in status:
            status_class = "status-good"
        elif "Poor" in status:
            status_class = "status-poor"
        else:
            status_class = "status-skipped"
        
        t1_str = f"{t1:.0f}" if t1 > 0 else "---"
        t2_str = f"{t2:.0f}" if t2 > 0 else "Skipped"
        t3_str = f"{t3:.0f}" if t3 > 0 else "Skipped"
        t4_str = f"{t4:.0f}" if t4 > 0 else "---"
        gap_str = f"{gap}%" if t1 > 0 else "N/A"
        
        html_content += f"""
                    <tr>
                        <td><strong>{json_name}</strong></td>
                        <td>{t1_str}</td>
                        <td>{t2_str}</td>
                        <td>{t3_str}</td>
                        <td>{t4_str}</td>
                        <td>{gap_str}</td>
                        <td class="{status_class}">{status}</td>
                    </tr>
"""
    
    html_content += """
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Generated by Knapsack Optimization Pipeline</p>
            <p style="margin-top: 10px; font-size: 0.9em;">
                <strong>Legend:</strong> 
                T1=Classical Exact, T2=QUBO, T3=Qiskit QAOA, T4=Dimod Annealing
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    html_path = os.path.join(output_dir, "report.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✨ HTML Report saved to: {html_path}\n")
    logger.info(f"HTML Report generated: {html_path}")

if __name__ == "__main__":
    # If run standalone, reads from current directory
    generate_comparison_report()