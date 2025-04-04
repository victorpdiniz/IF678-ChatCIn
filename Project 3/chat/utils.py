def parse_command(msg):
    parts = msg.strip().split()
    cmd = parts[0]
    args = parts[1:]
    return cmd, args