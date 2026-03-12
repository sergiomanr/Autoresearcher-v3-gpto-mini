import os
import subprocess
import re
import sys
import time

def get_current_commit():
    """Returns the current git commit hash to allow safe rollbacks."""
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip().decode('utf-8')
    except subprocess.CalledProcessError:
        print("[!] Error: Not a git repository. Please run 'git init' and commit your initial files.")
        sys.exit(1)

def run_evaluation():
    """Runs evaluate.py and extracts the CV RMSE."""
    print("[+] Running evaluation...")
    result = subprocess.run(['python', 'evaluate.py'], capture_output=True, text=True)
    output = result.stdout
    
    # Check if there was a crash in Python
    if result.returncode != 0 or "Crash during preprocessing" in output or "Error" in output:
        print("[!] Evaluation crashed.")
        print(result.stderr if result.stderr else output)
        return None
        
    match = re.search(r"cv_rmse:\s+([0-9.]+)", output)
    if match:
        return float(match.group(1))
    
    print("[!] Could not parse cv_rmse from output.")
    print(output)
    return None

def main():
    print("=== Starting Auto-Researcher ===")
    
    # Pre-flight check: Ensure OpenAI API key is set for GPT-4o Mini
    if not os.environ.get("OPENAI_API_KEY"):
        print("[!] ERROR: OPENAI_API_KEY environment variable is not set.")
        print("Please set it in your terminal before running: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)
    
    # 1. Establish Baseline
    print("\n--- Establishing Baseline ---")
    best_rmse = run_evaluation()
    
    if best_rmse is None:
        print("Fatal: Baseline evaluation failed. Please fix preprocess.py or evaluate.py manually before starting.")
        sys.exit(1)
        
    print(f"Baseline CV RMSE: {best_rmse}")
    
    iteration = 1
    
    # 2. The Infinite Loop
    while True:
        print(f"\n=== Iteration {iteration} ===")
        
        # Save state before Aider touches anything
        safe_commit = get_current_commit()
        
        # Formulate the prompt for Aider
        prompt = (
            "Act as an expert Data Scientist and Kaggle Grandmaster. "
            "Read program_1.md and deeply analyze data_dictionary.md. "
            "CRITICAL: Read 'failed_experiments.txt' to see what ideas have already been tried and rejected. DO NOT repeat them. "
            "Read 'exito.txt' to see what ideas were successful. "
            "Implement ONE sophisticated new feature in preprocess.py to lower the RMSE. "
            "I WANT you to experiment with categorical columns! Use advanced techniques like "
            "target encoding, frequency encoding, one-hot encoding or grouped aggregations of individual levels found in data_dictionary.md. "
            "EXAMPLE OF EXPECTED COMPLEXITY: Don't just one-hot encode. Create multi-variable interactions. For instance, create an "
            "'Age-Adjusted Foundation Premium' by target-encoding 'Foundation', multiplying it by 'Total_Bsmt_SF' (size), and applying "
            "a mathematical decay penalty based on 'Year_Built' (age). "
            "CRITICAL RULES: "
            "1. NO DATA LEAKAGE: If you use Target Encoding or aggregations based on 'Sale_Price', you MUST use a global "
            "`_SAVED_MAPPINGS = {}` dictionary at the top of the file. Only learn/calculate the target statistics when "
            "(`is_train = 'Sale_Price' in df.columns`), and then `.map()` those saved statistics back to the dataframe. "
            "2. Do not drop the target column ('Sale_Price'). "
            "3. MODERN PANDAS SYNTAX ONLY: NEVER use `inplace=True` (e.g., no `df[col].fillna(val, inplace=True)`). "
            "Instead, always use assignment: `df[col] = df[col].fillna(val)`. "
            "If creating many new columns, avoid DataFrame fragmentation by assigning them via a dictionary and using `pd.concat`, "
            "or use `df = df.copy()` to de-fragment before returning. "
            "4. Because the model cannot accept strings, before returning your dataframe you MUST drop all remaining object/category columns. "
            "Always end your function with: `return df.select_dtypes(include=['number', 'bool'])`."
        )
        
        # Run Aider via subprocess
        print("[+] Waking up Aider (GPT-5.1 Codex Mini)...")
        aider_cmd = [
            "aider", 
            "--model", "gpt-5.1-codex-mini",               # Updated to use the OpenAI API model
            "--yes",                                # Auto-accept changes
            "--message", prompt,
            "--read", "failed_experiments.txt",
            "--read", "exito.txt",
            "--read", "program_1.md",               # System instructions
            "--read", "data_dictionary.md",         # Feature ideas
            "--read", "evaluate.py",                # Read-only context
            "preprocess.py"                         # The ONLY file it edits
        ]
        
        # We let Aider print to standard output so you can watch it think in the terminal
        subprocess.run(aider_cmd)
        
        # Grab Aider's automated commit message to see what change it actually made
        # We do this BEFORE evaluating so we know what to log
        commit_msg_process = subprocess.run(['git', 'log', '-1', '--pretty=%B'], capture_output=True, text=True)
        change_description = commit_msg_process.stdout.strip()
        
        # Evaluate Aider's work
        current_rmse = run_evaluation()
        
        if current_rmse is None:
            print(f"[x] Code crashed. Logging failure and reverting to {safe_commit[:7]}...")
            with open('failed_experiments.txt', 'a') as f:
                f.write(f"CRASHED IDEA:\n{change_description}\n{'='*30}\n")
            subprocess.run(['git', 'reset', '--hard', safe_commit], capture_output=True)
            
        elif current_rmse < best_rmse:
            print(f"[✓] SUCCESS! RMSE improved from {best_rmse} to {current_rmse}.")
            
            # Log the success to exito.txt / results
            with open('exito.txt', 'a') as f:
                f.write(f"--- Iteration {iteration} ---\n")
                f.write(f"RMSE Improved: {best_rmse:.6f} -> {current_rmse:.6f}\n")
                f.write(f"Change:\n{change_description}\n")
                f.write("-" * 40 + "\n\n")
                
            best_rmse = current_rmse
            # Aider automatically commits on success, so we just leave it and move to the next iteration.
            
        else:
            print(f"[-] Score got worse or didn't improve (Current: {current_rmse} | Best: {best_rmse}).")
            with open('failed_experiments.txt', 'a') as f:
                f.write(f"FAILED IDEA (Worse RMSE: {current_rmse}):\n{change_description}\n{'='*30}\n")
                print("Failed idea included into failed_experiment")
            
            print(f"Logging failure and reverting to {safe_commit[:7]}...")
            
            # Log the failed idea so the AI doesn't try it again
            
                
            subprocess.run(['git', 'reset', '--hard', safe_commit], capture_output=True)
            
        iteration += 1
        
        # Optional: slight pause so you can cancel (Ctrl+C) if it's going off the rails
        time.sleep(2)

if __name__ == "__main__":
    # Create necessary text files if they don't exist
    if not os.path.exists('failed_experiments.txt'):
        open('failed_experiments.txt', 'w').close()
    if not os.path.exists('exito.txt'):
        open('exito.txt', 'w').close()

    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[+] Auto-Researcher stopped by user. Exiting gracefully.")
        sys.exit(0)