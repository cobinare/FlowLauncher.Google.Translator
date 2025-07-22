import subprocess

# TODO: Replace direct cmd call with some library (like `pyperclip`), since
# TODO: current implementation is vulnerable and can't contain some characters.
def copy_to_clipboard(text: str) -> bool:
    """
    Put text in clipboard.
    
    Returns `False` if:
    - an error occured;
    - text contains any of these special characters: `^&|><%!"()`.
    
    Otherwise returns `True` on success.
    """
    special_chars = ['^', '&', '|', '>', '<', '%', '!', '"', '(', ')']
    cmd = f'cmd /c "echo|set /p={text}"| clip'
    if any(char in text for char in special_chars):
        return False
    try:
        subprocess.check_call(cmd, shell=True)
        return True
    except:
        return False
