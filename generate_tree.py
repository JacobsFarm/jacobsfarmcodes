import os

# --- CONFIGURATIE ---
BASE_PATH = r"."    # Verander dit naar je doelmap, bijv. "./src" of "C:/Projects/App"
FANCY_MODE = True  # True voor iconen, False voor strakke Industry Standard
MAX_DEPTH = 2      # Hoe diep de boom moet gaan
EXCLUDE = {'.git', 'node_modules', '__pycache__', '.venv', 'dist', '.DS_Store', '.vscode'}

def get_icon(is_dir, name):
    if not FANCY_MODE:
        return ""
    if is_dir:
        return "📂 "
    
    # Bestandspecifieke iconen
    file_icons = {
        '.py': "🐍 ", '.js': "📜 ", '.ts': "📘 ", 
        '.html': "🌐 ", '.css': "🎨 ", '.md': "📝 ",
        '.json': "⚙️ ", '.env': "🔑 ", 'docker': "🐋 ",
        'LICENSE': "⚖️ ", '.png': "🖼️ ", '.jpg': "🖼️ "
    }
    
    for ext, icon in file_icons.items():
        if name.lower().endswith(ext) or name.lower() == ext.strip('.'):
            return icon
    return "📄 "

def generate_tree(current_path, depth=0):
    if depth > MAX_DEPTH:
        return ""

    output = ""
    try:
        items = os.listdir(current_path)
    except PermissionError:
        return ""

    # Sorteren: mappen eerst, dan bestanden (alfabetisch)
    items.sort(key=lambda x: (not os.path.isdir(os.path.join(current_path, x)), x.lower()))

    # Filter de items die we willen negeren
    filtered_items = [item for item in items if item not in EXCLUDE]

    for i, item in enumerate(filtered_items):
        path = os.path.join(current_path, item)
        is_last = (i == len(filtered_items) - 1)
        
        # Teken de boom-structuur symbolen
        connector = "└── " if is_last else "├── "
        prefix = "    " * depth
        
        icon = get_icon(os.path.isdir(path), item)
        output += f"{prefix}{connector}{icon}{item}\n"
        
        if os.path.isdir(path):
            output += generate_tree(path, depth + 1)
            
    return output

if __name__ == "__main__":
    # Haal de naam van de startmap op voor de top van de boom
    root_name = os.path.basename(os.path.abspath(BASE_PATH))
    print(f"```text\n{root_name}/")
    print(generate_tree(BASE_PATH))
    print("```")
