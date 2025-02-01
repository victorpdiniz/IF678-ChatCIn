from utils.Interpreter import Interpreter
from utils.Publisher import Publisher

class FileManager:
    
    def defineType(fileName: str) -> str:
        if fileName.endswith('.txt'):
            return 'txt'
        elif fileName.endswith('.pdf'):
            return 'pdf'
        elif fileName.endswith('.mp3'):
            return 'mp3'
        elif fileName.endswith('.mp4'):
            return 'mp4'
        elif fileName.endswith('.png'):
            return 'png'
        elif fileName.endswith('.jpeg'):
            return 'jpeg'
        else:
            raise ValueError
    
    def actFile(fileName: str, action: str, file: any = None) -> any:
        type = FileManager.defineType(fileName)
        fileName = 'files/' + fileName
        
        if action == 'get':
            if type == 'txt':
                return Interpreter.txtToMsg(fileName)
            elif type == 'pdf':
                return Interpreter.pdfToMsg(fileName)
            elif type == 'mp3':
                pass
            elif type == 'mp4':
                pass
            elif type == 'png':
                return Interpreter.pngToMsg(fileName)
            elif type == 'jpeg':
                return Interpreter.jpegToMsg(fileName)
            
        elif action == 'post':
            if type == 'txt':
                return Publisher.msgToTxt(fileName, file)
            elif type == 'pdf':
                return Publisher.msgToPdf(fileName,file)
            elif type == 'mp3':
                pass
            elif type == 'mp4':
                pass
            elif type == 'png':
                return Publisher.msgToPng(fileName,file)
            elif type == 'jpeg':
                return Publisher.msgToJpeg(fileName, file)
        
            
