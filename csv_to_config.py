#!/usr/bin/env python3
"""
CSV to PX4 Config File Converter

This script takes a CSV file with parameter data and converts it to a PX4 config file
format with proper initialization header and param set-default commands.

Usage:
    python csv_to_config.py input.csv output.conf

CSV Format Expected:
    Column 1: (ignored)
    Column 2: (ignored)
    Column 3: Parameter name
    Column 4: Parameter value
    Column 5: (ignored)
"""

import sys
import os
import argparse
from pathlib import Path


def create_config_header():
    """Create the standard PX4 config file header."""
    return """#!/bin/sh
#
# @name Generated Parameter Configuration
#
# @type Auto-generated from CSV
#

. ${R}etc/init.d/rc.vtol_defaults

"""


def parse_csv_line(line):
    """
    Parse a CSV line and extract parameter name and value.

    Args:
        line (str): CSV line with tab-separated values

    Returns:
        tuple: (param_name, param_value) or (None, None) if invalid
    """
    line = line.strip()
    if not line or line.startswith('#'):
        return None, None

    parts = line.split('\t')
    if len(parts) < 4:
        return None, None

    param_name = parts[2].strip()
    param_value = parts[3].strip()

    if not param_name or not param_value:
        return None, None

    return param_name, param_value


def convert_csv_to_config(csv_file_path, output_file_path):
    """
    Convert CSV file to PX4 config format.

    Args:
        csv_file_path (str): Path to input CSV file
        output_file_path (str): Path to output config file
    """
    try:
        with open(csv_file_path, 'r') as csv_file:
            lines = csv_file.readlines()
    except FileNotFoundError:
        print(f"Error: Input file '{csv_file_path}' not found.")
        return False
    except Exception as e:
        print(f"Error reading input file: {e}")
        return False

    # Create config content
    config_content = create_config_header()

    param_count = 0
    for line_num, line in enumerate(lines, 1):
        param_name, param_value = parse_csv_line(line)

        if param_name and param_value:
            config_content += f"param set-default {param_name} {param_value}\n"
            param_count += 1
        elif line.strip():  # Non-empty line that wasn't parsed
            print(f"Warning: Skipping invalid line {line_num}: {line.strip()}")

    # Add final newline
    config_content += "\n"

    try:
        with open(output_file_path, 'w') as output_file:
            output_file.write(config_content)
        print(f"Successfully converted {param_count} parameters to '{output_file_path}'")
        return True
    except Exception as e:
        print(f"Error writing output file: {e}")
        return False


def main():
    """Main function to handle command line arguments and execute conversion."""
    parser = argparse.ArgumentParser(
        description="Convert CSV parameter data to PX4 config file format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
    python csv_to_config.py parameters.csv airframe.conf

CSV format expected (tab-separated):
    1    1    ASPD_BETA_GATE    1    6
    1    1    ASPD_BETA_NOISE   0.150000006    9
    1    1    ASPD_DO_CHECKS    6    6
        """
    )

    parser.add_argument('input_csv', help='Input CSV file path')
    parser.add_argument('output_config', help='Output config file path')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')

    args = parser.parse_args()

    # Validate input file exists
    if not os.path.exists(args.input_csv):
        print(f"Error: Input file '{args.input_csv}' does not exist.")
        sys.exit(1)

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output_config)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if args.verbose:
        print(f"Converting '{args.input_csv}' to '{args.output_config}'")

    success = convert_csv_to_config(args.input_csv, args.output_config)

    if success:
        print("Conversion completed successfully!")
        sys.exit(0)
    else:
        print("Conversion failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
