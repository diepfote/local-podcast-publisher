# Podcast Publisher

Makes Podcasts available/downloadable on the local network.
Particularly useful if no-one officially published it to a podcasting platform.

In other words it is a RSS generator.

## How it works

* nginx to hosts files and reports metadata such as content-length to the generation script (gistfile1.py)
* gistfile1.py shells out to ffprobe helpers to fetch description, publishing date
* itunes extensions category, author and explicit tag are hardcoded

Thus, the container needs a host mount and needs to have access to the same data
the ffprobe helpers need to have access to.

To generate rss feeds for multiple podcasts you need to call gistfile1.py several times
while the container is running.

Well. This sounds clunky but it works.

### Alternative 

I was recently looking for a simpler alternative (a single binary specifically) and 
came across a rust project called [localhost-podcast](https://sr.ht/~j_wernick/localhost-podcast/).
It works quiet well as it is but it is missing:

* an index.html that lists your podcasts
* the ability to bind a specific ipv4 interface
* metadata extraction for date and description

It's hosted on SourceHut which is why I will not be "forking" it or repushing the
the code to my account.
My changes are submitted although one of them seems to be held up by a email filter.
Maybe because it's the largest change.

TL;DR I created a gist for it and will be archiving this project.

[Gist](https://gist.github.com/diepfote/59aaf5eb8ea3e2d7bcdd97b8efd2a472)


## Feed generator package installation

### Dependencies

* ffmpeg
* python 3 (tested on 3.9 and above)
* python libraries (installed via `Makefile` [command](https://github.com/diepfote/local-podcast-publisher/blob/35964a5faf979fdfcac88453f497b230c0535fee/Makefile#L19))
* [`gistfile1.py`](https://github.com/diepfote/local-podcast-publisher/blob/e39278cdb17020d1dc616537316289ad45fd4563/gistfile1.py) contains references to custom written `ffmpeg` and `ffprobe`
[scripts](https://github.com/diepfote/scripts/tree/8611a9d9a6cf6b29d47b5175d1ae594f36991651/bin).

### Install

```
make install
```


## Run

Open two terminal panes (to check traffic on file server)

1st pane:
```
make run-file-server
```

2nd pane:
```
host=<local-ip> port=8080 title='TGS Podcast' dir_to_expose='tgs_podcast'  make run-feed-generator
```

## Acccess

```
# test
curl <local-ip>:8080/TGS%20Podcast.xml
```

Enter the url above into the Apple Podcast app.  
Your podcast will now appear as `subscribed`.  
For as long as your `<local-ip>` stays the same,
you can use this podcast feed to make episodes
available offline.


## Automate ssh port-forward

```text
cd bin
go build port-forward-80-linux.go  -o port-forward-80
sudo chown root:root port-forward-80
sudo chmod u+s port-forward-80
```

## Expose all videos instead of podcasts

**Note**: Very specific to my setup (FS layout).

```text
$ cat ~/Movies/Makefile
SHELL := bash

.PHONY: run-file-server
run-file-server:
    ./.bin/serve-files.sh

$ cat ~/Movies/.bin/serve-files.sh
#!/usr/bin/env bash

set -x

cleanup () {
  cd audio-only && git checkout -- bin/run-file-server.sh
  set +x
}
trap cleanup EXIT

# shellcheck disable=SC2016
sed -i 's#"$PWD"/etc/nginx/conf.d#"$PWD"/audio-only/etc/nginx/conf.d#' audio-only/bin/run-file-server.sh

./audio-only/bin/run-file-server.sh

$ cd ~/Movies && make
```


## Notes on Mac OS

* Make sure to allow full disk access for `/opt/homebrew/bin/bash`, `Alacritty.app`, `/bin/bash` and `/bin/zsh`.
* Also be sure to (since Sequoia) allow `Local Network` access to `Alacritty.app` (we have to run it without `tmux` in plain `Alacritty` otherwise we will not be able to forward ports on this Mac OS version).

