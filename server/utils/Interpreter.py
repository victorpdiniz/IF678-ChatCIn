class Interpreter:
    
    def txtToMsg(fileName: str) -> bytes:
        with open(fileName, 'r') as localFile:
            data = localFile.read()
        data = data.encode() # Garante que é bytes
        return data
    
    def pdfToMsg(fileName: str) -> bytes:
        with open(fileName, 'rb') as imageFile:
            data = imageFile.read()
        return data
    def mp3ToMsg(fileName: str)-> bytes:
        with open(fileName, 'rb') as imageFile:
            data = imageFile.read()
        return data
    
    def mp4ToMsg(fileName: str)-> bytes:
        with open(fileName, 'rb') as imageFile:
            data = imageFile.read()
        return data
    
    def pngToMsg(fileName: str) -> bytes:
        with open(fileName, 'rb') as imageFile:
            data = imageFile.read()
        return data
    
    def jpegToMsg(fileName: str) -> bytes:
        with open(fileName, 'rb') as imageFile:
            data = imageFile.read()
        return data
