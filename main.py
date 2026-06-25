#!/usr/bin/env python3
"""
RealDiag - Real Time Diagnostic Assistant Software
Main entry point for the application
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORS_AVAILABLE = True
    COLOR_RESET = Style.RESET_ALL
except ImportError:
    COLORS_AVAILABLE = False
    COLOR_RESET = ""
    Fore = None
    Style = None

from config import Config
from diagnostics import SystemDiagnostics, NetworkDiagnostics, PerformanceMonitor


def print_colored(text, color=None):
    """Print colored text if colorama is available"""
    if COLORS_AVAILABLE and color:
        print(f"{color}{text}{COLOR_RESET}")
    else:
        print(text)


def print_header(title):
    """Print a formatted header"""
    print_colored("\n" + "=" * 60, Fore.CYAN if COLORS_AVAILABLE else None)
    print_colored(f"  {title}", Fore.CYAN if COLORS_AVAILABLE else None)
    print_colored("=" * 60, Fore.CYAN if COLORS_AVAILABLE else None)


def format_bytes(bytes_value):
    """Format bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def display_system_diagnostics(diagnostics):
    """Display system diagnostics in a formatted way"""
    print_header("SYSTEM DIAGNOSTICS")
    
    # System Info
    info = diagnostics['system_info']
    print_colored("\n[System Information]", Fore.YELLOW if COLORS_AVAILABLE else None)
    print(f"  Platform: {info['platform']} {info['platform_release']}")
    print(f"  Architecture: {info['architecture']}")
    print(f"  Hostname: {info['hostname']}")
    print(f"  Processor: {info['processor']}")
    
    # CPU
    cpu = diagnostics['cpu']
    print_colored("\n[CPU Status]", Fore.YELLOW if COLORS_AVAILABLE else None)
    status_color = Fore.GREEN if cpu['status'] == 'OK' else Fore.RED
    print_colored(f"  Status: {cpu['status']}", status_color if COLORS_AVAILABLE else None)
    print(f"  Usage: {cpu['cpu_percent']:.1f}%")
    print(f"  CPU Count: {cpu['cpu_count']}")
    print(f"  Threshold: {cpu['threshold']}%")
    
    # Memory
    memory = diagnostics['memory']
    print_colored("\n[Memory Status]", Fore.YELLOW if COLORS_AVAILABLE else None)
    status_color = Fore.GREEN if memory['status'] == 'OK' else Fore.RED
    print_colored(f"  Status: {memory['status']}", status_color if COLORS_AVAILABLE else None)
    print(f"  Usage: {memory['percent']:.1f}%")
    print(f"  Total: {format_bytes(memory['total'])}")
    print(f"  Used: {format_bytes(memory['used'])}")
    print(f"  Available: {format_bytes(memory['available'])}")
    print(f"  Threshold: {memory['threshold']}%")
    
    # Disk
    disk = diagnostics['disk']
    print_colored("\n[Disk Status]", Fore.YELLOW if COLORS_AVAILABLE else None)
    status_color = Fore.GREEN if disk['status'] == 'OK' else Fore.RED
    print_colored(f"  Status: {disk['status']}", status_color if COLORS_AVAILABLE else None)
    print(f"  Usage: {disk['percent']:.1f}%")
    print(f"  Total: {format_bytes(disk['total'])}")
    print(f"  Used: {format_bytes(disk['used'])}")
    print(f"  Free: {format_bytes(disk['free'])}")
    print(f"  Threshold: {disk['threshold']}%")


def display_network_diagnostics(diagnostics):
    """Display network diagnostics in a formatted way"""
    print_header("NETWORK DIAGNOSTICS")
    
    # Connectivity
    conn = diagnostics['connectivity']
    print_colored("\n[Connectivity]", Fore.YELLOW if COLORS_AVAILABLE else None)
    status_color = Fore.GREEN if conn['reachable'] else Fore.RED
    print_colored(f"  Status: {conn['status']}", status_color if COLORS_AVAILABLE else None)
    print(f"  Test Host: {conn['host']}")
    if not conn['reachable']:
        print(f"  Error: {conn.get('error', 'Unknown')}")
    
    # Network Stats
    stats = diagnostics['stats']
    print_colored("\n[Network Statistics]", Fore.YELLOW if COLORS_AVAILABLE else None)
    print(f"  Bytes Sent: {format_bytes(stats['bytes_sent'])}")
    print(f"  Bytes Received: {format_bytes(stats['bytes_recv'])}")
    print(f"  Packets Sent: {stats['packets_sent']}")
    print(f"  Packets Received: {stats['packets_recv']}")
    print(f"  Errors In: {stats['errin']}")
    print(f"  Errors Out: {stats['errout']}")


