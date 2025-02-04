# Podcast Publisher


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
