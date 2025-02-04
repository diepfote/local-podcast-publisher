package main

import (
	"fmt"
	"os"
	"os/exec"
)

// $ go build port-forward-80.go
// $ sudo chown root:root port-forward-80
// $ sudo chmod u+s port-forward-80

func main() {
	if len(os.Args) < 3 {
		fmt.Println("Please provide at least two arguments")
		return
	}

	idFile := os.Args[1]
	port := os.Args[2]

	cmd := exec.Command("ssh", "-o", "StrictHostKeychecking=no", "-NT", "-i", idFile, "-p", port, "-L", "podcast-svc-org:80:localhost:10080", "lima@localhost")
	fmt.Printf("port: %s, id_file: %s\n", port, idFile)
	cmd.Start()

	cmd.Wait()

	// // DEBUGGING from here on out:
	// // ...
	// // ...
	// // ...
	// // ...
	// // ...

	// // Prepare buffers to capture output
	// var out bytes.Buffer
	// var stderr bytes.Buffer
	// cmd.Stdout = &out
	// cmd.Stderr = &stderr

	// // Run the command
	// err := cmd.Run()

	// // Check for errors
	// if err != nil {
	// 	// If there's an error, log it and print stderr output
	// 	log.Fatalf("cmd.Run() failed with %s\nStderr: %s", err, stderr.String())
	// }

	// // Print the output of the command
	// fmt.Printf("Output:\n%s\n", out.String())

	// // Get exit status
	// if exitError, ok := err.(*exec.ExitError); ok {
	// 	// The command exited with an error, get the exit code
	// 	fmt.Printf("Exit Status: %d\n", exitError.ExitCode())
	// } else {
	// 	// The command was successful
	// 	fmt.Println("Exit Status: 0 (success)")
	// }
}
