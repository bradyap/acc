from pytube import YouTube

def download_youtube_video(url, save_path='.'):
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

        if stream:
            print(f"Downloading: {yt.title}...")
            stream.download(output_path=save_path)
            print(f"Downloaded '{yt.title}' successfully to {save_path}")
        else:
            print("No suitable progressive stream found for this video.")

    except Exception as e:
        print(f"An error occurred: {e}")

video_url = input("Enter the YouTube video URL: ")
download_youtube_video(video_url)        


