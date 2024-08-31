import requests, random, cv2, time
from moviepy.editor import *
import os
import google.auth
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class motivationBot:
    def __init__(self):
        self.tags = [
            "motivation",
            "inspiration",
            "success",
            "selfimprovement",
            "positivity"
        ]



        self.quote = ""
        self.author = ""
        self.responseJson = []
        self.numNewLines = 0
        # Scopes needed for accessing YouTube API
        self.SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
        
        return
    
    def run(self):
        #first motivational request
        self.startingIntervalTime = time.time()
        self.getMotivationalQuote()
        self.numQuotesUsedInInterval = 1
        self.getRandomBackgroundVideo()
        self.addMusicToVideo()
        self.convert_to_vertical('final_video.mp4', 'final_video_vertical.mp4')
        self.authenticate_youtube()
        self.uploadVideoToYoutube()

    def getMotivationalQuote(self):
        #get motivational quote
        response = requests.get("https://zenquotes.io/api/random")
        self.responseJson = response.json()
        self.quote = self.insert_newlines(self.responseJson[0]["q"])
        self.author = self.responseJson[0]["a"]
        print("Quote: " + self.quote)
        print("Author: " + self.author)
    
    def getRandomBackgroundVideo(self):
        randomVideoNum = random.randint(0, 17)
        video_path = "backgrounds/" + str(randomVideoNum) + ".mp4"
        print("path: " + video_path)
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Could not open video file {video_path}")
            return None
        else:
            print(f"Opened video file {video_path} successfully")
            self.addQuoteToBackground(cap)

    def insert_newlines(self, text, max_line_length=65):
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            # Check if adding the next word would exceed the max length
            if len(current_line) + len(word) + 1 <= max_line_length:
                # Add the word to the current line
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
            else:
                # If the current line is full, add it to the list of lines
                lines.append(current_line)
                # Start a new line with the current word
                current_line = word
        
        # Add the last line to the list
        if current_line:
            lines.append(current_line)

        # Join the lines with newline characters
        self.numNewLines = len(lines)
        return '\n'.join(lines)
        
    def addMusicToVideo(self, video_path = "quoted_video.mp4", outputPath = 'final_video.mp4'):
        print("adding music to video")
        video = VideoFileClip(video_path)
        randomAudioNum = random.randint(0, 7)
        audio_path = "music/" + str(randomAudioNum) + ".mp3"
        audio = AudioFileClip(audio_path).subclip(0, video.duration)  # Ensures the audio matches the video length
        video_with_audio = video.set_audio(audio)
        video_with_audio.write_videofile(outputPath, codec='libx264', audio_codec='aac')


    def addQuoteToBackground(self, cap):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec
        out = cv2.VideoWriter('quoted_video.mp4', fourcc, 30.0, (int(cap.get(3)), int(cap.get(4))))
        frameCount = 0
        quoteIndex = 0
        line_height = 50
        while cap.isOpened():
            ret, frame = cap.read()
            frameCount += 1
            font = cv2.FONT_HERSHEY_COMPLEX
            #place new quote about every 5 seconds (about every 200 frames)
            if(frameCount == 200):
                frameCount = 0
                quoteIndex += 1
                print("200 frames passed putting new quote")
                self.numNewLines = 0
                #check if within limit
                if(self.numQuotesUsedInInterval < 5 and (time.time() - self.startingIntervalTime < 30)):
                    self.getMotivationalQuote()
                    self.numQuotesUsedInInterval += 1
                else:
                    print("Limit reached waiting for next availability")
                    remainingTime = 30 - (time.time() - self.startingIntervalTime)
                    if remainingTime > 0:
                        time.sleep(remainingTime + 1)
                    self.startingIntervalTime = time.time()
                    self.getMotivationalQuote
                    self.numQuotesUsedInInterval = 1
            if not ret:
                break

            # Split the quote into lines
            lines = self.quote.split('\n')
            
            # Render each line on the video
            for i, line in enumerate(lines):
                y_position = 500 + i * line_height
                # Draw the outline
                cv2.putText(
                    frame, 
                    line, 
                    (100, y_position), 
                    font, 1, 
                    (0, 0, 0), 3,  # Black color, thickness 3 for the outline
                    cv2.LINE_AA
                )
                # Draw the main text on top
                cv2.putText(
                    frame, 
                    line, 
                    (100, y_position), 
                    font, 1, 
                    (255, 255, 255), 2,  # White color, thickness 2 for the main text
                    cv2.LINE_AA
                )
            
            # Place the author of the quote below the last line with an outline
            author_y_position = 500 + len(lines) * line_height
            # Draw the outline for the author
            cv2.putText(
                frame, 
                "- " + self.author, 
                (100, author_y_position), 
                font, 1, 
                (0, 0, 0), 3,  # Black color, thickness 3 for the outline
                cv2.LINE_AA
            )
            # Draw the main text for the author
            cv2.putText(
                frame, 
                "- " + self.author, 
                (100, author_y_position), 
                font, 1, 
                (255, 255, 255), 2,  # White color, thickness 2 for the main text
                cv2.LINE_AA
            )
            
            out.write(frame)

        print("Added quote and author to video")
        out.release()
        cv2.destroyAllWindows()

    def convert_to_vertical(self, video_path, output_path, target_height=1920):
        print("converting to vertical")
        # Open the original video
        cap = cv2.VideoCapture(video_path)
        
        # Get original dimensions
        original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        # Calculate target width for 9:16 aspect ratio
        target_width = int(target_height * 9 / 16)
        
        # Prepare the output video writer with the target resolution
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or try 'XVID' or 'avc1'
        out = cv2.VideoWriter(output_path, fourcc, fps, (target_width, target_height))
        
        if not out.isOpened():
            print("Error: VideoWriter not opened correctly")
            return
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Calculate the scaling factors to resize the frame
            width_scale = target_width / original_width
            height_scale = target_height / original_height

            # Use the smaller scaling factor to ensure the whole image fits
            scale_factor = min(width_scale, height_scale)

            # Calculate the new size after scaling
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)

            # Resize the frame to the new dimensions
            resized_frame = cv2.resize(frame, (new_width, new_height))

            # Calculate padding to center the resized frame
            pad_x = (target_width - new_width) // 2
            pad_y = (target_height - new_height) // 2

            # Apply padding to make the resized frame fit the target dimensions
            final_frame = cv2.copyMakeBorder(
                resized_frame, 
                pad_y, pad_y,  # Top and bottom padding
                pad_x, pad_x,  # Left and right padding
                cv2.BORDER_CONSTANT, 
                value=[0, 0, 0]  # Black padding
            )

            # Ensure the final frame has the exact target dimensions
            final_frame = cv2.resize(final_frame, (target_width, target_height))

            # Write the processed frame to the output video
            out.write(final_frame)
        
        # Release everything when done
        cap.release()
        out.release()

        # Confirm the file was written successfully
        print(f"Video saved to {output_path}")


    def authenticate_youtube(self):
        """Authenticate and return a YouTube service object."""
        creds = None
        # Token file to store the user's access and refresh tokens
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)
        # If no valid credentials, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        
        self.youtube = build("youtube", "v3", credentials=creds)
        return self.youtube
    
    def uploadVideoToYoutube(self):
        print("uploading to YouTube.")
        request_body = {
            "snippet": {
                "title": "Motivational Quotes",
                "description": "This is a channel of daily motivational quotes to help brighten your day! Make sure to like and subscribe if you enjoy!",
                "tags": self.tags,
                "categoryId": 22  # 22 corresponds to 'People & Blogs'
            },
            "status": {
                "privacyStatus": "public",  # Set to "private" or "unlisted" if needed
            },
        }

        media = MediaFileUpload('final_video_vertical.mp4')

        response_upload = self.youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=media
        ).execute()

        print(f"Video uploaded. Video ID: {response_upload['id']}")
        return response_upload
    
bot = motivationBot()
bot.run()