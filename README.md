# Podcast Publisher

## Feed generator package installation

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
host="$(local-ip)" port=8080 make run-feed-generator
```
