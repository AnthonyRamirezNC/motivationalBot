import requests, random, cv2, time
from moviepy.editor import *
class motivationBot:
    def __init__(self):
        self.quote = ""
        self.author = ""
        self.responseJson = []
        self.numNewLines = 0
        return
    
    def start(self):
        #first motivational request
        self.startingIntervalTime = time.time()
        self.getMotivationalQuote()
        self.numQuotesUsedInInterval = 1
        self.getRandomBackgroundVideo()
        self.addMusicToVideo()

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

    
    def uploadVideoToYoutube():
        return
    
bot = motivationBot()
bot.start()