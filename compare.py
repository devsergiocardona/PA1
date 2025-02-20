#!/usr/bin/env python3
import sys

def compare_files(file1, file2):
    with open(file1) as f1, open(file2) as f2:
        f1_lines = f1.readlines()
        f2_lines = f2.readlines()
    
    differences = []
    max_lines = max(len(f1_lines), len(f2_lines))
    for i in range(max_lines):
        line1 = f1_lines[i].rstrip() if i < len(f1_lines) else "<no line>"
        line2 = f2_lines[i].rstrip() if i < len(f2_lines) else "<no line>"
        if line1 != line2:
            differences.append(f"Line {i+1}:\n  File1: {line1}\n  File2: {line2}\n")
    
    if differences:
        print("Differences found:")
        for diff in differences:
            print(diff)
    else:
        print("The files match exactly.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python compare_outputs.py <file1> <file2>")
        sys.exit(1)
    
    compare_files(sys.argv[1], sys.argv[2])
