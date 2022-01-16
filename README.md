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

