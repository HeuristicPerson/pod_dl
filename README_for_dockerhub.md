![](https://raw.githubusercontent.com/HeuristicPerson/pod_dl/v1.x.dev/images/logo-grey_and_green.png)

# Pod DL docker image #

## >>> First the most important thing <<< ##

You can invite me to a **[☕ Ko-Fi](https://ko-fi.com/zipzop)**. It'll warm my heart for at least 10 minutes... which is much more than nothing!


## Introduction ##

"Pod DL" (Podcast Downloader) is a docker image containing "Pod DL" script to automatically download the latest episodes
of your podcast subscriptions. To follow the development of the container, notify bugs, and make improvement suggestions
please go to [github](https://github.com/HeuristicPerson/pod_dl/).


## Configuration options ## 

### Environment variables ###

* `UID` User ID of the user downloading and owning the episodes.
* `GID` Group ID of the user downloading and owning the episodes.
* `CRON_HOURS` Frequency in hours when Pod DL will attempt to fetch new episodes. Valid values are 1, 2, 3, 4, 6, 8, 12, and 24. First sync will always happen at 0:00 hours.
* `POD_DL_DEBUG` yes/no. When active, Pod DL logs will be more verbose. It's recommended to set debug to yes when ceating or testing a new configuration. After everything works as intended, you can set debug to
  "no" to have a nicer looking log.
* `POD_DL_MAX_SYNC` Maximum number of episodes to download on each synchronization. So, for example: if set to 3 any
  subscription to a new podcast will download the last 3 episodes available.
* `POD_DL_MAX_ARCH` Maximum number of episodes to keep in the archive directory. When the download of new episodes is
  completed, the old ones will be removed so the maximum number of episodes stored is maintained. If you set it to 0,
  no episodes will be deleted ever.
* `POD_DL_TRANSC_SERV` yes/no. Set it to yes if you want downloaded episodes to be converted to `.ogg`.
* `POD_DL_TRANSC_FORC` yes/no. When set to yes, the transcoded files will be kept, no matter if they are bigger than
  the original files or even valid. When set to no, the smallest and valid file will be kept, which is the recommended
  value.
* `POD_DL_TRANSC_FREQ` Frequency of the transcoded files, 44100 is the frequency of an audio CD, and 22050 is a
  reasonable value for common podcasts.
* `POD_DL_TRANSC_BITR` Bitrate of the transcoded `.ogg` files. 96-128 should give you reasonable audio quality at
  small file size.
* `POD_DL_SCR_CMD` Script to be executed after the download and transcoding of each episode. The script must be typed
  as a list of single-quoted "words", separated by commas and enclosed by parenthesis. Some tags with information
  about the downloaded episodes are available:

  * `%pod_name%` The name of the podcast
  * `%ep_title%` The title of the episode
  * `%ep_hsize%` The human size of the episode (e.g. "48 MiB")
  * `%ep_isize%` The size of the episode in bytes
  * `%ep_durat%` The duration of the episode in HH:MM:SS format (NOT VALID BY NOW, IT WILL ALWAYS BE 00:00:00
  * `%ep_path%` The full path of the archived episode (e.g. "/home/john/my_pods/episode.ogg")

* `POD_DL_SCR_MSG` Message to be printed in the logs when the script is executed. Read
  [pod_dl documentation](pod_dl/README.md) to know more.
* `TZ` Timezone of your location so files and logs will have the right time.


### Volumes ###

Pod DL will archive podcasts at `/podcasts` directory, and you can map or bind that to any location in your docker host.


### Podcast subscriptions ###

Pod DL will read your subscriptions from the file `/podcasts/subs.txt`. Add each of your subscriptions in a new line
with the format below:

    podcast_tile;podcast_feed_url

For example:

    a quemarropa;https://www.ivoox.com/feed_fg_f1175617_filtro_1.xml
    deknet;https://www.spreaker.com/show/1432098/episodes/feed
    freak n films;https://www.ivoox.com/freak-n-films_fg_f1786649_filtro_1.xml
    metodologic podcast;https://www.ivoox.com/feed_fg_f1284079_filtro_1.xml

Pod DL is able to download audio files from Youtube channels as if they were
regular podcasts. You only need to specify the URL of the channel RSS like in
the example below:

    my youtube channel; https://www.youtube.com/feeds/videos.xml?channel_id=VCRciVcT7tffYNFmDj2AmnkQ

You'll need to replace 'VCRciVcT7tffYNFmDj2AmnkQ' by the proper id of the
channel you're interested in. In the web browser, open the Youtube channel and
press Ctrl-U to see the source code of the page. Search
`https://www.youtube.com/channel/` and there you'll see the channel id.


## Sample Docker Compose file ##

Sample compose file including a post-download script that sends a notification to a simple event logger (not included)
in the docker image.

    version: "2.1"
    services:
      pod_dl:
        image: zipzop/pod_dl:v1.0
        container_name: pod_dl_production
        network_mode: bridge
        environment:
          - UID=1000
          - GID=1000
          - CRON_HOURS=2
          - POD_DL_DEBUG=no
          - POD_DL_MAX_SYNC=5
          - POD_DL_MAX_ARCH=10
          - POD_DL_TRANSC_SERV=yes
          - POD_DL_TRANSC_FORC=no
          - POD_DL_TRANSC_FREQ=22050
          - POD_DL_TRANSC_BITR=96
          - POD_DL_SCR_CMD=('curl', '-d', 'from=pod_dl&level=info&msg=Downloaded %pod_name% > %ep_title%', '-X', 'POST', 'http://mother.lan/log')
          - POD_DL_SCR_MSG=Log sent to MU/TH/UR 6000
          - TZ=Europe/Madrid
        volumes:
          - /docker_data/pod_dl/my_podcasts:/podcasts
        restart: "unless-stopped"

## Sample output of the log ##

Timestamps on each line are not shown for clarity, but you can easily activate them with `-t` option
in docker (`docker logs -t CONTAINER_ID`) or from portainer GUI.

    ##############################################################
    #                ______      _____                           #
    #               / _  (_)_ __/ _  / ___  _ __                 #
    #               \// /| | '_ \// / / _ \| '_ \                #
    #                / //\ | |_) / //\ (_) | |_) |               #
    #               /____/_| .__/____/\___/| .__/                #
    #                      |_|             |_|                   #
    ##############################################################
    
    Starting zipzop/pod_dl:v1.0 2021-09-23
    ==============================================================
    - muerte tenia un podcast, la
        - Downloading 5 latest episode(s) since 2021-09-03 07:30:00+02:00
        - [1/1] 2021-09-24 INICIATIVA BOND #25: Skyfall (2012)... DONE! (55.1 MiB)
        - Fixing ID3 tags... DONE!
        - Transcoding to .ogg at 22050 Hz and 96 kbps DONE! (62.5 MiB)
        - Keeping original file DONE!
        - Moving file to archive location... DONE!
        - Log sent to MU/TH/UR 6000... DONE!
    - a quemarropa
        - Downloading 5 latest episode(s) since 2021-09-10 13:00:00+02:00
        - [1/1] 2021-09-24 A Quemarropa FlixOlé (9): Fernando Colomo... DONE! (26.6 MiB)
            - Fixing ID3 tags... DONE!
            - Transcoding to .ogg at 22050 Hz and 96 kbps DONE! (29.2 MiB)
            - Keeping original file DONE!
            - Moving file to archive location... DONE!
            - Log sent to MU/TH/UR 6000... DONE!
    - deknet
        - Downloading 5 latest episode(s) since 2021-09-23 05:00:16+00:00
        - [1/1] 2021-09-25 CROSSOVER con REFLEX Podcast: Mochila 72 horas para volcanes y apagones... DONE! (34.1 MiB)
            - Fixing ID3 tags... DONE!
            - Transcoding to .ogg at 22050 Hz and 96 kbps DONE! (0.0 B)
            - Keeping original file DONE!
            - Moving file to archive location... DONE!
            - Log sent to MU/TH/UR 6000... DONE!