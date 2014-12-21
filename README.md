1-second-everyday
=================

A script to process one second memory links as described in http://www.ted.com/talks/cesar_kuriyama_one_second_every_day.html. Using ffmpeg (https://www.ffmpeg.org/), it concatenates videos of one second length into one full video. Each video is stamped with the recording date and can be modified with a configuration file "videos.txt". An example videos.txt file explaining the commands is included in the repository. The individual steps that are performed are:

1. Take all files from the working directory and move them into the 'full' folder
2. Apply the modifiers from the "video.txt" for each video and store the intermediate result in the "intermediate" folder
3. Add the date stamping and store the result in the "text" folder
4. Block videos in groups of 50 seconds and store blocked videos in the "block" folder
5. Concatenate all blocks together to form the full video as "1se.mp4"

ffmpeg has to be in the path so that it can be called using a Python system command.
