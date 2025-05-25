from scripts.fallback import fallback

@fallback
def initialization():
    from editor import Editor
    return Editor()

editor = initialization()
editor.loop()
editor.exit()
