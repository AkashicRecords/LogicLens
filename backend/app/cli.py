import argparse
import json
import os
import sys
from typing import Dict, Optional

from .utils.logger import AILogger, get_logger
from .utils.test_utils import TestManager, get_test_manager
from .utils.monitoring import MonitoringManager, get_monitoring_manager

def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI"""
    parser = argparse.ArgumentParser(
        prog="logiclens",
        description="LogicLens - AI-powered log analysis and system monitoring"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Web server command
    web_parser = subparsers.add_parser("web", help="Start the web interface")
    web_parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to")
    web_parser.add_argument("--port", type=int, default=5000, help="Port to listen on")
    web_parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    # Logging commands
    log_parser = subparsers.add_parser("log", help="Log events")
    log_parser.add_argument("--component", type=str, required=True, help="Component name")
    log_parser.add_argument("--message", type=str, required=True, help="Log message")
    log_parser.add_argument("--level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Log level")
    log_parser.add_argument("--details", type=str, help="JSON-formatted details")
    
    # Test commands
    test_parser = subparsers.add_parser("test", help="Test management")
    test_subparsers = test_parser.add_subparsers(dest="test_command", help="Test command")
    
    # Start test suite
    start_suite_parser = test_subparsers.add_parser("start-suite", help="Start a test suite")
    start_suite_parser.add_argument("--name", type=str, required=True, help="Test suite name")
    
    # Add test result
    add_result_parser = test_subparsers.add_parser("add-result", help="Add a test result")
    add_result_parser.add_argument("--suite-id", type=str, required=True, help="Test suite ID")
    add_result_parser.add_argument("--test-id", type=str, required=True, help="Test ID")
    add_result_parser.add_argument("--name", type=str, required=True, help="Test name")
    add_result_parser.add_argument("--status", type=str, required=True, choices=["PASSED", "FAILED", "SKIPPED"], help="Test status")
    add_result_parser.add_argument("--duration", type=float, default=0.0, help="Test duration in seconds")
    add_result_parser.add_argument("--message", type=str, help="Test message")
    
    # End test suite
    end_suite_parser = test_subparsers.add_parser("end-suite", help="End a test suite")
    end_suite_parser.add_argument("--suite-id", type=str, required=True, help="Test suite ID")
    end_suite_parser.add_argument("--status", type=str, choices=["PASSED", "FAILED"], help="Override test suite status")
    
    # Import JUnit XML
    import_junit_parser = test_subparsers.add_parser("import-junit", help="Import JUnit XML")
    import_junit_parser.add_argument("--file", type=str, required=True, help="JUnit XML file path")
    import_junit_parser.add_argument("--name", type=str, help="Test suite name")
    
    # Monitoring commands
    monitor_parser = subparsers.add_parser("monitor", help="System monitoring")
    monitor_subparsers = monitor_parser.add_subparsers(dest="monitor_command", help="Monitoring command")
    
    # Collect metrics
    collect_metrics_parser = monitor_subparsers.add_parser("collect", help="Collect system metrics")
    collect_metrics_parser.add_argument("--output", type=str, help="Output file path")
    
    # Analyze trends
    analyze_trends_parser = monitor_subparsers.add_parser("analyze", help="Analyze metric trends")
    analyze_trends_parser.add_argument("--metric", type=str, required=True, help="Metric name (e.g., system.cpu_percent)")
    analyze_trends_parser.add_argument("--window", type=int, default=60, help="Analysis window")
    
    return parser

def run_web_command(args: argparse.Namespace) -> None:
    """Run the web server"""
    from . import create_app
    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug)

def run_log_command(args: argparse.Namespace) -> None:
    """Run the log command"""
    logger = get_logger()
    
    details = None
    if args.details:
        try:
            details = json.loads(args.details)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in --details: {args.details}")
            sys.exit(1)
    
    log_entry = logger.log_event(
        component=args.component,
        message=args.message,
        level=args.level,
        details=details
    )
    
    print(json.dumps(log_entry, indent=2))

def run_test_command(args: argparse.Namespace) -> None:
    """Run the test command"""
    manager = get_test_manager()
    
    if args.test_command == "start-suite":
        suite_id = manager.start_suite(name=args.name)
        print(json.dumps({"suite_id": suite_id}, indent=2))
        
    elif args.test_command == "add-result":
        result = manager.add_test_result(
            suite_id=args.suite_id,
            test_id=args.test_id,
            test_name=args.name,
            status=args.status,
            duration=args.duration,
            message=args.message
        )
        print(json.dumps(result, indent=2))
        
    elif args.test_command == "end-suite":
        suite = manager.end_suite(args.suite_id, args.status)
        print(json.dumps(suite, indent=2))
        
    elif args.test_command == "import-junit":
        suite_id = manager.import_junit_xml(args.file, args.name)
        suite = manager.get_suite(suite_id)
        print(json.dumps(suite, indent=2))
        
    else:
        print("Error: Unknown test command")
        sys.exit(1)

def run_monitor_command(args: argparse.Namespace) -> None:
    """Run the monitor command"""
    manager = get_monitoring_manager()
    
    if args.monitor_command == "collect":
        metrics = manager.collect_metrics()
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(metrics, f, indent=2)
        else:
            print(json.dumps(metrics, indent=2))
            
    elif args.monitor_command == "analyze":
        analysis = manager.analyze_trends(args.metric, args.window)
        print(json.dumps(analysis, indent=2))
        
    else:
        print("Error: Unknown monitor command")
        sys.exit(1)

def main() -> None:
    """Main entry point for the CLI"""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.command == "web":
        run_web_command(args)
    elif args.command == "log":
        run_log_command(args)
    elif args.command == "test":
        run_test_command(args)
    elif args.command == "monitor":
        run_monitor_command(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main() 