class Publisher:
    
    def msgToTxt(fileName: str, file: str) -> None:
        localFile = open(fileName, 'x')

        if not localFile:
            print(f"Server: Couldn't create {fileName}.")
            raise ValueError

        localFile.write(file)
        localFile.close()
    
    def msgToPdf(fileName: str, file: str) -> None:
        pass
    
    def msgToMp3(fileName: str, file: str) -> None:
        pass
        
    def msgToMp4(fileName: str, file: str) -> None:
        pass
    
    def msgToPng(fileName: str, file: str) -> None:
        pass
    
    def msgToJpeg(fileName: str, file: str) -> None:
        pass
       