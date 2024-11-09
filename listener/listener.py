def listen_for_enter(stop_thread, running_flag):
    global running
    while not stop_thread():
        input("Press Enter to toggle start/stop...")
        # Toggle the global `running` variable
        running = not running  # Update the global `running` flag
        print(f"'running' is now set to: {running}")