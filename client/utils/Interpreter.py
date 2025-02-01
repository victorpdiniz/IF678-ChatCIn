class Interpreter:
    
    def txtToMsg(fileName: str) -> bytes:
        with open(fileName, 'r') as localFile:
            data = localFile.read()
        data=data.encode() # Garante que é bytes
        return data
    
    def pdfToMsg(fileName: str) -> bytes:
        with open(fileName, 'rb') as imageFile:
            data = imageFile.read()
        return data
    def mp3ToMsg() -> str:
        pass
    
    def mp4ToMsg() -> str:
        pass
    
    def pngToMsg(fileName: str) -> bytes:
        with open(fileName, 'rb') as imageFile:
            data = imageFile.read()
        return data
    
    def jpegToMsg(fileName: str) -> bytes:
        with open(fileName, 'rb') as imageFile:
            data = imageFile.read()
        return data
