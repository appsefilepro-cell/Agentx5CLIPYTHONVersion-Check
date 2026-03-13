import os
import subprocess
import sys
import tempfile

def print_help():
    print("AgentX5 CLI Terminal")
    print("Commands:")
    print("  /bash <cmd>  - Run a shell command")
    print("  /python      - Enter multiline Python mode (type /end on a new line to execute)")
    print("  /help        - Show this help message")
    print("  /clear       - Clear the terminal screen")
    print("  /exit        - Exit the CLI")
    print()

def run_bash(cmd):
    try:
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
    except Exception as e:
        print(f"Error executing bash: {e}")

def run_python_multiline():
    print("Enter Python code. Type '/end' on a new line to finish and execute.")
    lines = []
    while True:
        try:
            line = input(">>> ")
            if line.strip() == "/end":
                break
            lines.append(line)
        except EOFError:
            break
        except KeyboardInterrupt:
            print("^C")
            return

    code = "\n".join(lines)
    if not code.strip():
        return

    # Execute the code in a temporary file to keep it clean and allow importing local modules
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name

    try:
        print("\n--- Output ---")
        result = subprocess.run([sys.executable, temp_file], text=True, capture_output=True)
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        print("--------------\n")
    except Exception as e:
        print(f"Error executing python: {e}")
    finally:
        os.remove(temp_file)

def main():
    print_help()
    while True:
        try:
            cmd = input("AgentX5> ").strip()
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nType /exit to quit")
            continue

        if not cmd:
            continue

        if cmd == "/exit":
            print("Exiting...")
            break
        elif cmd == "/help":
            print_help()
        elif cmd == "/clear":
            os.system('clear' if os.name == 'posix' else 'cls')
        elif cmd.startswith("/bash "):
            run_bash(cmd[6:])
        elif cmd == "/python":
            run_python_multiline()
        else:
            # Default to bash if not a special command, or show error?
            # Let's default to bash for convenience if it's a known bash command, but to be safe, 
            # we can just treat anything else as a bash command.
            if cmd.startswith("/"):
                print(f"Unknown command: {cmd}")
            else:
                run_bash(cmd)

if __name__ == "__main__":
    main()
