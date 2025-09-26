"""Alternative methods to generate PNG from the Mermaid diagram."""

import os
import subprocess
import webbrowser
from pathlib import Path


def create_html_viewer(mermaid_file: str = "swiss_legal_agent_workflow.mmd") -> str:
    """
    Create an HTML file to view the Mermaid diagram in a browser.
    
    Args:
        mermaid_file: Path to the .mmd file
        
    Returns:
        Path to the created HTML file
    """
    if not os.path.exists(mermaid_file):
        print(f"❌ Mermaid file not found: {mermaid_file}")
        return None
    
    # Read the Mermaid content
    with open(mermaid_file, 'r', encoding='utf-8') as f:
        mermaid_content = f.read()
    
    # Create HTML with Mermaid.js
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Swiss Legal Analysis Agent - Workflow Diagram</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }}
        #diagram {{
            text-align: center;
            margin: 20px 0;
        }}
        .info {{
            background-color: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
        }}
        .info h3 {{
            margin-top: 0;
            color: #1976d2;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🇨🇭 Swiss Legal Analysis Agent - Workflow Diagram</h1>
        
        <div id="diagram">
            <div class="mermaid">
{mermaid_content}
            </div>
        </div>
        
        <div class="info">
            <h3>📊 Workflow Summary</h3>
            <ul>
                <li><strong>Start</strong> → <strong>Ingest</strong>: Normalize input and initialize memory</li>
                <li><strong>Ingest</strong> → <strong>Categorize</strong>: Classify case into legal category</li>
                <li><strong>Categorize</strong> → <strong>Win Likelihood</strong>: ReAct analysis (if not 'Andere')</li>
                <li><strong>Categorize</strong> → <strong>Aggregate</strong>: Direct path for 'Andere' category</li>
                <li><strong>Win Likelihood</strong> → <strong>Time & Cost</strong>: Business logic estimation</li>
                <li><strong>Time & Cost</strong> → <strong>Aggregate</strong>: Validate and format results</li>
                <li><strong>Aggregate</strong> → <strong>End</strong>: Return final JSON output</li>
            </ul>
            
            <h3>🏷️ Legal Categories</h3>
            <ul>
                <li><strong>Arbeitsrecht</strong>: Employment law cases</li>
                <li><strong>Immobilienrecht</strong>: Real estate law cases</li>
                <li><strong>Strafverkehrsrecht</strong>: Traffic criminal law cases</li>
                <li><strong>Andere</strong>: Other legal matters (classification only)</li>
            </ul>
        </div>
    </div>

    <script>
        mermaid.initialize({{ 
            startOnLoad: true,
            theme: 'default',
            flowchart: {{
                curve: 'linear',
                padding: 20
            }}
        }});
    </script>
</body>
</html>
"""
    
    # Save HTML file
    html_file = mermaid_file.replace('.mmd', '.html')
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML viewer created: {html_file}")
    return html_file


def try_mermaid_cli(mermaid_file: str = "swiss_legal_agent_workflow.mmd") -> bool:
    """
    Try to use Mermaid CLI to generate PNG (if installed).
    
    Args:
        mermaid_file: Path to the .mmd file
        
    Returns:
        True if successful, False otherwise
    """
    if not os.path.exists(mermaid_file):
        print(f"❌ Mermaid file not found: {mermaid_file}")
        return False
    
    try:
        # Check if Mermaid CLI is available
        result = subprocess.run(['mmdc', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Mermaid CLI (mmdc) not found")
            print("💡 Install with: npm install -g @mermaid-js/mermaid-cli")
            return False
        
        print("✓ Mermaid CLI found")
        
        # Generate PNG
        png_file = mermaid_file.replace('.mmd', '.png')
        cmd = ['mmdc', '-i', mermaid_file, '-o', png_file, '-b', 'white']
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ PNG generated using Mermaid CLI: {png_file}")
            return True
        else:
            print(f"❌ Mermaid CLI failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ Mermaid CLI not found")
        print("💡 Install with: npm install -g @mermaid-js/mermaid-cli")
        return False


def print_viewing_options(mermaid_file: str = "swiss_legal_agent_workflow.mmd"):
    """Print all available options for viewing the diagram."""
    
    print("\\n📊 Mermaid Diagram Generated Successfully!")
    print("=" * 50)
    print(f"📁 File: {mermaid_file}")
    print(f"📍 Location: {os.path.abspath(mermaid_file)}")
    
    print("\\n🎨 Viewing Options:")
    print("\\n1. 🌐 Online Viewer:")
    print("   • Go to: https://mermaid.live/")
    print(f"   • Copy and paste the content from {mermaid_file}")
    print("   • Download as PNG/SVG from the website")
    
    print("\\n2. 🔧 VS Code:")
    print("   • Install 'Mermaid Preview' extension")
    print(f"   • Open {mermaid_file} in VS Code")
    print("   • Right-click → 'Open Preview'")
    
    print("\\n3. 🖥️ Local HTML Viewer:")
    html_file = create_html_viewer(mermaid_file)
    if html_file:
        print(f"   • Open {html_file} in your browser")
        print("   • Right-click on diagram → 'Save image as...'")
    
    print("\\n4. 📱 Mermaid CLI (if available):")
    success = try_mermaid_cli(mermaid_file)
    if not success:
        print("   • Install: npm install -g @mermaid-js/mermaid-cli")
        print("   • Then run: mmdc -i swiss_legal_agent_workflow.mmd -o workflow.png")
    
    print("\\n5. 🐙 GitHub/GitLab:")
    print("   • Upload .mmd file to GitHub/GitLab repository")
    print("   • View directly in the web interface")
    print("   • GitHub renders Mermaid diagrams automatically")


if __name__ == "__main__":
    mermaid_file = "swiss_legal_agent_workflow.mmd"
    
    if os.path.exists(mermaid_file):
        print_viewing_options(mermaid_file)
        
        # Optionally open HTML viewer
        html_file = mermaid_file.replace('.mmd', '.html')
        if os.path.exists(html_file):
            try:
                print(f"\\n🚀 Opening {html_file} in browser...")
                webbrowser.open(f"file://{os.path.abspath(html_file)}")
            except Exception as e:
                print(f"Could not open browser: {e}")
    else:
        print(f"❌ Mermaid file not found: {mermaid_file}")
        print("💡 Run generate_png.py first to create the diagram")