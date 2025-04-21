import subprocess
import os
import sys

# Paths
GEPI_JAR = "gephi-toolkit-0.9.2-all.jar"
JAVA_FILES = ["GephiScript.java", "CommunityColor.java"]
CLASS_FILES = ["GephiScript.class", "CommunityColor.class"]

def compile_java():
    print("[INFO] Compiling Java source files...")
    try:
        subprocess.run(
            ["javac", "-cp", GEPI_JAR] + JAVA_FILES,
            check=True
        )
        print("[SUCCESS] Compilation complete.")
    except subprocess.CalledProcessError as e:
        print("[ERROR] Compilation failed.")
        sys.exit(1)

def run_gephi_toolkit(input_path, output_path):
    print(f"[INFO] Running Gephi Toolkit on {input_path}")
    try:
        subprocess.run(
            ["java", "-cp", f".:{GEPI_JAR}", "GephiScript", input_path, output_path],
            check=True
        )
        print(f"[SUCCESS] Exported processed graph to {output_path}")
    except subprocess.CalledProcessError as e:
        print("[ERROR] Java execution failed.")
        sys.exit(1)

def main():
    # Compile only if class files are missing
    if not all(os.path.exists(f) for f in CLASS_FILES):
        compile_java()

    FILES = ['../graph/graph.graphml', '../graph/condensed_graph.graphml', '../graph/co_citation_graph.graphml']

    for file in FILES:
        run_gephi_toolkit(file, file)


if __name__ == "__main__":
    main()