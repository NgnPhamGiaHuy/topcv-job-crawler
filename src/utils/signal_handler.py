import signal

should_exit = False


def signal_handler(signum, frame) -> None:
    global should_exit
    print(f"\nReceived signal {signum}. Exiting gracefully...")
    should_exit = True

def setup_signal_handlers() -> None:
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def get_exit_flag() -> bool:
    return should_exit