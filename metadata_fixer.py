import os
import re
import subprocess
import shutil
import sys

def clean_title(filename):
    # Remove YouTube ID in square brackets and file extension
    clean_name = re.sub(r'\[[a-zA-Z0-9_-]+\]\.m4a$', '', filename)
    
    # Clean up additional text patterns
    clean_name = clean_name.replace('(Official Audio)', '').replace('(Audio)', '')
    clean_name = clean_name.replace('(Official Video)', '').replace('(Official Music Video)', '')
    clean_name = clean_name.replace('(Live)', '').strip()
    
    return clean_name

def extract_artist_and_title(filename, default_artist=None):
    clean_name = clean_title(filename)
    
    # Common artist patterns
    if 'Tyler Childers' in clean_name:
        artist = 'Tyler Childers'
        # Remove artist name from title
        title = clean_name.replace('Tyler Childers - ', '').replace('Tyler Childers and ', '').strip()
        # Handle special cases where the title contains the artist name again
        if 'Tyler Childers' in title:
            title = re.sub(r'\s*Tyler Childers\s*', '', title)
            title = re.sub(r'\(Unreleased\)', '', title).strip()
        if title.startswith('and '):
            title = title[4:].strip()  # Remove leading "and "
        if 'the Food Stamps' in title.lower():
            title = re.sub(r'(?i)the Food Stamps\s*-\s*', '', title)
        if 'Senora May' in title:
            artist = 'Tyler Childers & Senora May'
            title = re.sub(r'Senora May\s*-?\s*', '', title).strip()
            title = re.sub(r'Senora May\s+', '', title).strip()
    elif 'Blaze Foley' in clean_name:
        artist = 'Blaze Foley'
        title = clean_name.replace('Blaze Foley - ', '').replace('Blaze Foley ', '').strip()
    else:
        # If no artist detected, use the default artist if provided
        artist = default_artist if default_artist else "Unknown Artist"
        title = clean_name
    
    # Clean up quotes, extra spaces, and special characters
    title = title.strip('\'\"').strip()
    title = re.sub(r'\s+', ' ', title)
    title = title.replace('⧸', '/').replace('＂', '"').replace('｜', '|')
    
    # Further clean up titles that might have unwanted patterns
    title = re.sub(r'^\s*-\s*', '', title)  # Remove leading dash
    title = re.sub(r'\s+-\s*$', '', title)  # Remove trailing dash
    title = re.sub(r'-\s*$', '', title)  # Remove trailing dash without space
    
    # Special case cleanups
    if title == "| OurVinyl Sessions":
        title = "OurVinyl Sessions"
    
    # Remove trailing hyphen from "Her and The Banks-" and similar
    title = re.sub(r'-+\s*$', '', title)
    
    # Final trim
    title = title.strip()
    
    return artist, title

def update_metadata_and_rename(old_filename, default_artist=None, dry_run=False):
    if not old_filename.endswith('.m4a') or os.path.isdir(old_filename):
        return
    
    try:
        artist, title = extract_artist_and_title(old_filename, default_artist)
        
        # Create a new clean filename
        new_filename = f"{artist} - {title}.m4a"
        new_filename = new_filename.replace('/', '_').replace(':', '-')  # Replace any problematic characters
        
        print(f"Processing: {old_filename}")
        print(f"  → Artist: {artist}")
        print(f"  → Title: {title}")
        print(f"  → New filename: {new_filename}")
        
        if dry_run:
            print("  → DRY RUN: No changes made")
            return
        
        # Create a temporary file for the metadata update
        temp_file = f"temp_{os.path.basename(old_filename)}"
        
        # Use ffmpeg to update the metadata
        cmd = [
            'ffmpeg', '-i', old_filename, 
            '-c', 'copy',  # Copy the content without re-encoding
            '-metadata', f'title={title}', 
            '-metadata', f'artist={artist}',
            '-y',  # Overwrite output file if it exists
            temp_file
        ]
        
        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error updating metadata: {result.stderr}")
            return
        
        # Move the temp file to the new filename
        shutil.move(temp_file, new_filename)
        
        # Remove the original file if the new one exists and is not the same
        if os.path.exists(new_filename) and old_filename != new_filename:
            os.remove(old_filename)
            
        print(f"Successfully processed: {new_filename}")
        
    except Exception as e:
        print(f"Error processing {old_filename}: {e}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Update metadata and rename audio files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--file', type=str, help='Process a single file (for testing)')
    parser.add_argument('--default-artist', type=str, help='Default artist name for files without artist in filename')
    args = parser.parse_args()
    
    default_artist = args.default_artist
    
    if args.file:
        # Process just one file
        if not os.path.exists(args.file):
            print(f"Error: File '{args.file}' not found")
            return
        
        print(f"Processing single file: {args.file}")
        update_metadata_and_rename(args.file, default_artist, dry_run=args.dry_run)
        return
    
    # Get all m4a files in the current directory
    files = [f for f in os.listdir('.') if f.endswith('.m4a') and os.path.isfile(f)]
    
    print(f"Found {len(files)} .m4a files to process.")
    
    # Ask for default artist if not provided
    if not default_artist:
        print("Some files don't have an artist name in their filename.")
        use_default = input("Would you like to set a default artist for these files? (y/n): ")
        if use_default.lower() == 'y':
            default_artist = input("Enter default artist name (e.g., Tyler Childers): ").strip()
    
    if not args.dry_run:
        # Ask for confirmation
        confirm = input(f"This will update metadata and rename {len(files)} files. Continue? (y/n): ")
        if confirm.lower() != 'y':
            print("Operation cancelled.")
            return
    
    # Process each file
    for i, filename in enumerate(files, 1):
        print(f"\nProcessing file {i} of {len(files)}")
        update_metadata_and_rename(filename, default_artist, dry_run=args.dry_run)
    
    print("\nAll files processed!")

if __name__ == "__main__":
    main()
