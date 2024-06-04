# A simple text editor built to learn/test my knowledge of the Command Design Pattern 
# Takes both keyboard input AND a simple web API via Flask

from abc import ABC, abstractmethod 
from flask import Flask, jsonify, request 
import threading

class Command(ABC):
    @abstractmethod 
    def execute(self):
        pass

    def undo(self):
        pass

class TextEditor:
    def __init__(self):
        self.text = ""

    def write(self, text):
        self.text += text
        print(f"Text after write: {self.text}")

    def delete(self, length):
        self.deleted_text = self.text[-length:]
        self.text = self.text[:-length]
        print(f"Text after delete: {self.text}")
    
    def append(self, text):
        self.text += text 
        print(f"Text after undo delete: {self.text}")

# Concrete Commands 
class WriteCommand(Command):
    def __init__(self, editor, text):
        self.editor = editor 
        self.text = text

    def execute(self):
        self.editor.write(self.text)

    def undo(self):
        self.editor.delete(len(self.text))
        
class DeleteCommand(Command):
    def __init__(self, editor, length: int):
        self.editor = editor 
        self.length = length 

    def execute(self):
        self.editor.delete(self.length)

    def undo(self):
        self.editor.append(self.editor.deleted_text)


# Invoker 
class CommandManager:
    def __init__(self):
        self.history = []

    def execute_command(self, command):
        command.execute()
        self.history.append(command)

    def undo(self):
        command = self.history.pop()
        command.undo()

# Flask Web API 
app = Flask(__name__)
editor = TextEditor()
manager = CommandManager() 

@app.route("/command", methods=["POST"])
def command():
    data = request.json 
    action = data.get('action') 
    if action == 'write':
        text = data.get('text')
        cmd = WriteCommand(editor, text)
        manager.execute_command(cmd)
        return jsonify({"status": "success"}), 200
    elif action == 'delete':
        try:
            length = data.get('length') 
            cmd = DeleteCommand(editor, length) 
            manager.execute_command(cmd) 
            return jsonify({"status": "success"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": "Length must be an integer"}), 400
    elif action == 'undo':
        manager.undo() 
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "error", "message": "Invalid action"}), 400

def run_flask_app():
    app.run(debug=True, use_reloader=False)

# Main Function (Keyboard Input)
def main():
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start() 

    while True:
        action = input("Enter 'write', 'delete', or 'undo': ")
        if action == 'write':
            text = input("Enter text to write: ")
            cmd = WriteCommand(editor, text)
            manager.execute_command(cmd)
        elif action == 'delete':
            try:
                length = int(input("Enter a number of characters to delete: "))
            except ValueError:
                print("Enter an integer")
                length = int(input("Enter a number of characters to delete: "))
            cmd = DeleteCommand(editor, length)
            manager.execute_command(cmd)
        elif action == 'undo':
            manager.undo()
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
