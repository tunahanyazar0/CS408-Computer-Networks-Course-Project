import socket
import threading
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pickle
import time

class FileServer:
    # initializing the server socket, client threads, clients dictionary, file directory, file metadata dictionary, metadata file, and running flag
    def __init__(self):
        self.server_socket = None
        self.client_threads = []
        self.clients = {}
        self.file_directory = ""
        self.file_metadata = {}
        self.metadata_file = "file_metadata.pickle"
        self.running = False

    # GUI setup
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Server GUI")
        
        # creating the labels, entry, and buttons for the server GUI
        tk.Label(self.root, text="Port Number:").grid(row=0 ,column= 0,padx=5,pady = 5,sticky="nswe")
        self.port_entry = tk.Entry(self.root)
        self.port_entry.grid(row=1 ,column= 0,padx=5,pady = 5,sticky="nswe")
        
        # creating the buttons for selecting the file directory, starting the server, and closing the server
        tk.Button(self.root, text="Select File Directory", command=self.select_directory).grid(row=3 ,column= 0,padx=5,pady = 5,sticky="nswe")
        tk.Button(self.root, text="Start Server", command=self.start_server).grid(row=2 ,column= 0,padx=5,pady = 5,sticky="nswe")
        
        # creating the labels and listboxes for the server GUI
        self.sever_log_label = tk.Label(self.root, text="Server Log").grid(row=4 ,column= 0,padx=5,pady = 5,sticky="nswe")
        self.log_box = tk.Listbox(self.root, width=80)
        self.log_box.grid(row=5 ,column= 0,columnspan=3,padx=5,pady = 5,sticky="nswe")
        self.online_user_label = tk.Label(self.root, text="Online Users").grid(row=0 ,column= 1,padx=5,pady = 5,sticky="nswe")
        self.online_user_box = tk.Listbox(self.root, width=80)
        self.online_user_box.grid(row=1 ,rowspan=4,column= 1,padx=5,pady = 5,sticky="nswe")
        self.files_label = tk.Label(self.root, text="Files on the Server").grid(row=0 ,column= 2,padx=5,pady = 5,sticky="nswe")
        self.files_box = tk.Listbox(self.root, width=80)
        self.files_box.grid(row=1 ,rowspan=4,column= 2,padx=5,pady = 5,sticky="nswe")

        # setting the weights for the columns and rows
        self.root.grid_columnconfigure(0,weight=1)
        self.root.grid_columnconfigure(1,weight=30)
        self.root.grid_columnconfigure(2,weight=30)

        self.root.grid_rowconfigure(0,weight=1)
        self.root.grid_rowconfigure(1,weight=1)
        self.root.grid_rowconfigure(2,weight=1)
        self.root.grid_rowconfigure(3,weight=1)
        self.root.grid_rowconfigure(4,weight=1)
        self.root.grid_rowconfigure(5,weight=20)

        
        self.root.protocol("WM_DELETE_WINDOW", self.close_server)

        # Load metadata after initializing the log box
        ##self.load_metadata()

        self.root.mainloop()
    
    # synchronizing the metadata with the directory
    def sync_metadata_with_directory(self):
     try:
        # Ensure file_metadata exists
        if not hasattr(self, 'file_metadata') or not isinstance(self.file_metadata, dict):
            self.file_metadata = {}
        
        # Ensure download directory exists
        if not os.path.exists(self.file_directory):
            self.log(f"Download directory does not exist: {self.file_directory}")
            return
        
        
        # Get the set of files currently in the directory
        actual_files = set(os.listdir(self.file_directory))
        filtered_files = actual_files - {"file_metadata.pickle"}
        for x in actual_files:
            if x not in self.file_metadata.keys():
                filtered_files = filtered_files - {x}

        
        
        
        self.log(f"Files in directory: {filtered_files}")
        
            
        
        # Find metadata entries not matching actual files
        missing_files = [key for key in self.file_metadata.keys() if key not in actual_files]
        if missing_files:
            self.log(f"Missing files from metadata: {missing_files}")
        
        # Remove metadata for missing files
        for file in missing_files:
            del self.file_metadata[file]
            self.log(f"Removed metadata for file: {file}")
        
        # Save updated metadata
        self.save_metadata()
        self.log(f"Metadata synchronization complete. Remaining entries: {len(self.file_metadata)}")
    
     except Exception as e:
        self.log(f"Error during metadata synchronization: {str(e)}")

    def load_metadata(self):
     try:
        # Load metadata from the file
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, "rb") as file:
                self.file_metadata = pickle.load(file)
            self.log(f"Loaded metadata for {len(self.file_metadata)} files")
        else:
            self.file_metadata = {}
            self.log("No metadata file found; starting with an empty dictionary.")
        
        # Synchronize metadata with the directory
        self.sync_metadata_with_directory()
    
     except Exception as e:
        self.log(f"Error loading metadata: {str(e)}")
        self.file_metadata = {}

    def save_metadata(self):
        try:
            with open(self.metadata_file, "wb") as file:
                pickle.dump(self.file_metadata, file)
        except Exception as e:
            self.log(f"Error saving metadata: {str(e)}")

    def select_directory(self):
        self.file_directory = filedialog.askdirectory()
        self.log(f"Selected Directory: {self.file_directory}")


    def show_online_users(self):
        # this function is used to show the online users on the server
        while self.server_socket != None:
         time.sleep(1)
         self.online_user_box.delete(0, tk.END)
         for x in self.clients:
            self.log_to_user_box(x)

    def show_files(self):
        # this function is used to show the files on the server
        while self.server_socket != None:
            time.sleep(1)
            self.files_box.delete(0, tk.END)
            size = len(self.file_metadata)
            file_list = ""
            # we are using [^] as a separator between the files to split them later 
            for i in range(size):
                if i != size - 1:
                    file_list += f"{list(self.file_metadata.keys())[i].split('_', 1)[1]} by {list(self.file_metadata.values())[i]} [^] "
                else:
                    file_list += f"{list(self.file_metadata.keys())[i].split('_', 1)[1]} by {list(self.file_metadata.values())[i]}"
            for x in file_list.split("[^]"):
             self.log_to_file_box(x)

    # starting the server
    def start_server(self):
        if not self.file_directory:
            self.log("Please select a file directory first")
            return
        # getting the port number from the entry
        port = int(self.port_entry.get())
        self.metadata_file = os.path.join(self.file_directory,self.metadata_file)

        # starting the server socket and accepting the clients in a new thread 
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(("0.0.0.0", port)) # binding the server socket to the port 
            self.server_socket.listen(5)
            self.running = True
            
            self.log(f"Server started on {self.server_socket.getsockname()}")
            threading.Thread(target=self.accept_clients, daemon=True).start()
            
        except Exception as e:
            self.log(f"Failed to start server: {str(e)}")
            if self.server_socket:
                self.server_socket.close()
                self.server_socket = None
        # starting the threads to show the online users and files on the server 
        threading.Thread(target=self.show_online_users, daemon=True).start()
        threading.Thread(target=self.show_files, daemon=True).start()
        self.load_metadata()


    def accept_clients(self):
        while self.running:
            try:
                # at first, servers accepts the client connection then starts a new thread to handle the client and check for the validity of username
                client_socket, client_address = self.server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket,),
                    daemon=True
                )
                client_thread.start()
                ##self.client_threads.append(client_thread)
            except:
                if self.running:
                    self.log("Error accepting client connection")

    def handle_client(self, client_socket):
        try:
            client_name = client_socket.recv(1024).decode()
            same_name = False
            # self.client is a dictionary that stores the client name and the client socket (current connections)
            if client_name in self.clients:
                client_socket.send("ERROR: Username already in use".encode())
                client_socket.close()
                same_name = True
                return
            self.client_threads.append(threading.current_thread()) # appending the current thread to the client threads list
            self.clients[client_name] = client_socket # adding the client name and the client socket to the clients dictionary
            client_socket.send("Connected successfully".encode())
            self.log(f"Client {client_name} connected")
            
            # handling the client commands
            while True:
                command = client_socket.recv(1024).decode()
                if not command:
                    break
                
                # handling the upload 
                if command.startswith("UPLOAD"):
                    self.handle_upload(client_name, command, client_socket)
                elif command.startswith("DOWNLOAD"):
                    self.handle_download(command, client_socket,client_name)
                elif command.startswith("DELETE"):
                    self.handle_delete(client_name, command, client_socket)
                elif command == "LIST_FILES":
                    self.send_file_list(client_socket,client_name)
                elif command == "DISCONNECT":
                    break
                    
        except Exception as e:
            self.log(f"Error handling client {client_name if 'client_name' in locals() else 'unknown'}: {str(e)}")
        finally:
            if same_name:
                same_name = False
                self.log(f"Another user tried to connect using username {client_name}. Connection rejected")
             # if client_name is in locals(), it means the client has connected
             # and we should remove them from the clients dictionary and close the socket because user clicked the disconnect button in this case
            else:
             if 'client_name' in locals() and client_name in self.clients:
                del self.clients[client_name]
                self.log(f"Client {client_name} disconnected")
             try:
                client_socket.close()
             except:
                pass

    def handle_upload(self, client_name, command, client_socket):
        # from the client, we receive the command in the format of "UPLOAD filename"
        file_exist = False
        if not self.file_directory:
            client_socket.send("ERROR: Server file directory not set".encode())
            return

        _, filename = command.split()
        unique_filename = f"{client_name}_{filename}"
        file_path = os.path.join(self.file_directory, unique_filename)

        # Send READY to client to confirm upload initiation
        if unique_filename in self.file_metadata.keys():
         client_socket.send("READY2".encode())
         file_exist = True
        else:
            client_socket.send("READY".encode())

        # Open the file in binary write mode and receive it in chunks
        try:
            with open(file_path, 'wb') as file:
                while True:
                    data = client_socket.recv(1024 * 1024)  # Receive in chunks
                    

                    # Check if this is the EOF control message (binary EOF)
                    # it might questioned as why we are checking for b"EOF" in data instead of data == b"EOF"
                    #if data == b"EOF":
                        #break

                    # Check if this is the EOF control message
                    if data.endswith(b"EOF"):
                        # Write all data except the EOF marker
                        file.write(data[:-3])
                        break

                    # Otherwise, write the chunk to the file
                    file.write(data)

            # Update metadata and send confirmation
            self.file_metadata[unique_filename] = client_name
            self.save_metadata()
            client_socket.send("UPLOAD_SUCCESS".encode())

            if file_exist:
                self.log(f"File '{filename}' uploaded by {client_name}. Overwriting the existing one")
            else:
             self.log(f"File '{filename}' uploaded by {client_name}")

        except Exception as e:
            self.log(f"Upload failed: {str(e)}")
            client_socket.send("ERROR: Upload failed.".encode())

    def handle_download(self, command, client_socket,client_name):
        # from the client, we receive the command in the format of "DOWNLOAD uploader filename"
        _, uploader, filename = command.split()
        unique_filename = f"{uploader}_{filename}"
        file_path = os.path.join(self.file_directory, unique_filename)

        # Check if the file exists and is accessible
        if unique_filename not in self.file_metadata:
            client_socket.send("ERROR: File not found".encode())
            self.log(f"ERROR: {client_name} request downloading {filename} from {uploader}. File not found")
            return

        # checking if the file exists in the directory
        if not os.path.exists(file_path):
            client_socket.send("ERROR: File not found on disk".encode())
            self.log(f"ERROR: {client_name} request downloading {filename} from {uploader}. File not found")
            return

        try:
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Confirm to the client that the server is ready to send the file
            client_socket.send("READY".encode())

            # Small delay to ensure READY message is received separately
            import time
            time.sleep(0.1)

            # Open the file in binary read mode and send it in chunks
            with open(file_path, 'rb') as file:
                bytes_sent = 0
                while bytes_sent < file_size:
                    chunk = file.read(1024 * 1024)  # Read 1MB at a time
                    if not chunk:
                        break
                    client_socket.sendall(chunk)
                    bytes_sent += len(chunk)

            # Small delay before sending EOF
            time.sleep(0.1)
            
            # Send EOF marker
            client_socket.sendall(b"EOF")
            self.log(f"File {filename} by {uploader} has been downloaded by {client_name} (Size: {file_size} bytes)")
            if uploader in self.clients.keys() and uploader != client_name:
                self.clients[uploader].send(f"File {filename} you have uploaded has been downloaded by {client_name}".encode())
        except Exception as e:
            self.log(f"Download failed: {str(e)}")
            client_socket.send("ERROR: Download failed.".encode())
    

    def handle_delete(self, client_name, command, client_socket):
        # from the client, we receive the command in the format of "DELETE filename"
        try:
            _, filename = command.split()
            unique_filename = f"{client_name}_{filename}"
            
            # checking if the file exists in the directory
            if unique_filename in self.file_metadata and self.file_metadata[unique_filename] == client_name:
                file_path = os.path.join(self.file_directory, unique_filename)
                
                # deleting the file from the directory and updating the metadata
                if os.path.exists(file_path):
                    os.remove(file_path)
                    del self.file_metadata[unique_filename]
                    self.save_metadata()
                    
                    client_socket.send("File deleted successfully.".encode())
                    self.log(f"File '{filename}' deleted by {client_name}")
                else:
                    client_socket.send("ERROR: File not found on server.".encode())
                    self.log("ERROR: File not found on server.")
            else:
                client_socket.send("ERROR: File not found or insufficient permissions.".encode())
                self.log(f"{client_name} tried to delete {filename}. Rejecting invalid request.")
    
        except Exception as e:
            self.log(f"Delete operation failed: {str(e)}")
            client_socket.send("ERROR: Delete operation failed.".encode())

    # sending the file list to the client
    def send_file_list(self, client_socket,client_name):
        try:
            # checking if there are files on the server
            if not self.file_metadata:
                client_socket.send("No files available.".encode())
                self.log(f"{client_name} requested file list. No files on the server")
            else:
                # sending the file list to the client
                self.log(f"{client_name} requested file list. Sending the file list")
                size = len(self.file_metadata)
                file_list = ""
                # we are using [^] as a separator between the files to split them later
                for i in range(size):
                    if i != size - 1:
                        file_list += f"{list(self.file_metadata.keys())[i].split('_', 1)[1]} by {list(self.file_metadata.values())[i]} [^] "
                    else:
                        file_list += f"{list(self.file_metadata.keys())[i].split('_', 1)[1]} by {list(self.file_metadata.values())[i]}"
                # sending the file list to the client
                client_socket.send(file_list.encode('utf-8'))
        except Exception as e:
            self.log(f"Failed to send file list: {str(e)}")
            client_socket.send("ERROR: Failed to retrieve file list.".encode())

    # logging the messages to the log box
    def log(self, message):
        self.log_box.insert(tk.END, message)
        self.log_box.yview(tk.END)
    
    # logging the messages to the online user box
    def log_to_user_box(self, message):
        self.online_user_box.insert(tk.END, message)
        self.online_user_box.yview(tk.END)
    
    # logging the messages to the files box
    def log_to_file_box(self, message):
        self.files_box.insert(tk.END, message)
        self.files_box.yview(tk.END)

    # closing the server
    def close_server(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None

        for client_socket in self.clients.values():
            try:
                client_socket.send("Server shutting down".encode())
                client_socket.close()
            except:
                pass
        
        self.save_metadata()
        
        self.log("Server closed.")
        self.root.destroy()

if __name__ == "__main__":
    FileServer().setup_gui()
