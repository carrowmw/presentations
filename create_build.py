# conceptual_build_script.py
import os
import shutil
from bs4 import BeautifulSoup
import re
import argparse

# --- Configuration ---
# Attributes to check for local file paths
ATTRS_TO_CHECK = {
    'link': 'href',    # CSS
    'script': 'src',   # JS
    'img': 'src',      # Images
    'source': 'src',   # For <video>/<audio> <source> tags
    'video': 'poster', # Poster images for videos
    'iframe': 'src',   # Local HTML iframes
    'section': 'data-background-image', # Reveal.js background images
    # Add other tags/attributes if your presentations use them for assets
}

# --- Helper Functions ---

def get_asset_path(base_dir, asset_url, current_file_path):
    """
    Resolves the absolute path of an asset.
    Handles relative paths from the current file or root-relative paths.
    """
    if not asset_url or asset_url.startswith(('http:', 'https:', 'data:', '//')):
        return None # External or data URI

    # If asset_url starts with '/', it's relative to base_dir (project root)
    # Otherwise, it's relative to the directory of current_file_path
    if asset_url.startswith('/'):
        abs_path = os.path.join(base_dir, asset_url.lstrip('/'))
    else:
        current_dir = os.path.dirname(current_file_path)
        abs_path = os.path.normpath(os.path.join(current_dir, asset_url))

    return abs_path

def copy_asset(src_abs_path, base_input_dir, output_dir):
    """
    Copies an asset to the output directory, maintaining relative structure.
    Returns the new relative path for the asset in the build.
    """
    if not os.path.exists(src_abs_path):
        print(f"Warning: Asset not found: {src_abs_path}")
        return None

    # Determine relative path from the base_input_dir to the asset
    # This relative path will be recreated in the output_dir
    rel_path = os.path.relpath(src_abs_path, base_input_dir)
    dest_abs_path = os.path.join(output_dir, rel_path)

    os.makedirs(os.path.dirname(dest_abs_path), exist_ok=True)
    shutil.copy2(src_abs_path, dest_abs_path)
    print(f"Copied: {src_abs_path} -> {dest_abs_path}")
    return rel_path # This is the path to use in the modified HTML

