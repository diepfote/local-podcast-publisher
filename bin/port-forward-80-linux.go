package main

import "os/exec"

// $ go build port-forward-80.go
// $ sudo chown root:root port-forward-80
// $ sudo chmod u+s port-forward-80

func main() {
	cmd := exec.Command("ssh", "-o", "StrictHostKeychecking=no", "-NT", "-i", "/home/flo/.ssh/podman-remote", "-L", "frame:80:localhost:10080", "flo@localhost")
	cmd.Start()

	cmd.Wait()
}
