# phonefmt.py
def port_to_number(port: int, base_port: int = 7000,
                   npa: int = 716, nxx: int = 555, start_suffix: int = 1200) -> str:
    """
    Example: port 7004 -> 716-555-1204  (if base_port=7000, start_suffix=1200)
    """
    offset = port - base_port
    last4 = start_suffix + offset
    return f"{npa:03d}-{nxx:03d}-{last4:04d}"
