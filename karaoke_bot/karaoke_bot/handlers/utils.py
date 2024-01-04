def format_subscribers_count(count: int) -> str:
    if count < 1000:
        return str(count)
    elif count < 10**6:
        suffix = "K"
        int_part, dec_part = divmod(count, 10**3)
        if count < 10**4:
            dec_part //= 10
        elif count < 10**5:
            dec_part //= 10**2
        else:
            dec_part //= 10**3
    else:
        suffix = "M"
        int_part, dec_part = divmod(count, 10 ** 6)
        dec_part //= 10 ** 4

    dec_part = str(dec_part).rstrip('0')
    if dec_part:
        return f"{int_part}.{dec_part}{suffix}"
    return f"{int_part}{suffix}"