def display_performance_diagnostics(diagnostics):
    """Display performance diagnostics in a formatted way"""
    print_header("PERFORMANCE DIAGNOSTICS")
    
    # Uptime
    uptime = diagnostics['uptime']
    print_colored("\n[System Uptime]", Fore.YELLOW if COLORS_AVAILABLE else None)
    print(f"  Boot Time: {uptime['boot_time']}")
    print(f"  Uptime: {uptime['uptime_days']:.2f} days ({uptime['uptime_hours']:.2f} hours)")
    
    # Process Count
    proc_count = diagnostics['process_count']
    print_colored("\n[Process Information]", Fore.YELLOW if COLORS_AVAILABLE else None)
    print(f"  Total Processes: {proc_count['total_processes']}")
    
    # Top Processes
    print_colored("\n[Top Processes by CPU]", Fore.YELLOW if COLORS_AVAILABLE else None)
    top_procs = diagnostics['top_processes']
    for i, proc in enumerate(top_procs, 1):
        print(f"  {i}. {proc['name']} (PID: {proc['pid']})")
        print(f"     CPU: {proc['cpu_percent']}%, Memory: {proc['memory_percent']:.2f}%")
    
    # Load Average
    load = diagnostics['load_average']
    if load['load_1min'] is not None:
        print_colored("\n[Load Average]", Fore.YELLOW if COLORS_AVAILABLE else None)
        print(f"  1 min: {load['load_1min']:.2f}")
        print(f"  5 min: {load['load_5min']:.2f}")
        print(f"  15 min: {load['load_15min']:.2f}")


def save_report(data, report_type):
    """Save diagnostic report to file"""
    Config.ensure_directories()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = Config.REPORT_DIR / f"{report_type}_report_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    return filename


def run_diagnostics(args):
    """Run the requested diagnostics"""
    results = {}
    
    if args.system or args.all:
        print_colored("\nRunning system diagnostics...", Fore.CYAN if COLORS_AVAILABLE else None)
        sys_diag = SystemDiagnostics()
        system_results = sys_diag.run_full_diagnostic()
        results['system'] = system_results
        
        if not args.quiet:
            display_system_diagnostics(system_results)
    
    if args.network or args.all:
        print_colored("\nRunning network diagnostics...", Fore.CYAN if COLORS_AVAILABLE else None)
        net_diag = NetworkDiagnostics()
        network_results = net_diag.run_full_diagnostic()
        results['network'] = network_results
        
        if not args.quiet:
            display_network_diagnostics(network_results)
    
    if args.performance or args.all:
        print_colored("\nRunning performance diagnostics...", Fore.CYAN if COLORS_AVAILABLE else None)
        perf_mon = PerformanceMonitor()
        performance_results = perf_mon.run_full_diagnostic()
        results['performance'] = performance_results
        
        if not args.quiet:
            display_performance_diagnostics(performance_results)
    
    # Save report if requested
    if args.save and results:
        report_type = "full" if args.all else "_".join([k for k in results.keys()])
        filename = save_report(results, report_type)
        print_colored(f"\n✓ Report saved to: {filename}", Fore.GREEN if COLORS_AVAILABLE else None)
    
    return results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description=f"{Config.APP_NAME} - {Config.APP_DESCRIPTION}",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('-v', '--version', action='version', 
                       version=f'{Config.APP_NAME} {Config.APP_VERSION}')
    
    # Diagnostic options
    parser.add_argument('-s', '--system', action='store_true',
                       help='Run system diagnostics')
    parser.add_argument('-n', '--network', action='store_true',
                       help='Run network diagnostics')
    parser.add_argument('-p', '--performance', action='store_true',
                       help='Run performance diagnostics')
    parser.add_argument('-a', '--all', action='store_true',
                       help='Run all diagnostics')
    
    # Output options
    parser.add_argument('--save', action='store_true',
                       help='Save diagnostic report to file')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Suppress console output')
    
    args = parser.parse_args()
    
    # If no specific diagnostic is selected, show help
    if not (args.system or args.network or args.performance or args.all):
        parser.print_help()
        return 0
    
    try:
        # Print banner
        if not args.quiet:
            print_colored("\n" + "=" * 60, Fore.CYAN if COLORS_AVAILABLE else None)
            print_colored(f"  {Config.APP_NAME} v{Config.APP_VERSION}", Fore.CYAN if COLORS_AVAILABLE else None)
            print_colored(f"  {Config.APP_DESCRIPTION}", Fore.CYAN if COLORS_AVAILABLE else None)
            print_colored("=" * 60 + "\n", Fore.CYAN if COLORS_AVAILABLE else None)
        
        # Run diagnostics
        run_diagnostics(args)
        
        if not args.quiet:
            print_colored("\n✓ Diagnostics completed successfully!", Fore.GREEN if COLORS_AVAILABLE else None)
        
        return 0
    
    except KeyboardInterrupt:
        print_colored("\n\n✗ Diagnostics interrupted by user", Fore.YELLOW if COLORS_AVAILABLE else None)
        return 1
    except Exception as e:
        print_colored(f"\n✗ Error: {str(e)}", Fore.RED if COLORS_AVAILABLE else None)
        return 1


if __name__ == "__main__":
    sys.exit(main())
