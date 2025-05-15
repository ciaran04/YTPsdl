import os

def download_audio(url, playlist=False, start=None, end=None):
    command = f'yt-dlp -x --audio-format m4a'
    
    if playlist and start is not None:
        command += f' --playlist-start {start}'
        
    if playlist and end is not None:
        command += f' --playlist-end {end}'
    
    command += f' "{url}"'
    print(f"Running command: {command}")
    os.system(command)

def main():
    # Prompt the user for the YouTube URL
    url = input("Enter the YouTube video or playlist URL: ")

    # Check if the URL is a playlist
    is_playlist = 'playlist' in url or input("Is this a playlist (y/n)? ").lower() == 'y'
    
    if is_playlist:
        use_range = input("Do you want to download a specific range of videos from the playlist (y/n)? ").lower() == 'y'
        
        if use_range:
            start = int(input("Enter the starting video number: "))
            end = int(input("Enter the ending video number: "))
            download_audio(url, playlist=True, start=start, end=end)
        else:
            # Download the entire playlist
            download_audio(url, playlist=True)
    else:
        download_audio(url)

if __name__ == "__main__":
    main()





