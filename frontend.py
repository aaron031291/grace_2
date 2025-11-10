
import subprocess
import sys

def main():
    """Main entry point for the Grace frontend."""
    
    while True:
        print("\n" + "="*70)
        print("  GRACE - Main Menu")
        print("="*70 + "\n")
        print("1. Start Chat")
        print("2. System Status")
        print("3. Exit")
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "1":
            start_chat()
        elif choice == "2":
            show_status()
        elif choice == "3":
            print("\nGoodbye!\n")
            break
        else:
            print("\nInvalid choice. Please try again.")

def start_chat():
    """Starts the Grace chat interface."""
    
    try:
        subprocess.run([sys.executable, "chat_with_grace.py"])
    except FileNotFoundError:
        print("\nError: chat_with_grace.py not found.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

def show_status():
    """Shows the Grace system status."""
    
    try:
        subprocess.run([sys.executable, "-m", "backend.main", "status"])
    except FileNotFoundError:
        print("\nError: backend.main not found.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
