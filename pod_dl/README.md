# Pod DL program #

## Introduction ##

"Pod DL" (Podcast Downloader) is a Python 3 script to automatically download the latest episodes of a list of podcast
feeds (your subscriptions) included in a `subs.txt` file.

## Configuration using `pod_dl.ini` ##

You can configure "Pod DL" to suit your needs by editing the file `pod_dl.ini`. Available options and their meaning are:


### Section `[main]` ###
    
  * `debug` yes/no. In debug mode, the program will be more verbose. It's recommended to create and test your
               configuration with debug mode activated; once you're sure everything works fine, deactivate debug mode. 
  * `tmp_dir` Directory for temporary episode downloads. Once the episodes are completed and post-processed, they
                 will be moved to the archive directory. In Linux, it's a good idea to set your temporary directory as
                 `/tmp`.
  * `arc_dir` Archive directory, the final destination of your episodes. The program will create a new folder inside
               this directory for each podcast.
  * `max_sync` Maximum number of episodes to be downloaded on each execution of the program. For example, when you
                first execute the downloader for a new podcast subscription, instead of all episodes available in the
                feed, only the number of episodes indicated by `max_sync` will be downloaded. If you set this option to
                zero, all available episodes will be downloaded.
  * `max_arch` The maximum number of episodes to store in the archive directory. The cleaning of old episodes will
                happen everytime you run the downloader. By setting it to 0, you can keep all the episodes you download.


### Section `[transcode]` ###

  * `active` yes/no. When active, downloaded episodes will be converted to `.ogg` format.
  * `force` yes/no. When active, `.mp3` episodes will be discarded and the transcoded `.ogg` will be kept. When set
             to `no`, the *smallest* file will be kept, no matter if it's the `.mp3`, or the `.ogg`. Conversion of
             `.mp3` files to `.ogg` is not very robust and can produce invalid files; for that reason, setting `force`
             to `yes` *is not recommended*. 
  * `frequency` Frequency in Hz of the transcoded `.ogg` file. For reference 44100 is CD audio quality; 22050 should
                 produce reasonable good quality for regular podcast episodes.
  * `bitrate` Bitrate of the transcoded file in kbps (kilobits per second). 96-128 should be fine for regular
               podcasts.


### Section `[post_script]` ###

This section will define a script that will be executed after the downloading (and transcoding) of each episode. You can
send information of the current episode to your script by using the following tags:
     
  * `%pod_name%` The name of the podcast
  * `%ep_title%` The title of the episode
  * `%ep_hsize%` The human size of the episode (e.g. "48 MBi")
  * `%ep_isize%` The size of the episode in bytes
  * `%ep_durat%` The duration of the episode in HH:MM:SS format (NOT VALID BY NOW, IT WILL ALWAYS BE 00:00:00
  * `%ep_path%` The full path of the archived episode (e.g. "/home/john/my_pods/episode.ogg")

The two available options in `[post_script]` section are:

  * `command` Script to be executed with all possible arguments. Type each chunk (or word) of the command between
                single quotes, joined by commas, and enclosed by parenthesis. e.g. To save the name of the podcast to a
                file you would do `echo "%ep_title%" >> /tmp/log.txt`, so in the command files you should put `('echo',
                '"%ep_title%"', '>>', '/tmp/log.txt')`

  * `message` Message to be printed by the program to indicate the post script was run. You can directly type your
              string create your string. e.g. `"This will appear in the program output"`


## Configuration using environment variables ##

All configuration options available in `pod_dl.ini` are also available as environment variables but under a different
name. Below you can see the correspondence between them. We won't explain again their meaning so please read the section
about `pod_dl.ini` to know more about them.

  * `POD_DL_DEBUG` → `debug`
  * `POD_DL_TEMP` → `tmp_dir`
  * `POD_DL_ARCH` → `arc_dir`
  * `POD_DL_MAX_SYNC` → `max_sync`
  * `POD_DL_MAX_ARCH` → `max_arch`
  * `POD_DL_TRANSC_SERV` → `active`
  * `POD_DL_TRANSC_FORC` → `force`
  * `POD_DL_TRANSC_FREQ` → `frequency`
  * `POD_DL_TRANSC_BITR` → `bitrate`
  * `POD_DL_SCR_CMD` → `command`
  * `POD_DL_SCR_MSG` → `message`


## TODO ##

  * [ ] Make sure downloader continues working fine if an episode download is interrupted
  * [ ] Retry episode downloads if anything fails
  * [ ] Check transcoding errors with ffmpeg. Why do they happen? any way of preventing them?
  * [ ] Launch two different scripts depending on whether an episode downloaded correctly or not
