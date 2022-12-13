def contains(fieldname: list[str], content: str) -> bool:
    return any(content in string for string in fieldname)

def equal_to(fieldname: list[str], content: str) -> bool:
    return content in fieldname #exact equal to