def process_css_file(css_abs_path, base_input_dir, output_dir):
    """
    Parses a CSS file for url(...) assets and copies them.
    Note: This is a simplified CSS parser. For complex cases, it might need enhancement.
    It doesn't rewrite paths within CSS files in this simplified version,
    but assumes relative paths will work if structure is maintained.
    """
    if not os.path.exists(css_abs_path):
        return

    print(f"Processing CSS file: {css_abs_path}")
    css_dir = os.path.dirname(css_abs_path)

    try:
        with open(css_abs_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Warning: Could not read CSS file {css_abs_path}: {e}")
        return

    # Regex to find url(...) patterns. This is basic and might need refinement.
    # It tries to capture unquoted, single-quoted, and double-quoted URLs.
    # It explicitly excludes data URIs.
    matches = re.findall(r'url\((?!["\']?data:)["\']?([^)"\']+)["\']?\)', content)

    for asset_url in matches:
        asset_url = asset_url.strip() # Clean up whitespace
        if not asset_url or asset_url.startswith(('http:', 'https:', '//')): # External
            continue

        # Resolve path relative to the CSS file itself
        asset_abs_path = os.path.normpath(os.path.join(css_dir, asset_url))

        # Check if this asset is within the base_input_dir to avoid copying system files
        if os.path.commonpath([asset_abs_path, base_input_dir]) == base_input_dir:
            copied_rel_path = copy_asset(asset_abs_path, base_input_dir, output_dir)
            # For a full solution, you'd also rewrite the URL in the copied CSS file
            # if its relative path changes significantly, or use absolute paths in build.
            # This example assumes simple relative paths like '../fonts' will be maintained.
        else:
            print(f"Warning: CSS asset path {asset_abs_path} is outside project base. Skipping.")


def process_html_file(html_file_path, base_input_dir, output_dir):
    """
    Processes a single HTML file: copies its assets and the file itself.
    This function would be called recursively for HTML iframes.
    """
    if not os.path.exists(html_file_path):
        print(f"Error: HTML file not found: {html_file_path}")
        return

    print(f"Processing HTML file: {html_file_path}")

    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
    except Exception as e:
        print(f"Warning: Could not parse HTML file {html_file_path}: {e}")
        return


    # Copy assets linked in the HTML
    for tag_name, attr_name in ATTRS_TO_CHECK.items():
        for tag in soup.find_all(tag_name):
            asset_url = tag.get(attr_name)
            if asset_url:
                asset_abs_path = get_asset_path(base_input_dir, asset_url, html_file_path)
                if asset_abs_path:
                    # Check if this asset is within the base_input_dir
                    if os.path.commonpath([asset_abs_path, base_input_dir]) == base_input_dir:
                        copied_rel_path = copy_asset(asset_abs_path, base_input_dir, output_dir)

                        # If it's a CSS file, process it for more assets (like fonts)
                        if copied_rel_path and copied_rel_path.lower().endswith('.css'):
                            process_css_file(os.path.join(output_dir, copied_rel_path), base_input_dir, output_dir)

                        # If it's a local HTML iframe, process it recursively
                        # Note: This would require careful handling of base paths and output paths for recursion
                        # and potentially rewriting the src attribute in the copied parent HTML.
                        # For simplicity, this example just copies it. A full recursive solution is more complex.
                        if tag_name == 'iframe' and copied_rel_path and copied_rel_path.lower().endswith(('.html', '.htm')):
                            # Simplistic copy; recursive processing is more involved
                            # process_html_file(asset_abs_path, base_input_dir, output_dir) # This needs refinement for recursion
                            pass
                    else:
                         print(f"Warning: HTML asset path {asset_abs_path} is outside project base. Skipping.")


    # Copy the HTML file itself
    html_rel_path = os.path.relpath(html_file_path, base_input_dir)
    dest_html_path = os.path.join(output_dir, html_rel_path)
    os.makedirs(os.path.dirname(dest_html_path), exist_ok=True)
    shutil.copy2(html_file_path, dest_html_path)
    print(f"Copied HTML: {html_file_path} -> {dest_html_path}")


# --- Main Script Logic ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a minimal build for a Reveal.js presentation.")
    parser.add_argument("input_html", help="Path to the main HTML file of the presentation.")
    parser.add_argument("output_dir", help="Directory to store the minimal build.")
    # parser.add_argument("--download-cdn", action="store_true", help="Download CDN assets locally (not implemented in this example).")

    args = parser.parse_args()

    input_html_file = os.path.abspath(args.input_html)
    # Assume the project root is the directory containing the input HTML file's parent,
    # or adjust as needed if your assets (like a global 'dist' or 'plugin' folder) are higher up.
    # For this example, let's assume the input_html_file is in the root of your project structure for THIS presentation.
    # If your 'dist', 'plugin', 'css', 'images' folders are siblings to where your presentation HTMLs are,
    # then base_input_dir should be the parent of your input_html_file.
    # If index.html is at project_root/index.html, then base_input_dir = project_root
    # If index.html is at project_root/presentations/my_pres/index.html, and 'dist' is at project_root/dist,
    # then base_input_dir = os.path.abspath(os.path.join(os.path.dirname(input_html_file), '../../')) # Adjust as needed

    # A common setup: your presentation HTML is in the root of its own asset collection.
    # Or, if you have one BIG common folder for all assets, the base_input_dir is that common folder.
    # Let's assume the script is run from the root of the BIG project folder,
    # and input_html is like 'presentations_folder/my_pres.html'
    # For your case, your index.html seems to be in the root of where 'dist', 'plugin', 'css', 'images' are.
    base_input_dir = os.path.abspath(os.path.dirname(input_html_file)) # Assuming assets are relative to the HTML's dir or in subdirs
    # If assets like 'dist/' are in the parent of where index.html is, adjust this.
    # Given your paths like 'dist/reveal.css', it's likely index.html is in the main project root.
    # So base_input_dir should be the directory containing index.html, dist/, plugin/, etc.
    # If script is in project_root and you run: python script.py index.html build_output
    # then base_input_dir = os.getcwd() or specifically os.path.dirname(os.path.abspath(args.input_html)) if html is in root.

    output_build_dir = os.path.abspath(args.output_dir)

    if os.path.exists(output_build_dir):
        # Basic cleanup: remove if exists. Be careful with this in production scripts!
        print(f"Output directory {output_build_dir} exists. Removing it.")
        shutil.rmtree(output_build_dir)
    os.makedirs(output_build_dir)

    print(f"Project base directory identified as: {base_input_dir}")
    process_html_file(input_html_file, base_input_dir, output_build_dir)

    print("\nMinimal build process complete.")
    print(f"Presentation exported to: {output_build_dir}")