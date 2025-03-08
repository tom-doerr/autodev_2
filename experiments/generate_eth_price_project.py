import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from codeagent.code_modifier import CodeModifierAgent
except ImportError:
    try:
        # Try alternative import path
        sys.path.append('/home/tom/git/autodev_2')
        from codeagent.code_modifier import CodeModifierAgent
    except ImportError:
        print("Error: Could not import CodeModifierAgent. Make sure the codeagent package is installed.")
        sys.exit(1)

def generate_eth_price_project(output_dir):
    """Generate a complete project for displaying ETH price."""
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create the agent
    agent = CodeModifierAgent("openrouter/google/gemini-2.0-flash-001")
    
    # Project structure
    project_files = {
        "main.py": "Create the main entry point that runs the ETH price tracker application",
        "eth_price_tracker.py": "Create a module that fetches ETH price data from a public API like CoinGecko",
        "price_display.py": "Create a module that displays ETH price data using matplotlib or another visualization library",
        "data_storage.py": "Create a module that stores historical ETH price data",
        "requirements.txt": "Create a requirements.txt file with all necessary dependencies",
        "README.md": "Create a README file explaining how to use the ETH price tracker application"
    }
    
    # Generate each file
    for filename, instructions in project_files.items():
        file_path = os.path.join(output_dir, filename)
        print(f"Generating {filename}...")
        
        # Create an empty file first (needed for Rope to work with it)
        with open(file_path, 'w') as f:
            f.write("# Generated file\n")
        
        try:
            # Generate code for the file
            project_instructions = f"""
            This file is part of an ETH price tracker application. The application should:
            1. Fetch ETH price data from a public API (like CoinGecko or CryptoCompare)
            2. Display the current price and a chart of historical prices
            3. Store historical data for later analysis
            
            Specific instructions for this file:
            {instructions}
            
            Make sure the code is well-structured, includes proper error handling, and follows best practices.
            """
            
            # Use the agent to modify the file
            modified_code = agent.modify_file(file_path, project_instructions, project_path=output_dir)
            
            # Write the modified code back to the file
            with open(file_path, 'w') as f:
                f.write(modified_code)
            
            print(f"✓ Generated {filename}")
        except Exception as e:
            print(f"Error generating {filename}: {e}")

if __name__ == "__main__":
    # Create the ETH price tracker project in a new directory
    output_dir = "eth_price_tracker"
    generate_eth_price_project(output_dir)
    print(f"\nProject generated in {output_dir}/")
    print("To run the project:")
    print(f"1. cd {output_dir}")
    print(f"2. pip install -r requirements.txt")
    print(f"3. python main.py")
