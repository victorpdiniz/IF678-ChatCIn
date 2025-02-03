class Publisher:
    
    def msgToTxt(fileName: str, file: str) -> None:
        localFile = open(fileName, 'x')
        if not localFile:
            print(f"Server: Couldn't create {fileName}.")
            raise ValueError

        localFile.write(file)
        localFile.close()
    
    def msgToPdf(fileName: str, file: bytes) -> None:
        try:
            with open(fileName, 'xb') as localFile:
                localFile.write(file)
        except FileExistsError:
            print(f"Server: O arquivo '{fileName}' já existe.")
            raise
    
    def msgToMp3(fileName: str, file: bytes) -> None:
        try:
            with open(fileName, 'xb') as localFile:
                localFile.write(file)
        except FileExistsError:
            print(f"Server: O arquivo '{fileName}' já existe.")
            raise
        
    def msgToMp4(fileName: str, file: bytes) -> None:
        try:
            with open(fileName, 'xb') as localFile:
                localFile.write(file)
        except FileExistsError:
            print(f"Server: O arquivo '{fileName}' já existe.")
            raise
    
    def msgToPng(fileName: str, file: bytes) -> None:
        try:
            with open(fileName, 'xb') as localFile:
                localFile.write(file)
        except FileExistsError:
            print(f"Server: O arquivo '{fileName}' já existe.")
            raise


    def msgToJpeg(fileName: str, file: bytes) -> None:
        try:
            with open(fileName, 'xb') as localFile:
                localFile.write(file)
        except FileExistsError:
            print(f"Server: O arquivo '{fileName}' já existe.")
            raise

       