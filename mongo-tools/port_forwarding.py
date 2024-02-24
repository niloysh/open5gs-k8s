import subprocess
import time
from logger import log

NAMESPACE = "open5gs"


def run_with_port_forwarding(script):
    """
    Port forward the MongoDB service so the host can access it.
    """
    try:
        port_forward_command = [
            "kubectl",
            "port-forward",
            "service/mongodb",
            "-n",
            NAMESPACE,
            "27017:27017",
        ]
        port_forward_process = subprocess.Popen(port_forward_command, stdout=subprocess.DEVNULL)
        time.sleep(5)

        script()  # business logic

    except subprocess.CalledProcessError as e:
        # Handle any errors that occur during port forwarding
        log.warning(f"Error occurred during port forwarding: {e}")

    finally:
        if port_forward_process.poll() is None:
            # If the process is still running, terminate it
            port_forward_process.terminate()
            port_forward_process.wait()
