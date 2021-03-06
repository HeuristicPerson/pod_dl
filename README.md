# Pod DL docker image #

## Introduction ##

"Pod DL" (Podcast Downloader) is a docker image containing "Pod DL" script to
automatically download the latest episodes of your podcast subscriptions.

To get the already built docker image, please go to
[hub.docker.com/r/zipzop/pod_dl](https://hub.docker.com/r/zipzop/pod_dl) or, if
you just want to get the downloader script, please download folder
[pod_dl](https://github.com/HeuristicPerson/pod_dl/tree/v1.0/pod_dl) and
checkout [README.md](https://github.com/HeuristicPerson/pod_dl/blob/v1.0/pod_dl/README.md)
in it.


## Configuration options ## 

### Environment variables ###

  * `UID` User ID of the user downloading and owning the episodes.
  * `GID` Group ID of the user downloading and owning the episodes.
  * `CRON_HOURS` Frequency in hours when Pod DL will attempt to fetch new episodes. Valid values are 1, 2, 3, 4, 6, 8,
                 12, and 24. First sync will always happen at 0:00 hours. 
  * `POD_DL_DEBUG` yes/no. When active, Pod DL logs will be more verbose. It's recommended to set debug to yes when
                   creating or testing a new configuration. After everything works as intended, you can set debug to
                   "no" to have a nicer looking log.
  * `POD_DL_MAX_SYNC` Maximum number of episodes to download on each synchronization. So, for example: if set to 3 any
                      subscription to a new podcast will download the last 3 episodes available.
  * `POD_DL_MAX_ARCH` Maximum number of episodes to keep in the archive directory. When the download of new episodes is
                      completed, the old ones will be removed so the maximum number of episodes stored is maintained. If
                      you set it to 0, no episodes will be deleted ever.
  * `POD_DL_TRANSC_SERV` yes/no. Set it to yes if you want downloaded episodes to be converted to `.ogg`.
  * `POD_DL_TRANSC_FORC` yes/no. When set to yes, the transcoded files will be kept, no matter if they are bigger than
                         the original files or even valid. When set to no, the smallest and valid file will be kept,
                         which is the recommended value.
  * `POD_DL_TRANSC_FREQ` Frequency of the transcoded files, 44100 is the frequency of an audio CD, and 22050 is a
                         reasonable value for common podcasts.
  * `POD_DL_TRANSC_BITR` Bitrate of the transcoded `.ogg` files. 96-128 should give you reasonable audio quality at
                         small file size.
  * `POD_DL_SCR_CMD` Script to be executed after the download and transcoding of each episode. The script must be
                     typed as a list of single-quoted "words", separated by commas and enclosed by parenthesis. Some
                     tags with information about the downloaded episodes are available. Read
                     [pod_dl documentation](pod_dl/README.md) to know more.
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
channel you're interested in. In the web broswer, open the Youtube channel and
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
